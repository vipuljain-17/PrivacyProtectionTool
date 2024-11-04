## Project
Create a customizable privacy detection and protection system using Microsoft Presidio
- Github Repo: https://github.com/microsoft/presidio 

### Task 1 - Basic Configuration and Detection
Define configuration parameters to control which types of personal information to detect:
- Create a configuration file (JSON) to enable/disable different recognizers
- Implement basic text scanning functionality


Example of configuration
```
{
  "recognizers": {
    "EmailRecognizer": true,
    "PhoneRecognizer": true,
    "CreditCardRecognizer": false,
    "NameRecognizer": true
  }
}
```
Invocation
```
python privacy_tool.py -scan "input text"  -config config.json
```

### Task 2 Anonymization Implementation
Expand Task 1 to include anonymization options:
- Add ability to specify anonymization method per recognizer
- Implement different anonymization types (replace, mask, redact)


Invocation
```
python privacy_tool.py -anonymize "input text" -method replace
```

### Task 3 API Conversion

- Convert the command-line tool to a REST API service: Flask or FastAPI
- Create endpoints for scanning and anonymization
- Accept JSON payloads for configuration
- Return structured results
- Example API endpoints:
- GET /scan - Scan text for PII
- POST /anonymize - Anonymize detected PII

#### Sample Input/Output

*Input Text*

`"Hi, I'm John Smith and my email is john@email.com"`

*Detection Output*
```
{
  "entities": [
    {
      "type": "PERSON",
      "text": "John Smith",
      "position": [7, 16]
    },
    {
      "type": "EMAIL",
      "text": "john@email.com",
      "position": [30, 43]
    }
  ]
}
```
*Anonymized Output*

`"Hi, I'm <PERSON> and my email is <EMAIL>"`