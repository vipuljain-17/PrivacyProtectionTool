from typing import Dict, Optional
import json
from pathlib import Path
import importlib
from presidio_analyzer import RecognizerRegistry
from presidio_analyzer.predefined_recognizers import (
    __all__ as DEFAULT_PREDEFINED_RECOGNIZERS,
    SpacyRecognizer,
)


class ConfigLoader:
    """
    Loads configuration from a json file or defaults to a configuration with the predefined recognizers.
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config: Dict[str, Dict[str, bool]] = self.__load_config(config_path)

    def __load_config(self, config_path: Optional[Path]) -> Dict[str, Dict[str, bool]]:
        if not config_path:
            print("No config path provided. Using default recognizers.")
            return {}

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                self._validate_config(config)
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            print("Configuration file not found or invalid. Using default recognizers.")

        return {}

    def _validate_config(self, config: Dict[str, Dict[str, bool]]) -> None:
        if "recognizers" not in config:
            raise KeyError("Configuration must contain 'recognizers' section")

        for recognizer_name in config["recognizers"]:
            if (
                recognizer_name not in DEFAULT_PREDEFINED_RECOGNIZERS
                and recognizer_name != "NameRecognizer"
                and not config["recognizers"].get(recognizer_name)
            ):
                raise ValueError(f"Unknown recognizer: {recognizer_name}")

    def get_recognizers_config(self) -> Dict[str, bool]:
        return self.config.get("recognizers")


class PIIRegistry:
    """
    Loads recognizers based on the configuration provided.

    Args:
        config (str): Path to the configuration file.
    """

    def __init__(self, config: str):
        registry_config: Dict[str, bool] = ConfigLoader(config).get_recognizers_config()
        if registry_config:
            self.registry: RecognizerRegistry = self._create_custom_registry(
                registry_config
            )
        else:
            self.registry: RecognizerRegistry = self._load_default_predefined_registry()

    def get_registry(self) -> RecognizerRegistry:
        return self.registry

    def _load_default_predefined_registry(self):
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()
        # registry.add_recognizer(SpacyRecognizer())
        return registry

    def _create_custom_registry(
        self, registry_config: Dict[str, bool]
    ) -> RecognizerRegistry:
        registry = RecognizerRegistry()

        for recognizer_name, enabled in registry_config.items():
            if enabled:
                try:
                    if recognizer_name == "NameRecognizer":
                        registry.add_recognizer(
                            self._import_recognizer("SpacyRecognizer")
                        )
                        continue

                    elif isinstance(enabled, dict) and enabled["enabled"]:
                        enabled.pop("enabled")
                        registry.add_pattern_recognizer_from_dict(enabled)
                    else:
                        registry.add_recognizer(
                            self._import_recognizer(recognizer_name)
                        )
                except Exception:
                    print(
                        f"Error while fetching the registry for the recognizer: {recognizer_name}"
                    )
                    raise

        return registry

    def _import_recognizer(self, recognizer_name: str) -> object:
        try:
            module = importlib.import_module("presidio_analyzer.predefined_recognizers")

            recognizer_class = getattr(module, recognizer_name)

            return recognizer_class()

        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not import recognizer {recognizer_name}: {str(e)}")
            return None
