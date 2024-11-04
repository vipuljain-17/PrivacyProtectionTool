import argparse
import json

from scanner import PrivacyScanner, ANONYMIZATIONMETHOD


def main():
    parser = argparse.ArgumentParser(description="Privacy Detection Tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-scan", type=str, help="Text to scan")
    group.add_argument("-anonymize", type=str, help="Text to anonymize")
    parser.add_argument("-config", type=str, help="Path to config file")
    parser.add_argument(
        "-method",
        type=str,
        choices=ANONYMIZATIONMETHOD,
        default="replace",
        help="Anonymization method (for -anonymize only)",
    )

    args = parser.parse_args()

    try:
        scanner = PrivacyScanner(args.config)

        if args.scan:
            results = scanner.scan_text(args.scan)
            print(json.dumps(results, indent=2))
        else:
            anonymized_text = scanner.anonymize_text(args.anonymize, args.method)
            print(anonymized_text)

        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit(main())
