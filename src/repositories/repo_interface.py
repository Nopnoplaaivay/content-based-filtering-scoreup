from typing import Dict, List, Optional
from abc import ABC, abstractmethod
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RepoInterface(ABC):
    """Interface for repository pattern"""
    
    @abstractmethod
    def fetch_one(self, query: Dict) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def fetch_all(self, query: Dict) -> List[Dict]:
        pass
    
    @abstractmethod
    def insert_one(self, document: Dict) -> str:
        pass
    
    @abstractmethod
    def insert_many(self, documents: List[Dict]) -> List[str]:
        pass
    
    @abstractmethod
    def update_one(self, query: Dict, update: Dict) -> bool:
        pass
    
    @abstractmethod
    def update_many(self, query: Dict, update: Dict) -> int:
        pass
    