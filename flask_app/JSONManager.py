import json
import os


class JSONManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading data: {e}")
            return []

    def save_data(self, data):
        """Save data to JSON file"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    def add_item(self, item):
        """Add new item to JSON"""
        data = self.load_data()
        data.append(item)
        return self.save_data(data)

    def update_item(self, index, item):
        """Update item at specific index"""
        data = self.load_data()
        if 0 <= index < len(data):
            data[index] = item
            return self.save_data(data)
        return False

    def delete_item(self, index):
        """Delete item at specific index"""
        data = self.load_data()
        if 0 <= index < len(data):
            data.pop(index)
            return self.save_data(data)
        return False

# Initialize JSON manager with file path
json_manager = None
