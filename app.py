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
def init_opensearch(host, username, password):
    try:
        client = OpenSearch(
            hosts=[{
                'host': host,
                'port': 443,  # Use HTTPS port 443
                'scheme': 'https'  # Explicitly set HTTPS
            }],  
            http_auth=(username, password),
            use_ssl=True,  # Always use SSL for port 443
            verify_certs=False,
            ssl_show_warn=False,
            timeout=30,  
        )
        # Test the connection
        health = client.cluster.health()
        logger.debug(f"Successfully connected to OpenSearch. Cluster health: {health}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to OpenSearch: {str(e)}")
        return None

def generate_fake_data(field_type):
    if field_type == 'string':
        return fake.text()
    elif field_type == 'number':
        return fake.random_number(digits=5)
    elif field_type == 'float':
        return round(fake.random.uniform(-1000.0, 1000.0), 2)
    elif field_type == 'boolean':
        return fake.boolean()
    elif field_type == 'date':
        return fake.date_time_this_decade().isoformat()
    elif field_type == 'email':
        return fake.email()
    elif field_type == 'ip':
        return fake.ipv4() if fake.boolean() else fake.ipv6()
    elif field_type == 'geo_point':
        return {
            'lat': float(fake.latitude()),
            'lon': float(fake.longitude())
        }
    else:
        return str(fake.word())

def generate_data_for_schema(schema, num_records=10):
    data = []
    properties = schema.get('properties', {})
    
    for _ in range(num_records):
        record = {}
        for field_name, field_info in properties.items():
            field_type = field_info.get('type')
            
            if field_type == 'array':
                # Generate array of items
                array_type = field_info.get('items', {}).get('type', 'string')
                array_length = fake.random_int(min=1, max=5)
                record[field_name] = [generate_fake_data(array_type) for _ in range(array_length)]
            elif field_type == 'object':
                # Generate nested object
                nested_properties = field_info.get('properties', {})
                nested_record = {}
                for nested_name, nested_info in nested_properties.items():
                    nested_type = nested_info.get('type', 'string')
                    nested_record[nested_name] = generate_fake_data(nested_type)
                record[field_name] = nested_record
            else:
                record[field_name] = generate_fake_data(field_type)
        
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
        domain = data['domain']
        username = data['username']
        password = data['password']
        
        logger.debug(f"Connecting to OpenSearch domain: {domain}")
        
        # Initialize OpenSearch client with provided credentials
        client = init_opensearch(domain, username, password)
        
        if client is None:
            return jsonify({'status': 'error', 'message': 'Failed to connect to OpenSearch'}), 500
        
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
    app.run(debug=True, port=5001)
