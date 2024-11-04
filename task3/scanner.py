from typing import List, Dict, Tuple
from dataclasses import dataclass
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from config_schema import PIIRegistry


DEFAULT_OPERATOR_CONFIG: Dict = {
    "replace": {"new_value": ""},
    "redact": {},
    "hash": {"hash_type": "sha256"},
    "mask": {"chars_to_mask": 100, "masking_char": "*", "from_end": True},
    "keep": {},
}
LANGUAGE: str = "en"


class PrivacyScannerError(Exception):
    """Custom exception for Privacy Scanner errors"""

    pass


@dataclass
class ScanResult:
    """Structure for scan results"""

    type: str
    position: List[int]
    text: str


class PrivacyScanner:
    """
    Main scanner class for privacy detection

    Attributes:
        analyzer (AnalyzerEngine): An instance of AnalyzerEngine to analyze text for privacy information
        anonymizer_engine (AnonymizerEngine): An instance of AnonymizerEngine to anonymize text
    """

    def __init__(self, config: Dict = None):
        try:
            self.analyzer = AnalyzerEngine(registry=PIIRegistry(config).get_registry())
            self.anonymizer_engine = AnonymizerEngine()
        except Exception as e:
            raise PrivacyScannerError(f"Failed to initialize Privacy Scanner: {str(e)}")

    def _analyze_text(self, text: str) -> List:
        """Analyze text for privacy information"""
        try:
            results = self.analyzer.analyze(text=text, language=LANGUAGE, entities=None)
            return results
        except Exception as e:
            raise PrivacyScannerError(f"Text analysis failed: {str(e)}")

    def scan_text(self, text: str) -> List:
        """
        Scan the provided text for privacy-related information.

        Args:
            text (str): The text to be scanned for privacy entities.

        Returns:
            list: A list of dictionaries, each containing:
                - "type" (str): The type of the detected entity.
                - "position" (list): A list containing the start and end positions of the entity in the text.
                - "text" (str): The substring of the text that corresponds to the detected entity.
        """
        try:
            results = self._analyze_text(text)
            return [
                ScanResult(
                    type=result.entity_type,
                    position=[result.start, result.end],
                    text=text[result.start : result.end],
                ).__dict__
                for result in results
            ]
        except PrivacyScannerError:
            raise
        except Exception as e:
            raise PrivacyScannerError(f"Scan operation failed: {str(e)}")

    def _get_operator_config(self, method: str) -> OperatorConfig:
        try:
            return OperatorConfig(method, DEFAULT_OPERATOR_CONFIG[method])
        except KeyError:
            raise PrivacyScannerError(f"Invalid anonymization method: {method}")
        except Exception as e:
            raise PrivacyScannerError(f"Failed to create operator config: {str(e)}")

    def anonymize_text(self, text: str, method: str) -> Tuple:
        """
        Anonymize the given text using the given method.

        Args:
            text (str): The text to anonymize
            method (str): The method to use for anonymization, one of ["replace", "redact", "hash", "mask", "keep"]

        Returns:
            tuple: A tuple containing the anonymized text and the anonymized entities.
        """
        try:
            analyzer_results = self._analyze_text(text)
            entities = [
                ScanResult(
                    type=result.entity_type,
                    position=[result.start, result.end],
                    text=text[result.start : result.end],
                ).__dict__
                for result in analyzer_results
            ]

            if not analyzer_results:
                return text, entities

            operator_config = self._get_operator_config(method)
            anonymizer_operator_config = {
                entity_type: operator_config
                for entity_type in set(
                    result.entity_type for result in analyzer_results
                )
            }
            # print(anonymizer_operator_config)

            return (
                self.anonymizer_engine.anonymize(
                    text=text,
                    analyzer_results=analyzer_results,
                    operators=anonymizer_operator_config,
                ).text,
                entities,
            )
        except PrivacyScannerError:
            raise
        except Exception as e:
            raise PrivacyScannerError(f"Anonymization failed: {str(e)}")
