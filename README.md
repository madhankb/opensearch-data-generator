# OpenSearch Data Generator

A web application that allows you to generate and ingest sample data into OpenSearch based on a user-defined schema.

## Features

- Dynamic schema definition through web interface
- Support for various field types:
  - String
  - Number
  - Boolean
  - Date
  - Email
  - Array (of any basic type)
  - Nested Objects
- Configurable number of records to generate
- Direct ingestion to OpenSearch
- Sample data preview

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy example.env to .env and configure your OpenSearch connection:
   ```bash
   cp example.env .env
   ```
5. Edit .env with your OpenSearch credentials and connection details

## Running the Application

```bash
python app.py
```

The application will be available at http://localhost:5000

## Usage

1. Access the web interface at http://localhost:5000
2. Define your schema by adding fields:
   - Enter field names
   - Select field types
   - For arrays, specify the type of items in the array
   - For objects, add nested fields
3. Enter the desired index name and number of records
4. Click "Generate & Ingest Data" to create and store the data in OpenSearch

## Requirements

- Python 3.7+
- OpenSearch instance
- Modern web browser
