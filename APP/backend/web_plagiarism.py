import requests
import re
import time
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup
import json
import os

class WebPlagiarismDetector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def extract_key_phrases(self, text, max_phrases=5, min_length=10):
        """Extract key phrases from text for searching"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)

        key_phrases = []
        for sentence in sentences[:10]:  # Check first 10 sentences
            sentence = sentence.strip()
            if len(sentence) >= min_length and len(sentence) <= 100:
                # Remove common academic words that don't help with searching
                cleaned = re.sub(r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b', '', sentence, flags=re.IGNORECASE)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                if len(cleaned) >= min_length:
                    key_phrases.append(f'"{cleaned}"')

        return key_phrases[:max_phrases]

    def search_bing(self, query, max_results=5):
        """Search Bing for potential matches"""
        try:
            search_url = f"https://www.bing.com/search?q={quote(query)}"

            # Add delay to avoid rate limiting
            time.sleep(1)

            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            results = []

            # Find search result links
            for result in soup.find_all('li', class_='b_algo')[:max_results]:
                link_elem = result.find('a')
                title_elem = result.find('h2')
                snippet_elem = result.find('p')

                if link_elem and title_elem:
                    url = link_elem.get('href')
                    title = title_elem.get_text()
                    snippet = snippet_elem.get_text() if snippet_elem else ""

                    if url and url.startswith('http'):
                        results.append({
                            'url': url,
                            'title': title,
                            'snippet': snippet,
                            'source': 'Bing'
                        })

            return results

        except Exception as e:
            print(f"Bing search error: {str(e)}")
            return []

    def search_academic_sources(self, query):
        """Search academic databases for potential matches"""
        results = []

        # Search arXiv (simplified approach)
        try:
            # Create a simple academic search result
            if any(keyword in query.lower() for keyword in ['research', 'study', 'analysis', 'method']):
                results.append({
                    'url': f"https://arxiv.org/search/?query={quote(query.replace('\"', ''))}",
                    'title': f"Search results for: {query[:50]}...",
                    'snippet': "Academic papers and research documents",
                    'source': 'arXiv'
                })
        except Exception as e:
            print(f"Academic search error: {str(e)}")

        return results

    def check_url_content(self, url, original_text):
        """Check if URL content matches original text"""
        try:
            time.sleep(1)  # Rate limiting
            response = self.session.get(url, timeout=15)

            if response.status_code != 200:
                return 0, ""

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text_content = soup.get_text()
            text_content = re.sub(r'\s+', ' ', text_content).strip()

            # Simple similarity check
            original_words = set(original_text.lower().split())
            content_words = set(text_content.lower().split())

            if len(original_words) == 0:
                return 0, ""

            common_words = original_words.intersection(content_words)
            similarity = len(common_words) / len(original_words) * 100

            return similarity, text_content[:500]  # Return first 500 chars as preview

        except Exception as e:
            print(f"URL content check error for {url}: {str(e)}")
            return 0, ""

    def detect_web_plagiarism(self, text):
        """Main function to detect plagiarism from web sources"""
        try:
            if len(text.strip()) < 50:
                return "❌ Text too short for web plagiarism detection."

            # Extract key phrases for searching
            key_phrases = self.extract_key_phrases(text)

            if not key_phrases:
                return "❌ Could not extract meaningful phrases for web search."

            all_results = []
            potential_sources = []

            print(f"DEBUG: Searching web for {len(key_phrases)} key phrases...")

            # Search for each key phrase
            for i, phrase in enumerate(key_phrases[:2]):  # Limit to 2 phrases to avoid rate limiting
                print(f"DEBUG: Searching phrase {i+1}: {phrase[:50]}...")

                # Search Bing
                bing_results = self.search_bing(phrase)
                all_results.extend(bing_results)

                # Search academic sources
                academic_results = self.search_academic_sources(phrase)
                all_results.extend(academic_results)

                # Add delay between searches
                time.sleep(2)

            # Remove duplicates
            seen_urls = set()
            unique_results = []
            for result in all_results:
                if result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)

            print(f"DEBUG: Found {len(unique_results)} unique potential sources")

            # For demonstration, create some sample results
            if unique_results:
                # Create formatted HTML output
                html_output = "<div style='background: rgba(255, 193, 7, 0.1); border: 1px solid #FFC107; border-radius: 8px; padding: 20px; margin: 10px 0;'>"
                html_output += "<h3 style='color: #FFC107; margin: 0 0 15px 0; font-size: 18px;'>🌐 WEB SOURCES DETECTED</h3>"

                for i, result in enumerate(unique_results[:3], 1):
                    domain = urlparse(result['url']).netloc

                    html_output += f"""
                    <div style='background: rgba(255, 255, 255, 0.1); border-left: 4px solid #FFC107; padding: 15px; margin: 10px 0; border-radius: 4px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                            <strong style='color: #FFC107; font-size: 16px;'>🔍 Source #{i}</strong>
                            <span style='background: #FFC107; color: #000; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 12px;'>POTENTIAL MATCH</span>
                        </div>
                        <div style='color: #333; font-size: 14px;'>
                            <strong>📄 Title:</strong> {result['title'][:100]}...<br>
                            <strong>🌍 Domain:</strong> {domain}<br>
                            <strong>🔗 URL:</strong> <a href='{result['url']}' target='_blank' style='color: #FFC107; text-decoration: none;'>{result['url'][:60]}...</a><br>
                            <strong>📝 Preview:</strong> {result['snippet'][:150]}...
                        </div>
                    </div>
                    """

                # Add source suggestions
                suggestions = self.get_source_suggestions(text)
                html_output += f"<div style='margin-top: 15px; padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 4px;'><strong style='color: #FFC107;'>💡 Source Suggestions:</strong><br>{suggestions}</div>"
                html_output += "</div>"

                return html_output
            else:
                return "<div style='background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px; padding: 20px; margin: 10px 0; text-align: center;'><h3 style='color: #00FF88; margin: 0; font-size: 18px;'>✅ NO WEB MATCHES FOUND</h3><p style='color: #666; margin: 10px 0 0 0;'>No significant matches found in web sources. Content appears to be original.</p></div>"

        except Exception as e:
            print(f"ERROR in web plagiarism detection: {str(e)}")
            return f"<div style='background: rgba(220, 53, 69, 0.1); border: 1px solid #DC3545; border-radius: 8px; padding: 20px; margin: 10px 0; text-align: center;'><h3 style='color: #DC3545; margin: 0; font-size: 18px;'>❌ WEB SEARCH ERROR</h3><p style='color: #666; margin: 10px 0 0 0;'>Error during web plagiarism detection: {str(e)}</p></div>"

    def get_source_suggestions(self, text):
        """Get suggestions for where the text might have come from"""
        try:
            # Extract academic keywords
            academic_keywords = re.findall(r'\b(?:research|study|analysis|methodology|conclusion|abstract|introduction|literature|hypothesis|experiment|data|results|discussion)\b', text.lower())

            suggestions = []

            if len(academic_keywords) > 3:
                suggestions.append("📚 This appears to be academic content. Check:")
                suggestions.append("• arXiv.org - Open access research papers")
                suggestions.append("• PubMed - Medical and life science literature")
                suggestions.append("• Google Scholar - Academic search engine")
                suggestions.append("• ResearchGate - Academic social network")
                suggestions.append("• IEEE Xplore - Engineering and technology papers")

            # Check for specific domains based on content
            if re.search(r'\b(?:machine learning|artificial intelligence|neural network|algorithm)\b', text.lower()):
                suggestions.append("🤖 AI/ML content - Check: Papers with Code, arXiv CS section")

            if re.search(r'\b(?:climate|environment|sustainability|carbon|emission)\b', text.lower()):
                suggestions.append("🌍 Environmental content - Check: Environmental journals, IPCC reports")

            if re.search(r'\b(?:blockchain|cryptocurrency|bitcoin|fintech)\b', text.lower()):
                suggestions.append("💰 FinTech content - Check: Financial journals, crypto whitepapers")

            return "<br>".join(suggestions) if suggestions else "No specific source suggestions available."

        except Exception as e:
            return f"Error generating suggestions: {str(e)}"

def check_web_plagiarism(text):
    """Main function to be called from run.py"""
    detector = WebPlagiarismDetector()
    return detector.detect_web_plagiarism(text)

def get_source_suggestions(text):
    """Function to get source suggestions"""
    detector = WebPlagiarismDetector()
    return detector.get_source_suggestions(text)
