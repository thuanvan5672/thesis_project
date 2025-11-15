# clients/mongo_client.py
from pymongo import MongoClient
from .config import Config


class MongoClientWrapper:
    def __init__(self) -> None:
        # Kết nối MongoDB Atlas (hoặc local)
        self.client = MongoClient(Config.MONGO_URI)
        # Lấy tên DB từ URI (phần sau dấu / cuối cùng)
        db_name = Config.MONGO_URI.rsplit("/", 1)[-1].split("?")[0] or "test"
        self.db = self.client[db_name]

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    def ping(self) -> bool:
        # Gọi lệnh ping đơn giản
        self.client.admin.command("ping")
        return True


# Instance dùng chung trong toàn app
mongo_client = MongoClientWrapper()
