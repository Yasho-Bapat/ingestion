import os
from time import time

from main import DocumentProcessor
from utils.store_results import store_results


if __name__ == "__main__":
    directory_path = "test_docs"
    processor = DocumentProcessor(documents_directory=directory_path, persist_directory="experiment_chroma_db", log_file="logs/ingestion_service_experiment.log", chunking_method="semantic", store_to_neo4j=False)
    files = os.listdir(directory_path)
    files = [f for f in files if os.path.isfile(os.path.join(directory_path, f))]
    timestamp = str(int(time()))
    for file in files:
        print(f"Processing {file}...")
        processor.logger.info(f"Submitting {file} for processing...")
        results = processor.experiment_gliner_ner(file)
        print(store_results(filename=f"json_dump/gliner_ner_result_{timestamp}.json", results=results, logger=processor.logger))
        print(results)
