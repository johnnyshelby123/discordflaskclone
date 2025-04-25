import json
import os
import threading
from typing import Dict, List, Any, Optional

class JSONStorage:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.locks = {}
        
    def _get_lock(self, file_path: str) -> threading.Lock:
        """Get or create a lock for a specific file path."""
        if file_path not in self.locks:
            self.locks[file_path] = threading.Lock()
        return self.locks[file_path]
        
    def read(self, collection: str, id: str) -> Optional[Dict]:
        """Read a document from a collection by ID."""
        file_path = os.path.join(self.data_dir, collection, f"{id}.json")
        if not os.path.exists(file_path):
            return None
            
        lock = self._get_lock(file_path)
        with lock:
            with open(file_path, 'r') as f:
                return json.load(f)
                
    def write(self, collection: str, id: str, data: Dict) -> None:
        """Write a document to a collection with the given ID."""
        dir_path = os.path.join(self.data_dir, collection)
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, f"{id}.json")
        lock = self._get_lock(file_path)
        
        with lock:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
    def delete(self, collection: str, id: str) -> bool:
        """Delete a document from a collection by ID."""
        file_path = os.path.join(self.data_dir, collection, f"{id}.json")
        if not os.path.exists(file_path):
            return False
            
        lock = self._get_lock(file_path)
        with lock:
            os.remove(file_path)
            return True
            
    def list_all(self, collection: str) -> List[Dict]:
        """List all documents in a collection."""
        dir_path = os.path.join(self.data_dir, collection)
        if not os.path.exists(dir_path):
            return []
            
        result = []
        for filename in os.listdir(dir_path):
            if filename.endswith('.json'):
                id = filename[:-5]  # Remove .json extension
                data = self.read(collection, id)
                if data:
                    result.append(data)
                    
        return result
        
    def query(self, collection: str, filter_func) -> List[Dict]:
        """Query documents in a collection using a filter function."""
        all_items = self.list_all(collection)
        return [item for item in all_items if filter_func(item)]
