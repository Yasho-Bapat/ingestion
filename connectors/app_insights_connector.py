import logging

from opencensus.ext.azure.log_exporter import AzureLogHandler

from constants import Constants


class AppInsightsConnector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.logger.setLevel(logging.INFO)

        self.azure_handler = AzureLogHandler(connection_string=Constants.azure_app_insights_connector)
        self.logger.addHandler(self.azure_handler)

        self.local_logs_handler = logging.FileHandler('../experiment/logs/ingestion_service_experiment.log')
        self.logger.addHandler(self.local_logs_handler)

    def get_logger(self):
        return self.logger
