import os
import re

def normalize(text):
    """Normalize text by removing extra spaces and converting to lowercase"""
    return re.sub(r'\s+', ' ', text).strip().lower()

def rabin_karp_search(pattern, text, prime=101):
    """Optimized Rabin-Karp algorithm for pattern matching"""
    m, n = len(pattern), len(text)
    d = 256
    if m > n: return 0
    p_hash = t_hash = 0
    h = 1
    matches = 0

    # Limit search for very large texts
    if n > 100000:
        # Only search in the first 100K characters
        text = text[:100000]
        n = 100000
        
    for i in range(m - 1):
        h = (h * d) % prime

    for i in range(m):
        p_hash = (d * p_hash + ord(pattern[i])) % prime
        t_hash = (d * t_hash + ord(text[i])) % prime

    for i in range(n - m + 1):
        if p_hash == t_hash and text[i:i + m] == pattern:
            matches += 1
            # Early exit if we find multiple matches
            if matches >= 5:
                return matches
                
        if i < n - m:
            t_hash = (d * (t_hash - ord(text[i]) * h) + ord(text[i + m])) % prime
            t_hash = (t_hash + prime) % prime if t_hash < 0 else t_hash

    return matches

def get_chunks(text, chunk_size=10):
    """Break text into chunks for comparison"""
    words = text.split()
    # Limit number of chunks for performance
    max_chunks = 50
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, min(len(words), max_chunks * chunk_size), chunk_size)]
    return chunks[:max_chunks]

def check_plagiarism(query_text):
    """Check text for plagiarism against reference documents"""
    try:
        # Get the correct path to the research data folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(os.path.dirname(current_dir), 'research data')
        
        # Fallback to hardcoded path if folder doesn't exist
        if not os.path.exists(folder):
            folder = r"C:\Users\pushk\OneDrive\Desktop\PLAG AND AI CONTENT DETECTOR PROJECT\APP\research data"
        
        print(f"DEBUG: Using research data folder: {folder}")
        
        query_text = normalize(query_text)
        
        # For very large texts, only check a sample
        if len(query_text) > 10000:
            query_text = query_text[:10000]
            print("DEBUG: Text truncated to 10K characters for processing")
            
        query_chunks = get_chunks(query_text, chunk_size=10)
        total_chunks = len(query_chunks) if query_chunks else 1  # Avoid division by zero
        
        # Check if folder exists and has files
        if not os.path.exists(folder):
            return "<div style='background: rgba(255, 193, 7, 0.1); border: 1px solid #FFC107; border-radius: 8px; padding: 20px; margin: 10px 0; text-align: center;'><h3 style='color: #FFC107; margin: 0; font-size: 18px;'>⚠️ CONFIGURATION ERROR</h3><p style='color: #666; margin: 10px 0 0 0;'>Research data folder not found. Please check configuration.</p></div>"

        files = [f for f in os.listdir(folder) if f.endswith('.txt')]
        if not files:
            return "<div style='background: rgba(255, 193, 7, 0.1); border: 1px solid #FFC107; border-radius: 8px; padding: 20px; margin: 10px 0; text-align: center;'><h3 style='color: #FFC107; margin: 0; font-size: 18px;'>⚠️ NO REFERENCE DATA</h3><p style='color: #666; margin: 10px 0 0 0;'>No reference documents found for plagiarism checking.</p></div>"
            
        print(f"DEBUG: Found {len(files)} reference documents")
        results = []

        # Limit number of files to check for performance
        max_files = 5
        for file in files[:max_files]:
            try:
                file_path = os.path.join(folder, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = normalize(f.read())
                    # Limit content size for performance
                    if len(content) > 50000:
                        content = content[:50000]
                        
                matched_chunks = sum(1 for chunk in query_chunks if rabin_karp_search(chunk, content) > 0)
                if matched_chunks:
                    percent = (matched_chunks / total_chunks) * 100
                    results.append((file, percent))
                    print(f"DEBUG: Match found in {file}: {percent:.2f}%")
            except Exception as e:
                print(f"ERROR: Failed to process file {file}: {str(e)}")
                continue  # Skip problematic files

        if results:
            # Sort results by percentage (highest first)
            results.sort(key=lambda x: x[1], reverse=True)

            # Create formatted HTML output
            html_output = "<div style='background: rgba(255, 68, 68, 0.1); border: 1px solid #FF4444; border-radius: 8px; padding: 20px; margin: 10px 0;'>"
            html_output += "<h3 style='color: #FF4444; margin: 0 0 15px 0; font-size: 18px;'>🚨 PLAGIARISM DETECTED</h3>"

            for i, (file, percent) in enumerate(results, 1):
                # Determine severity color
                if percent >= 70:
                    color = "#FF4444"  # High similarity - red
                    severity = "HIGH"
                elif percent >= 40:
                    color = "#FFD700"  # Medium similarity - yellow
                    severity = "MEDIUM"
                else:
                    color = "#FFA500"  # Low similarity - orange
                    severity = "LOW"

                html_output += f"""
                <div style='background: rgba(255, 255, 255, 0.1); border-left: 4px solid {color}; padding: 15px; margin: 10px 0; border-radius: 4px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                        <strong style='color: {color}; font-size: 16px;'>Match #{i}</strong>
                        <span style='background: {color}; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 14px;'>{percent:.1f}% - {severity}</span>
                    </div>
                    <div style='color: #333; font-size: 14px;'>
                        <strong>📄 Source File:</strong> {file}<br>
                        <strong>🔍 Similarity:</strong> {percent:.2f}% of your content matches this source
                    </div>
                </div>
                """

            html_output += "</div>"
            return html_output
        return "<div style='background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px; padding: 20px; margin: 10px 0; text-align: center;'><h3 style='color: #00FF88; margin: 0; font-size: 18px;'>✅ NO PLAGIARISM DETECTED</h3><p style='color: #666; margin: 10px 0 0 0;'>Your content appears to be original.</p></div>"
    except Exception as e:
        import traceback
        print(f"ERROR in plagiarism detection: {str(e)}")
        print(traceback.format_exc())
        return f"<div style='background: rgba(220, 53, 69, 0.1); border: 1px solid #DC3545; border-radius: 8px; padding: 20px; margin: 10px 0; text-align: center;'><h3 style='color: #DC3545; margin: 0; font-size: 18px;'>❌ SYSTEM ERROR</h3><p style='color: #666; margin: 10px 0 0 0;'>Error in plagiarism detection: {str(e)}</p></div>"
