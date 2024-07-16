import os, dotenv, time
from langchain_community.graphs import Neo4jGraph
from langchain_openai import AzureChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer

dotenv.load_dotenv()

class LangGraphProc:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
        self.graph = Neo4jGraph()
        self.llm = AzureChatOpenAI(temperature=0, deployment_name=os.getenv("LLM_DEPLOYMENT"))
        self.llm_transformer = LLMGraphTransformer(llm=self.llm,
                                                   allowed_nodes=["Chemical", "Carcinogen info", "Manufacturer Name"],
                                                   allowed_relationships=["CONTAINS_CHEMICAL", "IS_CARCINOGEN", "MANUFACTURED_BY"])

    def create_graph_documents(self, doc):
        print("create graph called")
        rn = time.perf_counter()
        graph_documents = self.llm_transformer.convert_to_graph_documents(doc)
        print(f"Graph creation took {time.perf_counter() - rn} seconds")
        print(f"Nodes:{graph_documents[0].nodes}")
        print(f"Relationships:{graph_documents[0].relationships}")
        self.graph.add_graph_documents(graph_documents)