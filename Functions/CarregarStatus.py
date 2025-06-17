import json

def ObterStatusInfo():
    with open("config.json") as f:
        config = json.load(f)
    
    type = config["status"]["type"]