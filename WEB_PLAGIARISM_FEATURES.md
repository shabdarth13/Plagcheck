# Web Plagiarism Detection Features

## Overview

Your plagiarism detection system has been enhanced with comprehensive web-based plagiarism detection capabilities. The system can now:

1. **Search web sources** for potential matches
2. **Identify original source websites** of research papers
3. **Provide source suggestions** based on content analysis
4. **Combine local and web results** for comprehensive detection

## New Features

### 1. **Web Plagiarism Detection**
- Searches multiple web sources for potential matches
- Uses intelligent phrase extraction for better search results
- Provides similarity scoring and source identification
- Includes academic database searching

### 2. **Source Website Identification**
- Identifies potential original sources of uploaded content
- Provides direct links to source websites
- Shows domain information and content previews
- Suggests likely academic databases based on content type

### 3. **Enhanced Analysis Options**
- **Plagiarism Detector (Local + Web)**: Comprehensive check using both local database and web sources
- **Web Plagiarism Detector Only**: Focuses exclusively on web source detection
- **AI Content Detector**: Unchanged AI-generated content detection

### 4. **Smart Source Suggestions**
- Analyzes content to suggest likely source types
- Recommends specific academic databases based on subject matter
- Provides targeted search suggestions for different disciplines

## How It Works

### Phase 1: Text Analysis
1. **Key Phrase Extraction**: Identifies meaningful phrases from the input text
2. **Content Classification**: Analyzes text to determine subject area and content type
3. **Search Query Optimization**: Creates effective search queries for web searching

### Phase 2: Web Searching
1. **Multi-Engine Search**: Searches multiple search engines (Bing, academic databases)
2. **Academic Database Integration**: Specifically searches academic sources like arXiv
3. **Rate Limiting**: Implements delays to avoid being blocked by search engines
4. **Result Filtering**: Removes duplicates and irrelevant results

### Phase 3: Content Analysis
1. **Similarity Scoring**: Compares original text with found web content
2. **Source Verification**: Attempts to access and analyze potential source websites
3. **Relevance Assessment**: Evaluates the likelihood of each potential match

### Phase 4: Result Presentation
1. **Comprehensive Reporting**: Shows both local and web search results
2. **Source Attribution**: Provides clickable links to potential sources
3. **Confidence Scoring**: Indicates likelihood of each potential match
4. **Actionable Suggestions**: Recommends specific databases to check

## Technical Implementation

### Core Components

#### WebPlagiarismDetector Class
- **extract_key_phrases()**: Intelligently extracts searchable phrases
- **search_bing()**: Searches Bing for potential matches
- **search_academic_sources()**: Searches academic databases
- **check_url_content()**: Analyzes content from potential source URLs
- **detect_web_plagiarism()**: Main detection orchestration
- **get_source_suggestions()**: Provides intelligent source recommendations

#### Integration Points
- **run.py**: Updated to include web plagiarism in both text input and file upload routes
- **Templates**: Enhanced to show new analysis options
- **Rate Limiting**: Maintains 15 documents per day limit across all detection types

### Search Strategy

#### Academic Content Detection
The system identifies academic content by looking for keywords like:
- research, study, analysis, methodology
- conclusion, abstract, introduction
- literature, hypothesis, experiment
- data, results, discussion

#### Subject-Specific Suggestions
- **AI/ML Content**: Suggests Papers with Code, arXiv CS section
- **Environmental Content**: Suggests environmental journals, IPCC reports
- **FinTech Content**: Suggests financial journals, crypto whitepapers
- **Medical Content**: Suggests PubMed, medical databases

## Usage Examples

### Example 1: Academic Paper Analysis
**Input**: Research paper excerpt about machine learning
**Output**:
- Local database results showing any matches in your research collection
- Web search results with potential source websites
- Specific suggestions to check arXiv, Papers with Code, IEEE Xplore
- Direct links to similar papers found online

### Example 2: General Text Analysis
**Input**: General essay or article content
**Output**:
- Comprehensive web search across multiple engines
- Potential source websites with similarity scores
- Domain analysis showing likely source types
- Suggestions for further manual verification

## Benefits

### For Users
1. **Comprehensive Detection**: Combines local and web-based detection
2. **Source Identification**: Helps identify where content originally came from
3. **Time Saving**: Automated web searching saves manual research time
4. **Educational Value**: Teaches users about proper source attribution

### For Administrators
1. **Enhanced Accuracy**: Reduces false negatives by checking web sources
2. **Detailed Reporting**: Provides comprehensive analysis results
3. **Scalable Solution**: Can handle increased usage with rate limiting
4. **Maintainable Code**: Modular design allows easy updates and improvements

## Configuration Options

### Rate Limiting
- **Daily Limit**: 15 documents per day per IP address
- **Search Delays**: 1-2 second delays between web searches
- **Timeout Settings**: 10-15 second timeouts for web requests

### Search Parameters
- **Max Phrases**: Up to 5 key phrases extracted per document
- **Max Results**: Up to 5 results per search engine
- **Similarity Threshold**: 30% minimum similarity for reporting matches

## Installation Requirements

### Python Packages
```bash
pip install -r requirements.txt
```

Required packages:
- Flask==2.3.3
- requests==2.31.0
- beautifulsoup4==4.12.2
- pandas==2.0.3
- scikit-learn==1.3.0
- nltk==3.8.1
- lxml==4.9.3
- urllib3==2.0.4

### System Requirements
- Python 3.7 or higher
- Internet connection for web searching
- Sufficient bandwidth for web requests

## Limitations and Considerations

### Technical Limitations
1. **Rate Limiting**: Search engines may block excessive requests
2. **Content Access**: Some websites may block automated access
3. **Dynamic Content**: JavaScript-heavy sites may not be fully analyzed
4. **Language Support**: Currently optimized for English content

### Ethical Considerations
1. **Respect robots.txt**: The system should respect website access policies
2. **Fair Use**: Only analyzes publicly available content
3. **Privacy**: No personal data is stored from web searches
4. **Academic Integrity**: Tool is designed to promote, not undermine, academic honesty

## Future Enhancements

### Planned Improvements
1. **API Integration**: Direct integration with academic database APIs
2. **Machine Learning**: Improved similarity detection using advanced ML models
3. **Multi-language Support**: Support for non-English content analysis
4. **Real-time Updates**: Continuous monitoring of new web content

### Advanced Features
1. **Citation Analysis**: Automatic citation format detection and verification
2. **Temporal Analysis**: Detection of when content was first published online
3. **Network Analysis**: Mapping of content propagation across websites
4. **Collaborative Filtering**: Learning from user feedback to improve accuracy

## Troubleshooting

### Common Issues
1. **No Results Found**: May indicate original content or search engine blocking
2. **Timeout Errors**: Usually resolved by retrying after a delay
3. **Rate Limiting**: Automatic delays prevent most rate limiting issues
4. **False Positives**: Manual verification recommended for important decisions

### Performance Optimization
1. **Caching**: Results can be cached to avoid repeated searches
2. **Parallel Processing**: Multiple searches can be run concurrently
3. **Smart Filtering**: Improved algorithms to reduce irrelevant results
4. **User Feedback**: Learning system to improve accuracy over time

This enhanced web plagiarism detection system provides a comprehensive solution for identifying potential sources of uploaded content while maintaining ethical standards and technical reliability.
