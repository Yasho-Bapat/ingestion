import os, dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_openai import AzureChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer

dotenv.load_dotenv()

class LangGraphProc:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
        self.graph = Neo4jGraph()
        self.llm = AzureChatOpenAI(temperature=0, deployment_name=os.getenv("LLM_DEPLOYMENT"))
        self.llm_transformer = LLMGraphTransformer(llm=self.llm)

    def create_graph_documents(self, doc):
        print("create graph called")
        graph_documents = self.llm_transformer.convert_to_graph_documents(doc)
        print(f"Nodes:{graph_documents[0].nodes}")
        print(f"Relationships:{graph_documents[0].relationships}")
        self.graph.add_graph_documents(graph_documents)