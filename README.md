# OpenSearch Data Generator

A web-based tool to generate sample data for OpenSearch based on your mapping schema. This tool helps you quickly create test data that matches your index structure.

## Features

- Interactive web interface to define your mapping schema
- Supports multiple field types:
  - Basic Types:
    - String (text data)
    - Number (integer numbers)
    - Float (decimal numbers)
    - Boolean (true/false)
    - Date (ISO format dates)
    - Email (email addresses)
  - Special Types:
    - IP (IPv4 and IPv6 addresses)
    - Geo Point (latitude/longitude pairs)
  - Complex Types:
    - Array (lists of any basic type)
    - Object (nested objects with custom fields)
- Generates realistic fake data using the Faker library
- Direct connection to OpenSearch for data indexing
- Configurable number of records to generate

## Installation

1. Clone the repository:
```bash
git clone https://github.com/madhankb/opensearch-data-generator.git
cd opensearch-data-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure OpenSearch connection:
Set the following environment variables:
- `OPENSEARCH_HOST`: Your OpenSearch host
- `OPENSEARCH_PORT`: Your OpenSearch port
- `OPENSEARCH_USER`: Your OpenSearch username
- `OPENSEARCH_PASSWORD`: Your OpenSearch password

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5004`

3. Create your mapping schema:
   - Add fields using the "Add Field" button
   - For each field, specify:
     - Field name
     - Field type (string, number, float, etc.)
     - For array fields, select the type of items in the array
     - For object fields, add nested fields as needed

4. Enter:
   - Index name where the data should be stored
   - Number of records to generate

5. Click "Generate Data" to create and index the sample data

## Example Mappings

### Basic Document
```json
{
    "title": "Sample Article",
    "views": 12345,
    "rating": 4.5,
    "published": true,
    "created_at": "2024-02-11T12:34:56",
    "author_email": "author@example.com"
}
```

### Document with Special Types
```json
{
    "server": "192.168.1.1",
    "location": {
        "lat": 37.8267,
        "lon": -122.4233
    }
}
```

### Document with Arrays and Objects
```json
{
    "tags": ["technology", "programming", "web"],
    "metadata": {
        "category": "Tutorial",
        "difficulty": "Intermediate",
        "topics": ["OpenSearch", "Data Generation"]
    }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
