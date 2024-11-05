# Privacy Protection Tool
_(README.md - Created via ChatGPT)_

A Flask-based REST API for detecting and anonymizing personally identifiable information (PII) in text using Microsoft's Presidio framework.

Refer to TaskList.md to understand the context behind this

### Table of Contents

- Features
- Prerequisites
- Installation
- Configuration
- API Endpoints
- Usage Examples
- Error Handling
- Testing

## Features

- Text scanning for PII detection
- Multiple anonymization methods (replace, redact, hash, mask, keep)
- Configurable recognizers for different types of PII
- Comprehensive error handling
- REST API interface

## Prerequisites

- Python 3.11.9
- pip (Python package manager)
- Virtual environment (recommended)

## Installation
1. Clone the repository:

```
git clone <repository-url>
cd privacy-tool/task3
```
2. Create and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:

```pip install -r requirements.txt```

## Configuration
The application uses a configuration system for PII recognizers. You can either use the default configuration or provide a custom one.

#### Default Configuration
The default configuration enables the following recognizers:

- Email Recognition
- Phone Number Recognition
- Credit Card Number Recognition
- Name Recognition (via Spacy)

#### Custom Configuration

Create a JSON configuration file (e.g., config.json):
```
{
    "recognizers": {
        "EmailRecognizer": true,
        "PhoneRecognizer": true,
        "CreditCardRecognizer": true,
        "NameRecognizer": true
        // Add other pre-defined recognizers as needed
    }
}
```

### API Endpoints

#### Home Endpoint
1. **URL**: /
2. **METHOD**: GET
3. **RESPONSE**: 
```
{
    "message": "Welcome to Privacy Tool",
    "version": "1.0"
}
```

#### Scan Text Endpoint
1. **URL**: /scan
2. **METHOD**: POST
3. **BODY**: 
```
{
    "scan": "Text to be scanned",
    "config": "Local Path of the config"
}
```
4. **RESPONSE**: 
```
{
    "message": "Success",
    "entities": [
        {
            "type": "EMAIL_ADDRESS",
            "position": [10, 30],
            "text": "example@email.com"
        }
    ]
}
```

#### Anonymize Text Endpoint
1. **URL**: /anonymize
2. **METHOD**: POST
3. **BODY**: 
```
{
    "anonymize": "Text to be anonymized",
    "method": "replace",
    "config": "Local Path of the config"
}
```
4. **RESPONSE**: 
```
{
    "message": "Success",
    "entities": [
        {
            "type": "EMAIL_ADDRESS",
            "position": [10, 30],
            "text": "example@email.com"
        }
    ],
    "anonymized_output": "Text with <EMAIL_ADDRESS>"
}
```

### Usage Examples

#### Scanning Text
```
import requests

url = "http://localhost:5000/scan"
payload = {
    "scan": "My email is john@example.com and phone is 123-456-7890"
    # "config": <path to the config> # Optional
}

response = requests.post(url, json=payload)
print(response.json())
```

#### Anonymizing Text
```
import requests

url = "http://localhost:5000/anonymize"
payload = {
    "anonymize": "My email is john@example.com and phone is 123-456-7890",
    "method": "mask"
    # "config": <path to the config> # Optional
}

response = requests.post(url, json=payload)
print(response.json())
```

### Error Handling
The API uses standard HTTP status codes and provides detailed error messages:
- `200`: Success
- `400`: Bad Request (invalid input, missing fields)
- `500`: Internal Server Error

Error responses follow this format:
```
{
    "message": "Error description"
}
```

### Testing
Run tests using pytest:
`pytest tests/`

Create new tests in the tests/ directory following the existing pattern.