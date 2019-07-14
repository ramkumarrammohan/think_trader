import json


def print_json(data):
    """
    Print dict data in json formatted data
    Used to print json in easy reable format
    """
    print(json.dumps(data, indent=4, sort_keys=True, default=str))
