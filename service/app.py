from dotenv import load_dotenv

from additional_data_from_sds.routes import MainRoutes

load_dotenv()

from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
from apispec import APISpec
from flask_swagger_ui import get_swaggerui_blueprint
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

from constants import Constants
from app_insights_connector import AppInsightsConnector

constants = Constants

app = Flask(__name__)
CORS(app)

main_routes = MainRoutes(app=app)
app.register_blueprint(main_routes.blueprint, url_prefix=Constants.api_version)

logger = AppInsightsConnector().get_logger()

swagger_endpoint = constants.swagger_endpoint
# Swagger and APISpec setup
spec = APISpec(
    title=constants.apispec_config.title,
    version=constants.apispec_config.version,
    openapi_version=constants.apispec_config.openapi_version,
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

with app.test_request_context():
    for view in [
        main_routes.home,
        main_routes.upload_file,
        main_routes.health_check,
    ]:
        spec.path(view=view)

swaggerui_blueprint = get_swaggerui_blueprint(
    swagger_endpoint,
    constants.api_swagger_json,
    config={"app_name": constants.swagger_app_name},
)

app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_endpoint)


@app.route('/')
def root():
    return redirect(constants.api_version)


@app.route(constants.api_swagger_json)
def create_swagger_spec():
    return jsonify(spec.to_dict())


@app.before_request
def log_request_info():
    logger.info(f"API REQUEST : {request.method} {request.path}")
    pass


@app.after_request
def log_response_info(response):
    logger.info(f"API RESPONSE : {response.status}")
    return response


if __name__ == "__main__":
    # Main thread will serve the api calls
    app.run(
        threaded=True,
        debug=True,
        port=constants.flask_app_port,
        host=constants.flask_host,
    )
