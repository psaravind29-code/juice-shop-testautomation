import json

def load_credentials(file_path='new-user.json'):
    with open(file_path, 'r') as f:
        return json.load(f)