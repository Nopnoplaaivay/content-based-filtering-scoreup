import os
from bson import ObjectId
from pymongo import MongoClient

from src.utils.logger import LOGGER

MONGO_URI = os.getenv("MONGO_URL")


class Base:
    def __init__(self, collection_name, notion_database_id="c3a788eb31f1471f9734157e9516f9b6", db_name="codelab1"):
        self.connection = None
        self.client = None
        self.collection_name = collection_name
        self.notion_database_id = notion_database_id
        self.db_name = db_name

    def connect(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.connection = self.client[self.db_name][self.collection_name]
            # LOGGER.info(f"Connected to MongoDB collection: {self.collection_name}")
        except Exception as e:
            LOGGER.error(f"Error connecting to MongoDB: {e}")
            raise e

    def close(self):
        if self.client:
            self.client.close()
            # LOGGER.info("MongoDB connection closed.")

    def fetch_one(self, id=None, object_id=False):
        try:
            self.connect()
            query = {"_id": ObjectId(id)} if object_id else {"_id": id}
            document = self.connection.find_one(query)
            # LOGGER.info(f"Fetched document with ID: {id} from {self.collection_name}.")
            return document
        except Exception as e:
            LOGGER.error(f"Error fetching document: {e}")
            raise e
        finally:
            self.close()

    def fetch_all(self, query=None):
        try:
            self.connect()
            query = query or {}
            documents = list(self.connection.find(query))
            # LOGGER.info(f"Fetched {len(documents)} documents from {self.collection_name}.")
            return documents
        except Exception as e:
            LOGGER.error(f"Error fetching documents: {e}")
            raise e
        finally:
            self.close()
