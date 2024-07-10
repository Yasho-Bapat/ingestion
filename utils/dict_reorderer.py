from constants import Constants


def reorder_keys(results):
    ordered_results = {key: results[key] for key in Constants.order if key in results}
    return ordered_results
