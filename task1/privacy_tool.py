import argparse
import json

from scanner import PrivacyScanner


def main():
    parser = argparse.ArgumentParser(description="Privacy Detection Tool")
    parser.add_argument("-scan", type=str, required=True, help="Text to scan")
    parser.add_argument("-config", type=str, help="Path to config file")

    args = parser.parse_args()

    try:
        scanner = PrivacyScanner(args.config)
        results = scanner.scan_text(args.scan)

        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
