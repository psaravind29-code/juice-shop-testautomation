"""Configuration utilities for test automation."""
import json
import os


def load_credentials(file_path=None):
    """
    Load test user credentials from new-user.json.
    
    Args:
        file_path: Optional path to credentials file. If None, searches common locations.
        
    Returns:
        dict: {"email": "...", "password": "..."}
    """
    if file_path is None:
        # Try multiple common locations
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '../tests/new-user.json'),
            os.path.join(os.path.dirname(__file__), '../../tests/new-user.json'),
            'tests/new-user.json',
            './new-user.json',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if file_path is None:
            raise FileNotFoundError(
                "Could not find new-user.json in any expected location. "
                "Searched: tests/new-user.json, ./new-user.json"
            )
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Credentials file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        creds = json.load(f)
    
    # Validate structure
    if 'email' not in creds or 'password' not in creds:
        raise ValueError(
            f"Invalid credentials format in {file_path}. "
            "Expected: {{\"email\": \"...\", \"password\": \"...\"}}"
        )
    
    return creds