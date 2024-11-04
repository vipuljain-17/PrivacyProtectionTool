import pytest
from pathlib import Path
import json
from presidio_analyzer import RecognizerRegistry
from presidio_analyzer.predefined_recognizers import EmailRecognizer, PhoneRecognizer, CreditCardRecognizer
from task3.config_schema import ConfigLoader, PIIRegistry

def test_config_loader_default():
    config_loader = ConfigLoader()
    config = config_loader.get_recognizers_config()
    assert config == {
        "EmailRecognizer": True,
        "PhoneRecognizer": True,
        "CreditCardRecognizer": True,
        "NameRecognizer": True,
    }

def test_config_loader_custom_config_file(tmp_path):
    config_data = {
        "recognizers": {
            "EmailRecognizer": False,
            "PhoneRecognizer": True,
        }
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))

    config_loader = ConfigLoader(config_file)
    config = config_loader.get_recognizers_config()
    assert config == config_data["recognizers"]

def test_pii_registry_default():
    pii_registry = PIIRegistry(None)
    registry = pii_registry.get_registry()
    assert isinstance(registry, RecognizerRegistry)
    assert any(isinstance(recognizer, EmailRecognizer) for recognizer in registry.recognizers)
    assert any(isinstance(recognizer, PhoneRecognizer) for recognizer in registry.recognizers)

def test_pii_registry_custom_config(tmp_path):
    config_data = {
        "recognizers": {
            "EmailRecognizer": True,
            "PhoneRecognizer": False,
            "CreditCardRecognizer": True,
        }
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))

    pii_registry = PIIRegistry(config_file)
    registry = pii_registry.get_registry()
    
    assert any(isinstance(recognizer, EmailRecognizer) for recognizer in registry.recognizers)
    assert not any(isinstance(recognizer, PhoneRecognizer) for recognizer in registry.recognizers)
    assert any(isinstance(recognizer, CreditCardRecognizer) for recognizer in registry.recognizers)

