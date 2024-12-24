import os
from bson import ObjectId
from pymongo import MongoClient

from src.utils.logger import LOGGER

MONGO_URI = os.getenv("MONGO_URL")


class BaseRepo:
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
        except Exception as e:
            LOGGER.error(f"Error connecting to MongoDB: {e}")
            raise e

    def close(self):
        if self.client:
            self.client.close()
        LOGGER.info("Closed MongoDB connection.")

    def fetch_one(self, id=None, object_id=False):
        try:
            self.connect()
            query = {"_id": ObjectId(id)} if object_id else {"_id": id}
            document = self.connection.find_one(query)
            return document
        except Exception as e:
            LOGGER.error(f"Error fetching document: {e}")
            raise e

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

    def insert_one(self, data):
        try:
            self.connect()
            self.connection.insert_one(data)
            # LOGGER.info(f"Inserted document: {data}.")
        except Exception as e:
            LOGGER.error(f"Error inserting document: {e}")
            raise e

    def insert_many(self, data):
        try:
            self.connect()
            self.connection.insert_many(data)
        except Exception as e:
            LOGGER.error(f"Error inserting documents: {e}")
            raise e

    def update_one(self, query, update):
        try:
            self.connect()
            self.connection.update_one(query, update)
        except Exception as e:
            LOGGER.error(f"Error updating document: {e}")
            raise e

    def update_many(self, query, update):
        try:
            self.connect()
            self.connection.update_many(query, update)
        except Exception as e:
            LOGGER.error(f"Error updating documents: {e}")
            raise e