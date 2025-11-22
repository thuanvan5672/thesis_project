# clients/mongo_client.py
from pymongo import MongoClient
from .config import Config


class MongoClientWrapper:
    def __init__(self) -> None:
        """
        Kết nối MongoDB Atlas hoặc MongoDB local dựa trên MONGO_URI trong file .env
        """
        if not Config.MONGO_URI:
            raise ValueError("Thiếu cấu hình MongoDB: MONGO_URI")

        # Tạo client MongoDB
        self.client = MongoClient(Config.MONGO_URI)

        # Lấy tên database từ URI
        db_name = Config.MONGO_URI.rsplit("/", 1)[-1].split("?")[0] or "test"
        self.db = self.client[db_name]

    def get_collection(self, collection_name: str):
        """Trả về một collection MongoDB"""
        return self.db[collection_name]

    def ping(self) -> bool:
        """Ping MongoDB để kiểm tra kết nối"""
        self.client.admin.command("ping")
        return True


# Instance dùng chung trong toàn ứng dụng
mongo_client = MongoClientWrapper()
