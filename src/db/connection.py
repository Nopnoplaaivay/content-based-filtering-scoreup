import os
from pymongo import MongoClient

from src.utils.logger import LOGGER

MONGO_URI = os.getenv("MONGO_URL")

class MongoDBConnection:
    def __init__(self, url=MONGO_URI, db_name="codelab1"):
        self.url = url
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        """Connect to the MongoDB database."""
        try:
            self.client = MongoClient(self.url)
            self.db = self.client[self.db_name]
            LOGGER.info(f"Connected to MongoDB database: {self.db_name}")
        except Exception as e:
            LOGGER.error(f"Error connecting to MongoDB: {e}")
            raise e

    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            LOGGER.info("MongoDB connection closed.")

    def get_database(self):
        """Get the connected database."""
        if self.db is None:
            raise ValueError("Database connection is not established. Call `connect` first.")
        return self.db
