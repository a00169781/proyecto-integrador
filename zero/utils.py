# utils.py
# File with utility functions common to the project

from openai import OpenAI
import os, os.path
from datetime import datetime
import json
import requests
import re
import copy
from os import path

from pathlib import Path

def get_current_timestamp() -> str:
  """
  Returns the current timestamp in the format "YYYY-MM-DD hh:mm:ss".
  """
  now = datetime.now()
  return now.strftime("%Y-%m-%d %H:%M:%S")

def get_current_date() -> str:
  """
  Returns the current date in the format "YYYY-MM-DD".
  """
  now = datetime.now()
  return now.strftime("%Y-%m-%d")

def save_dict_to_drive(data: dict, filename: str) -> None:
  """Saves a dictionary to a JSON file in Google Drive.

  Args:
    data: The dictionary to save.
    filename: The name of the file to save to (e.g., 'my_data.json').
  """
  # Uncomment the following lines if you are using google colab
  # drive.mount('/content/drive')
  # filepath = f'/content/drive/MyDrive/Colab/{filename}'

  # If you are not using google colab, you can save the file in the current directory
  filepath = f'{filename}'
  with open(filepath, 'w') as f:
    json.dump(data, f, indent=4)
  print(f"Dictionary saved to: {filepath}")

def load_dict_from_drive(filename: str) -> dict | None:
  """Loads a dictionary from a JSON file in Google Drive.

  Args:
    filename: The name of the file to load from (e.g., 'my_data.json').

  Returns:
    The loaded dictionary, or None if the file is not found.
  """
  # Uncomment the following lines if you are using google colab
  # drive.mount('/content/drive')
  # filepath = f'/content/drive/MyDrive/Colab/{filename}'

  # If you are not using google colab, you can load the file from the current directory
  filepath = f'{filename}'
  try:
    with open(filepath, 'r') as f:
      data = json.load(f)
    print(f"Dictionary loaded from: {filepath}")
    return data
  except FileNotFoundError:
    print(f"File not found: {filepath}")
    return None


    # Example usage:
    # my_dict = {'key1': 'value1', 'key2': 'value2'}
    # save_dict_to_drive(my_dict, 'my_dictionary.json')

    # loaded_dict = load_dict_from_drive('my_dictionary.json')
    # if loaded_dict:
    #   print(loaded_dict)



def zs_prompt() -> str:
  return """
You are an AI language model specialized in determining causal relationships. When presented with a question about causality, analyze the information carefully and provide a clear, concise response. Your answer should:

Reasoning: Begin with a brief explanation of whether and how the cause leads to the effect.
Conclusion: End with "The answer is Yes." or "The answer is No." based on your analysis.
"""

