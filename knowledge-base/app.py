from flask import Flask, request, jsonify
import os
import json
import logging
from fuzzywuzzy import fuzz

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load documents from the data directory
def load_documents():
    documents = {}
    data_dir = 'data'
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        logger.warning(f"Data directory {data_dir} not found")
        return documents
        
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(data_dir, filename), 'r') as f:
                    documents[filename] = json.load(f)
                    logger.info(f"Loaded document: {filename}")
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
    
    logger.info(f"Loaded {len(documents)} documents total")
    return documents

# Global documents variable
documents = load_documents()

@app.route('/search', methods=['POST'])
def search():
    """Search for relevant document content"""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    logger.info(f"Search query: {query}")
    
    results = []
    for doc_id, content in documents.items():
        # Simple text matching 
        score = fuzz.token_set_ratio(query.lower(), content.get('text', '').lower())
        if score > 60:  # Relevance threshold
            # Use 'content' as the key instead of 'text' to match what Claude integration expects
            results.append({
                'title': content.get('title', 'Untitled'),
                'content': content.get('text', '')[:500] + '...',
                'score': score
            })
    
    # Sort by relevance score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    top_results = results[:3]  # Return top 3 matches
    logger.info(f"Found {len(top_results)} relevant results")
    
    return jsonify({
        'results': top_results,
        'has_knowledge': len(top_results) > 0,  # Flag indicating if knowledge was found
        'highest_score': top_results[0]['score'] if top_results else 0
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok', 'document_count': len(documents)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)