import os
from bson import ObjectId
from pymongo import MongoClient
from typing import Dict, List, Optional

from src.utils.logger import LOGGER
from .repo_interface import RepoInterface

MONGO_URI = os.getenv("MONGO_URL")


class BaseRepo(RepoInterface):
    def __init__(
        self,
        collection,
        notion_database_id="c3a788eb31f1471f9734157e9516f9b6",
        db="codelab1",
    ):
        self.notion_database_id = notion_database_id
        self.db = db
        self.collection = collection
        self._client = None
        self._db = None
        self._collection = None

    def connect(self):
        if not self._client:
            try:
                self._client = MongoClient(
                    MONGO_URI,
                    maxpoolsize=50,
                    connectTimeoutMS=30000,
                    socketTimeoutMS=30000,
                )
                self._db = self._client[self.db]
                self._collection = self._db[self.collection]
                # self.connection = self._client[self.db][self.collection]
                LOGGER.info(f"Connected to MongoDB")
            except Exception as e:
                LOGGER.error(f"Error connecting to MongoDB: {e}")
                raise 

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._collection = None
        LOGGER.info("Closed MongoDB connection.")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def fetch_one(self, query=None) -> Optional[Dict]:
        try:
            with self:
                document = self._collection.find_one(query)
                return document
        except Exception as e:
            LOGGER.error(f"Error fetching document: {e}")
            raise 

    def fetch_all(self, query=None) -> List[Dict]:
        try:
            with self:
                query = query or {}
                documents = list(self._collection.find(query))
                return documents
        except Exception as e:
            LOGGER.error(f"Error fetching documents: {e}")
            raise

    def insert_one(self, data: Dict) -> str:
        try:
            with self:
                self._collection.insert_one(data)
        except Exception as e:
            LOGGER.error(f"Error inserting document: {e}")
            raise

    def insert_many(self, data: List[Dict]) -> List[str]:
        try:
            with self:
                self._collection.insert_many(data)
        except Exception as e:
            LOGGER.error(f"Error inserting documents: {e}")
            raise

    def update_one(self, query: Dict, update: Dict) -> bool:
        try:
            with self:
                self._collection.update_one(query, update)
        except Exception as e:
            LOGGER.error(f"Error updating document: {e}")
            raise

    def update_many(self, query: Dict, update: Dict) -> int:
        try:
            with self:
                result = self._collection.update_many(query, update)
                return result.modified_count
        except Exception as e:
            LOGGER.error(f"Error updating documents: {e}")
            raise