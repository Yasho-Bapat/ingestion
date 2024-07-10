import json
import logging


def store_results(filename: str, results: dict, logger: logging.Logger):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        logger.info(f"Cumulative result stored successfully in {filename}")
    except FileNotFoundError as e:
        logger.info(f"{e}; CREATING NEW FILE")
        data = []
    data.append(results)

    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        logger.info(f"Stored results successfully in {filename}.")
        return f"Stored results successfully in {filename}."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Unexpected error occured: {e}"