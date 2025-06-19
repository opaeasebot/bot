import json
import os

class Database:
    @staticmethod
    def Obter(arquivo: str) -> dict:
        if not os.path.exists(arquivo):
            return {}
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def Salvar(arquivo: str, data: dict):
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
