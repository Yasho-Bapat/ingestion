import json

from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph


graph = Neo4jGraph(url="neo4j+s://663e91a3.databases.neo4j.io", username='neo4j', password='N_Cvo6fQ-rURxaON67dmtu4HalNLG54x86ghrLQVsuw')

with open("../json_dump/tempdelete_1720606764.json", "r") as file:
    data = json.load(file)

for i, document in enumerate(data):
    material_name = document["identification"]["material_name"]
    manu_name = document["identification"]["manufacturer_info"]["name"]
    chemicals = document["material_composition"]
    graph.query(f"""
        CREATE (m{i}: MATERIAL {{name:'{material_name}', manu_name:'{manu_name}'}})
    """)
    print(chemicals)
    for i, chem in enumerate(chemicals['composition']):
        chem_name = chem["name"]
        cas = chem["cas_number"]
        graph.query(f"""
        CREATE (c{i}: CHEMICAL {{name: '{chem_name}', cas_number: '{cas}'}})
        """)
        print(f"{chem_name} successfully inserted")
    print(f"{material_name} successfully inserted")
