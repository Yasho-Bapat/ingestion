from flask import Blueprint, jsonify, render_template, request
from flask_uploads import UploadSet, configure_uploads, DATA
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
            methods=[self.constants.RestApiMethods.get_api],
        )

        self.blueprint.add_url_rule(
            "/upload-file",
            view_func=self.upload_file,
            methods=[self.constants.RestApiMethods.post],
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
            self.constants.ApiResponseParameters.status: status,
            self.constants.ApiResponseParameters.message: message,
            self.constants.ApiResponseParameters.result: result,
        }
        if additional_data:
            response_data.update(additional_data)

        return jsonify(response_data), status

    def home(self):
        return render_template("index.html")

    def upload_file(self):
        if 'file' not in request.files:
            return self.return_api_response(
                self.constants.ApiStatusCodes.bad_request,
                self.constants.ApiResponseMessages.missing_file,
            )

        file = request.files['file']
        if file.filename == '':
            return self.return_api_response(
                self.constants.ApiStatusCodes.bad_request,
                self.constants.ApiResponseMessages.no_file_selected,
            )

        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.constants.uploads_directory, filename)
            file.save(file_path)

            # Process the uploaded file
            try:
                results = self.document_processor.run(document_name=filename)
                return self.return_api_response(
                    self.constants.ApiStatusCodes.ok,
                    self.constants.ApiResponseMessages.file_uploaded_successfully,
                    results,
                )
            except Exception as e:
                return self.return_api_response(
                    self.constants.ApiStatusCodes.internal_server_error,
                    str(e),
                )
        else:
            return self.return_api_response(
                self.constants.ApiStatusCodes.bad_request,
                self.constants.ApiResponseMessages.invalid_file_type,
            )

    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'pdf'}

    def health_check(self):
        return self.return_api_response(
            self.constants.ApiStatusCodes.ok,
            self.constants.ApiResponseMessages.server_is_running,
        )
