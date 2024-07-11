from flask import Blueprint, jsonify, render_template, request
from flask_uploads import UploadSet, configure_uploads, ALL, DATA
import os
from werkzeug.utils import secure_filename

from constants import Constants
from main import DocumentProcessor


class MainRoutes:
    def __init__(self, app):
        self.blueprint = Blueprint("main_routes", __name__, template_folder="templates", static_folder="static")
        self.constants = Constants

        os.makedirs(self.constants.uploads_directory, exist_ok=True)

        self.blueprint.add_url_rule(
            "/",
            view_func=self.home,
            methods=[self.constants.rest_api_methods.get_api],
        )

        self.blueprint.add_url_rule(
            "/ingestion-service",
            view_func=self.ask_viridium_ai,
            methods=[self.constants.rest_api_methods.post],
        )

        self.blueprint.add_url_rule(
            "/upload-file",
            view_func=self.upload_file,
            methods=[self.constants.rest_api_methods.post],
        )

        self.blueprint.add_url_rule("/health", view_func=self.health_check)

        # Initialize file uploads
        self.files = UploadSet('files', DATA)
        app.config['UPLOADS_DEFAULT_DEST'] = self.constants.uploads_directory
        configure_uploads(app, self.files)

        # Initialize DocumentProcessor
        self.document_processor = DocumentProcessor(
            documents_directory=self.constants.uploads_directory,
            persist_directory="chroma_persistence",
            log_file="processing.log",
            chunking_method="recursive"  # or "semantic" based on your need
        )

    def return_api_response(self, status, message, result=None, additional_data=None):
        response_data = {
            self.constants.api_response_parameters.status: status,
            self.constants.api_response_parameters.message: message,
            self.constants.api_response_parameters.result: result,
        }
        if additional_data:
            response_data.update(additional_data)

        return jsonify(response_data), status

    def validate_request_data(self, request_data, required_params):
        missing_params = [
            param for param in required_params if param not in request_data
        ]
        if missing_params:
            return False, missing_params
        return True, None

    def home(self):
        return render_template("index.html")

    def ask_viridium_ai(self):
        request_data = request.get_json()
        required_params = [
            self.constants.input_parameters["material_name"],
        ]

        valid_request, missing_params = self.validate_request_data(
            request_data, required_params
        )
        if not valid_request:
            return self.return_api_response(
                self.constants.api_status_codes.bad_request,
                self.constants.api_response_messages.missing_required_parameters,
                f"{self.constants.api_response_parameters.missing_parameters}: {missing_params}",
            )

        ask_vai = DocumentProcessor()
        ask_vai.query(request_data[self.constants.input_parameters["material_name"]],
                      request_data[self.constants.input_parameters["manufacturer_name"]],
                      request_data[self.constants.input_parameters["work_content"]])

        return self.return_api_response(
            self.constants.api_status_codes.ok,
            self.constants.api_response_messages.success,
            ask_vai.result,
        )

    def upload_file(self):
        if 'file' not in request.files:
            return self.return_api_response(
                self.constants.api_status_codes.bad_request,
                self.constants.api_response_messages.missing_file,
            )
        file = request.files['file']
        if file.filename == '':
            return self.return_api_response(
                self.constants.api_status_codes.bad_request,
                self.constants.api_response_messages.no_file_selected,
            )
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(self.constants.uploads_directory, filename))
            # Here you can process the file as needed

            return self.return_api_response(
                self.constants.api_status_codes.ok,
                self.constants.api_response_messages.file_uploaded_successfully,
                {'filename': filename},
            )
        else:
            return self.return_api_response(
                self.constants.api_status_codes.bad_request,
                self.constants.api_response_messages.invalid_file_type,
            )

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in {'pdf'}

    def health_check(self):
        return self.return_api_response(
            self.constants.api_status_codes.ok,
            self.constants.api_response_messages.server_is_running,
        )
