from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from config_schema import PIIRegistry

# TODO: Convert to data class
ANONYMIZATIONMETHOD = [
    "replace",
    "redact",
    "hash",
    "mask",
    "encrypt",
    "keep",
    "decrypt",
]


class PrivacyScanner:
    """Main scanner class for privacy detection"""

    def __init__(self, config):
        self.analyzer = AnalyzerEngine(registry=PIIRegistry(config).get_registry())
        self.anonymizer_engine = AnonymizerEngine()
        # TODO: Implement eccryption key handler
        # self.encryption_key = "saiuddubdub"

    def __analyze_text(self, text: str) -> list:
        """Analyze text for privacy information"""

        results = self.analyzer.analyze(text=text, language="en", entities=None)

        return results

    def scan_text(self, text: str) -> list:
        """Scan text for privacy information"""

        results = self.__analyze_text(text)

        return [
            {
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "text": text[result.start : result.end],
            }
            for result in results
        ]

    def _get_operator_config(self, method):
        """Get operator config for anonymization method"""
        if method in ("replace", "redact", "keep"):
            return OperatorConfig(method)
        elif method == "mask":
            return OperatorConfig(
                method, {"chars_to_mask": 100, "masking_char": "*", "from_end": True}
            )
        elif method == "hash":
            return OperatorConfig(method, {"hash_type": "sha256"})
        # TODO: Once the key handler is enabled, uncomment below line
        # elif method in ("encrypt", "decrypt"):
        #     return OperatorConfig(method, {"key": self.encryption_key})
        else:
            raise ValueError(f"Unsupported anonymization method: {method}")

    def anonymize_text(self, text: str, method: str) -> str:
        """Anonymize text"""
        try:
            if method not in ANONYMIZATIONMETHOD:
                raise ValueError(
                    f"Invalid method: {method}. Must be one of {ANONYMIZATIONMETHOD}"
                )

            analyzer_results = self.__analyze_text(text)

            if not analyzer_results:
                return text

            operator_config = self._get_operator_config(method)
            # print(operator_config)

            anonymizer_operator_config = {
                entity_type: operator_config
                for entity_type in set(
                    result.entity_type for result in analyzer_results
                )
            }
            # print(anonymizer_operator_config)

            return self.anonymizer_engine.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                operators=anonymizer_operator_config,
            ).text

        except Exception as e:
            raise RuntimeError(f"Failed to anonymize text: {str(e)}")
