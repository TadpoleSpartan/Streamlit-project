"""Utility functions for safe JSON file operations."""
import json
from pathlib import Path
from typing import Any, Dict


def ensure_json_file(file_path: Path, default_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure a JSON file exists and contains valid data.
    
    If the file doesn't exist or is invalid, it will be created/fixed with default content.
    
    Args:
        file_path: Path to the JSON file
        default_content: Default content to use if file is missing or invalid
        
    Returns:
        The loaded JSON data
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        return data
        except (json.JSONDecodeError, ValueError, IOError) as e:
            print(f"Warning: Could not load {file_path}: {e}. Using default content.")
    
    # Create/overwrite with default content
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_content, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving {file_path}: {e}")
    
    return default_content


def safe_load_json(file_path: Path, default_value: Any = None) -> Any:
    """
    Safely load JSON from a file.
    
    If the file is missing or invalid, it will be replaced with the
    provided default value and that default is returned. This ensures that
    future loads won't repeatedly throw decode errors.
    
    Args:
        file_path: Path to the JSON file
        default_value: Default value to return if file doesn't exist or is invalid
        
    Returns:
        Loaded JSON data or default_value
    """
    if default_value is None:
        default_value = {}
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        # write default out so file exists for next time
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_value, f, indent=4, ensure_ascii=False)
        except IOError:
            pass
        return default_value
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
            else:
                return default_value
    except (json.JSONDecodeError, ValueError, IOError):
        # replace corrupt file with default
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_value, f, indent=4, ensure_ascii=False)
        except IOError:
            pass
        return default_value


def safe_save_json(file_path: Path, data: Any) -> bool:
    """
    Safely save data to a JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to save
        
    Returns:
        True if successful, False otherwise
    """
    file_path = Path(file_path)
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error saving {file_path}: {e}")
        return False
