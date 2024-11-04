from http import HTTPStatus
from typing import Dict, Any, Tuple
from flask import Flask, request
from flask_restful import Resource, Api
from dataclasses import dataclass

from scanner import PrivacyScanner, DEFAULT_OPERATOR_CONFIG, PrivacyScannerError

DEBUG_MODE: bool = True

app = Flask(__name__)
api = Api(app)


@dataclass
class APIResponse:
    """Standard API response structure"""

    message: str
    data: Dict[str, Any] = None
    status_code: int = HTTPStatus.OK

    def to_dict(self) -> Dict[str, Any]:
        response = {"message": self.message}
        if self.data is not None:
            response.update(self.data)
        return response


class PrivacyToolBase(Resource):
    """Base class for Privacy Tool endpoints with common functionality"""

    def _validate_input(
        self, json_data: Dict[str, Any], required_field: str
    ) -> Tuple[bool, APIResponse]:
        """Validate input data"""
        if not json_data:
            return False, APIResponse(
                message="No JSON data provided", status_code=HTTPStatus.BAD_REQUEST
            )

        if required_field not in json_data:
            return False, APIResponse(
                message=f"Missing required field: {required_field}",
                status_code=HTTPStatus.BAD_REQUEST,
            )

        text = json_data[required_field]
        if not text or not isinstance(text, str):
            return False, APIResponse(
                message=f"Invalid or empty {required_field} field",
                status_code=HTTPStatus.BAD_REQUEST,
            )

        return True, None


class PrivacyToolHome(PrivacyToolBase):
    """Welcome endpoint"""

    def get(self) -> Dict[str, str]:
        return APIResponse(
            message="Welcome to Privacy Protection Tool", data={"version": "1.0"}
        ).to_dict()


class PrivacyToolScanner(PrivacyToolBase):
    """Scanner endpoint"""

    def post(self) -> Dict[str, Any]:
        try:
            json_data = request.get_json(force=True)
            is_valid, error_response = self._validate_input(json_data, "scan")
            if not is_valid:
                return error_response.to_dict(), error_response.status_code

            config = json_data.get("config")
            privacy_scanner = PrivacyScanner(config)
            result = privacy_scanner.scan_text(json_data["scan"])

            return APIResponse(message="Success", data={"entities": result}).to_dict()

        except PrivacyScannerError as e:
            return APIResponse(
                message=str(e), status_code=HTTPStatus.BAD_REQUEST
            ).to_dict(), HTTPStatus.BAD_REQUEST
        except Exception as e:
            return APIResponse(
                message=f"Internal server error: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            ).to_dict(), HTTPStatus.INTERNAL_SERVER_ERROR


class PrivacyToolAnonymize(PrivacyToolBase):
    """Anonymization endpoint"""

    def _validate_method(self, method: str) -> Tuple[bool, APIResponse]:
        """Validate anonymization method"""
        if method not in DEFAULT_OPERATOR_CONFIG:
            return False, APIResponse(
                message=f"Invalid anonymization method: {method}. Valid methods are: {list(DEFAULT_OPERATOR_CONFIG.keys())}",
                status_code=HTTPStatus.BAD_REQUEST,
            )
        return True, None

    def post(self) -> Dict[str, Any]:
        try:
            json_data = request.get_json(force=True)
            is_valid, error_response = self._validate_input(json_data, "anonymize")
            if not is_valid:
                return error_response.to_dict(), error_response.status_code

            method = str(json_data.get("method", "replace")).lower()
            is_valid_method, error_response = self._validate_method(method)
            if not is_valid_method:
                return error_response.to_dict(), error_response.status_code

            config = json_data.get("config")
            privacy_scanner = PrivacyScanner(config)
            anonymized_text, entities = privacy_scanner.anonymize_text(
                json_data["anonymize"], method
            )

            return APIResponse(
                message="Success",
                data={"entities": entities, "anonymized_output": anonymized_text},
            ).to_dict()

        except PrivacyScannerError as e:
            return APIResponse(
                message=str(e), status_code=HTTPStatus.BAD_REQUEST
            ).to_dict(), HTTPStatus.BAD_REQUEST
        except Exception as e:
            return APIResponse(
                message=f"Internal server error: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            ).to_dict(), HTTPStatus.INTERNAL_SERVER_ERROR


api.add_resource(PrivacyToolHome, "/")
api.add_resource(PrivacyToolScanner, "/scan")
api.add_resource(PrivacyToolAnonymize, "/anonymize")

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)
