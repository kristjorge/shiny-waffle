import json


class Reporter:

    def __init__(self, filename: str, path: str):
        self.path = path
        self.filename = filename

    def aggregate_report(self, data_dict: dict):
        with open(self.path + "/" + self.filename + ".json", "w") as json_out:
            json.dump(data_dict, json_out, sort_keys=False, indent=3)
