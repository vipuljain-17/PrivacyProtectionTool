import json
from pathlib import Path
from presidio_analyzer import RecognizerRegistry
from presidio_analyzer.predefined_recognizers import (
    EmailRecognizer,
    PhoneRecognizer,
    CreditCardRecognizer,
    SpacyRecognizer,
)

RECOGINZERS = {
    "EmailRecognizer": EmailRecognizer,
    "PhoneRecognizer": PhoneRecognizer,
    "CreditCardRecognizer": CreditCardRecognizer,
    "NameRecognizer": SpacyRecognizer,
}


class ConfigLoader:
    DEFAULT_RECOGNIZERS = {
        "EmailRecognizer": True,
        "PhoneRecognizer": True,
        "CreditCardRecognizer": True,
        "NameRecognizer": True,
    }

    def __init__(self, config_path=None):
        self.config = self.__load_config(config_path)

    def __load_config(self, config_path):
        if not config_path:
            print("No config path provided. Using default recognizers.")
            return {"recognizers": self.DEFAULT_RECOGNIZERS}

        try:
            config_path = Path(config_path)
            
            with open(config_path, "r") as f:
                config = json.load(f)
                self._validate_config(config)
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            print("Configuration file not found or invalid. Using default recognizers.")

        return {"recognizers": self.DEFAULT_RECOGNIZERS}

    def _validate_config(self, config: dict):
        if "recognizers" not in config:
            raise KeyError("Configuration must contain 'recognizers' section")

        for recognizer in config["recognizers"]:
            if recognizer not in RECOGINZERS:
                raise ValueError(f"Unknown recognizer: {recognizer}")

    def get_recognizers_config(self):
        return self.config.get("recognizers")
    
class PIIRegistry:
    @staticmethod
    def create_custom_registory(config):
        registry = RecognizerRegistry()
        registry_config = ConfigLoader(config).get_recognizers_config()

        for recognizer_name, enabled in registry_config.items():
            if enabled:
                try:
                    registry.add_recognizer(RECOGINZERS[recognizer_name]())
                except KeyError:
                    print(f"Error while fetching the registry for the recognizer: {recognizer_name}")
                    # print(f"Proceding ahead without it")
                    continue
        return registry

    def __init__(self, config):
        self.registry = self.create_custom_registory(config)

    def get_registry(self):
        return self.registry