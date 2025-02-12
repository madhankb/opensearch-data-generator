from flask import Flask, request, render_template, jsonify
from opensearchpy import OpenSearch, OpenSearchException
from faker import Faker
import json
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import logging
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

fake = Faker()

# OpenSearch configuration
OPENSEARCH_HOST = os.getenv('OPENSEARCH_HOST', 'https://search-uitestdomain-43tel7vooim24uwac5fzgipyxq.ap-south-1.es.amazonaws.com')
OPENSEARCH_PORT = int(os.getenv('OPENSEARCH_PORT', '443'))  # Use standard HTTPS port
OPENSEARCH_USER = os.getenv('OPENSEARCH_USER', 'madhan')
OPENSEARCH_PASSWORD = os.getenv('OPENSEARCH_PASSWORD', 'Madhan@123')

# Parse the host URL to handle HTTPS correctly
parsed_url = urlparse(OPENSEARCH_HOST)
host = parsed_url.netloc if parsed_url.netloc else OPENSEARCH_HOST
scheme = parsed_url.scheme if parsed_url.scheme else 'http'

logger.debug(f"OpenSearch Configuration - Host: {host}, Port: {OPENSEARCH_PORT}, Scheme: {scheme}")

# For AWS OpenSearch domains, we don't need to specify the port
client = OpenSearch(
    hosts=[{'host': host, 'port': OPENSEARCH_PORT}],  
    http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
    use_ssl=True if scheme == 'https' else False,
    verify_certs=False,
    ssl_show_warn=False,
    timeout=30,  
)

# Test the connection
try:
    health = client.cluster.health()
    logger.debug(f"Successfully connected to OpenSearch. Cluster health: {health}")
except Exception as e:
    logger.error(f"Failed to connect to OpenSearch: {str(e)}")

def generate_fake_data(field_type):
    if field_type == 'string':
        return fake.word()
    elif field_type == 'number':
        return fake.random_number()
    elif field_type == 'date':
        return fake.date()
    elif field_type == 'boolean':
        return fake.boolean()
    elif field_type == 'email':
        return fake.email()
    return fake.word()

def generate_data_for_schema(schema, num_records=10):
    data = []
    for _ in range(num_records):
        record = {}
        for field_name, field_info in schema.items():
            if field_info['type'] == 'array':
                array_length = fake.random_int(min=1, max=5)
                record[field_name] = [
                    generate_fake_data(field_info['items_type']) 
                    for _ in range(array_length)
                ]
            elif field_info['type'] == 'object':
                nested_record = {}
                for nested_field, nested_type in field_info['properties'].items():
                    nested_record[nested_field] = generate_fake_data(nested_type)
                record[field_name] = nested_record
            else:
                record[field_name] = generate_fake_data(field_info['type'])
        data.append(record)
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        logger.debug(f"Received request data: {data}")
        
        schema = data['schema']
        index_name = data['index_name']
        num_records = data.get('num_records', 10)
        
        logger.debug(f"Generating {num_records} records for index {index_name}")
        
        # Generate fake data based on the schema
        generated_data = generate_data_for_schema(schema, num_records)
        
        # Create index if it doesn't exist
        if not client.indices.exists(index=index_name):
            client.indices.create(index=index_name)
        
        # Bulk insert the generated data
        bulk_data = []
        for doc in generated_data:
            bulk_data.append({'index': {'_index': index_name}})
            bulk_data.append(doc)
        
        if bulk_data:
            response = client.bulk(body=bulk_data, refresh=True)
            success_count = sum(1 for item in response['items'] if 'index' in item and item['index']['status'] == 201)
            
            return jsonify({
                'status': 'success',
                'message': f'Successfully generated and inserted {success_count} records',
                'sample_data': generated_data[:2]
            })
    
    except Exception as e:
        logger.error(f"Error in generate endpoint: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5006)
