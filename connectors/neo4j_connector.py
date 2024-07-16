from neo4j import GraphDatabase

from constants import Constants


class Neo4jConnector:
    def __init__(self):
        self.constants = Constants

        self.driver = GraphDatabase.driver(self.constants.neo4j_uri, auth=self.constants.neo4j_auth)
        self.driver.verify_connectivity()

    def get_session(self):
        return self.driver.session()
