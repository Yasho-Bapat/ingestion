from langchain_chroma import Chroma
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
import json, time, os, dotenv

from langchain_community.callbacks import get_openai_callback

from langchain_core.utils.function_calling import convert_to_openai_function
from outputs import MaterialComposition, DocumentInformation, Identification

dotenv.load_dotenv()

ENDPOINT = os.getenv("ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
embedding_function = AzureOpenAIEmbeddings(deployment="langchain-splitting-test1", api_key=AZURE_OPENAI_API_KEY, azure_endpoint=ENDPOINT)
llm = AzureChatOpenAI(deployment_name="langchain-askvai-test-4o", api_key=AZURE_OPENAI_API_KEY, azure_endpoint=ENDPOINT, api_version=OPENAI_API_VERSION)

db = Chroma(persist_directory="./chroma_db", collection_name="semantic", embedding_function=embedding_function)

# material_function = [convert_to_openai_function(MaterialComposition), convert_to_openai_function(Identification)]
id_function = [convert_to_openai_function(Identification)]
material_function = [convert_to_openai_function(DocumentInformation)]
materialmodel = llm.bind_functions(functions=material_function)
idmodel = llm.bind(functions=id_function, function_call={"name": "Identification"})

# Placeholder
template = """
You will be given selected chunks from a safety datasheet of a material. Your job is to find whatever is requested by 
the user. Return output as a JSON object. 
"""
prompt = ChatPromptTemplate.from_messages([
    ("system", template),
    ("human", "context: {docs}, query: {query}")
])

parser = JsonOutputFunctionsParser()

material_chain = prompt | materialmodel | parser
id_chain = prompt | idmodel | parser

material_query = "Return material composition and identification information in the document"
docs = db.similarity_search(material_query)
docus = [doc.page_content for doc in docs]
# print(docus)

res = {"time": time.time()}

costs = []
tokens = []
with get_openai_callback() as cb:
    res["material_info"] = material_chain.invoke({"docs": docus, "query": material_query})
    costs.append(cb.total_cost)
    tokens.append(cb.total_tokens)

# id_query = "Return section on material identification"
# docs = db.similarity_search(id_query)
# documents = [doc.page_content for doc in docs]
# print("retrieved stuff for id query")
# with get_openai_callback() as cb:
#     res["identification"] = id_chain.invoke({"docs": documents, "query": material_query})
#     costs.append(cb.total_cost)
#     tokens.append(cb.total_tokens)

res["total_cost"] = sum(costs)
res["total_tokens"] = sum(tokens)

with open("yashoresult.json", "w") as f:
    json.dump(res, f, indent=4)


