from presidio_analyzer import AnalyzerEngine
from config_schema import PIIRegistry


class PrivacyScanner:
    """Main scanner class for privacy detection"""

    def __init__(self, config):
        self.analyzer = AnalyzerEngine(registry=PIIRegistry(config).get_registry())

    def scan_text(self, text: str) -> list:
        """Scan text for privacy information"""

        results = self.analyzer.analyze(text=text, language="en", entities=None)
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
