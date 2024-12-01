"""
Configuration settings for the product creation system
"""

import os

# Path Settings
PATH_SETTINGS = {
    "input": {
        "directory": "input",  # Directory for input files
        "filename": "input.csv",  # Name of input file
        "required_columns": ["details"]  # Required columns in input file
    },
    "output": {
        "directory": "output",  # Directory for output files
        "data_filename": "product_information.csv",  # Name of output CSV
        "images_directory": "images"  # Subdirectory for generated images
    }
}

# Create full paths
def get_input_path():
    """Get the full path to input file"""
    return os.path.join(PATH_SETTINGS["input"]["directory"], 
                       PATH_SETTINGS["input"]["filename"])

def get_output_csv_path():
    """Get the full path to output CSV file"""
    return os.path.join(PATH_SETTINGS["output"]["directory"], 
                       PATH_SETTINGS["output"]["data_filename"])

def get_image_directory():
    """Get the full path to images directory"""
    return os.path.join(PATH_SETTINGS["output"]["directory"], 
                       PATH_SETTINGS["output"]["images_directory"])

# API Configuration
API_SETTINGS = {
    "mistral": {
        "base_url": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-tiny",
        "max_retries": 3,
        "retry_delay": 2,
        "timeout": 30
    },
    "together": {
        "model": "black-forest-labs/FLUX.1-schnell-Free",
        "steps": 2,
        "n": 1
    }
}

# File Settings
FILE_SETTINGS = {
    "image_prefix": "image_",
    "image_format": "png"
}

# Content Settings
CONTENT_SETTINGS = {
    "title": {
        "max_chars": 50,
        "suffix": ""
    },
    "description": {
        "max_chars": 150,
        "template": """
        <p></p>
        """
    },
    "image_prompt": {
        "max_chars": 75
    }
}

# Image Generation Settings
IMAGE_SETTINGS = {
    "width": 1024,
    "height": 1024,
    "quality": "standard"
}

# Output Columns
OUTPUT_COLUMNS = [
    "file_name",
    "local_path",
    "title",
    "description",
    "tags"
]

# Create required directories if they don't exist
def create_directories():
    """Create all required directories if they don't exist"""
    directories = [
        PATH_SETTINGS["input"]["directory"],
        PATH_SETTINGS["output"]["directory"],
        get_image_directory()
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True) 