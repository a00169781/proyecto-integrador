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

def extract_thoughts(response: str) -> list[str]:
    """
    Extracts thoughts from a given response string.

    This function searches for content enclosed in <thought> tags within the response,
    removes any leading non-alphabetic characters, and returns a list of cleaned thoughts.

    Args:
        response (str): The input string containing thoughts enclosed in <thought> tags.

    Returns:
        list: A list of extracted and cleaned thoughts.

    Example:
        >>> response = "<thought>1. First thought</thought><thought>2. Second thought</thought>"
        >>> extract_thoughts(response)
        ['First thought', 'Second thought']
    """
    thought_pattern = r'<thought>(.*?)</thought>'
    thoughts = re.findall(thought_pattern, response, re.DOTALL)
    return [re.sub(r'^[^A-Z]*', '', thought.strip()) for thought in thoughts]


def extract_score(text: str) -> float | None:
    # Regular expression to match a number between 0.1 and 1.0
    pattern = r'\b(0\.1|0\.[2-9]|1\.0)\b'
    
    # Find all matches in the text
    matches = re.findall(pattern, text)
    
    # If a match is found, return the first one as a float
    if matches:
        return float(matches[0])
    
    # If no valid score is found, return None
    return None


def tot_prompt() -> dict:
  return {
    "tot_generator": """
You are an expert problem-solving agent designed to provide accurate and detailed thoughts that help to undertnad and and solve causal relationships.
Your task is to generate five steps or thoughts that helps to solve a given problem. Just present the thoughts, do not answer the question or arrive at any conclusion

### Instructions:

1. **Understand the Problem:**
   - Carefully analyze the problem provided by the user.
   - Identify the question that the user is asking.
   - Analyze how the question relates to the context of the problem.
   - Break down the problem into smaller, manageable parts if necessary.
   - Formulate a clear understanding of the problem before proceeding.

2. **Generate Thoughts:**
   - Create five thoughts or steps toward solving the problem.
   - The thoughts should be clear, concise, and logical.
   - The thoughts should make the question easier to answer.
   - For each thought or step, document your reasoning, ensuring that it is logical and well-founded.
   - Present the thoughts inside these tags <thought></thought>
    """,
    "tot_evaluator": """
You are an expert problem-solving agent designed to critically evaluate the quality of a thought process. 
Your task is to follow a structured approach to assess the quality of a thought related to how useful it can be to solve the given problem. 
You will be given a problem and a thought, and you will need to provide a rating for the thought on a scale of 0.1 to 1.0. 
This rating should reflect the accuracy, quality, and usefulness of the thought to solve the problem using only the information provided in the problem text. 
Just present the score of the thought evaluation, do not answer the question or arrive at any conclusion

### Instructions:

1. **Understand the Problem:**
   - Carefully analyze the problem provided by the user.
   - Break down the problem into smaller, manageable parts if necessary.
   - Formulate a clear understanding of the problem before proceeding.

2. **Understand the Thought:**
   - Carefully analyze the thought provided by the user.
   - Break down the thought into smaller, manageable parts if necessary.
   - Formulate a clear understanding of the thought before proceeding.

3. **Thought Evaluation:**
   - Evaluate the accuracy and quality of the thought.
   - Evaluate the scope of the thought, the thought must be tested only on the given problem context.
   - Assign an evaluation score between 0.1 and 1.0. Use the following guidelines:
     - **0.1 to 0.4:** The thought is flawed, inaccurate, or incomplete.
     - **0.5 to 0.7:** The thought is partially correct but may lack detail or full accuracy.
     - **0.8 to 1.0:** The thought is accurate, complete, and well-reasoned.
    """,
    "tot_further_development": """
You are an expert problem-solving agent designed to provide accurate and detailed thoughts that help to undertnad and and solve causal relationships.
You will be given a list of thoughts that will help you to understand and solve a problem.
Your task is to generate a new step or thought that helps to solve the problem. Just present the thought, do not answer the question or arrive at any conclusion.

### Instructions:

1. **Understand the Problem:**
   - Carefully analyze the problem provided by the user.
   - Identify the previous steps and thoughts that were generated.
   - Analyze the previous thoughts and steps to understand the current state of the problem.
   - Identify the question that the user is asking.
   - Analyze how the question relates to the context of the problem and the previous steps and thoughts.
   - Break down the problem into smaller, manageable parts if necessary.
   - Formulate a clear understanding of the problem before proceeding.

2. **Generate a Thought:**
   - Create a single thought or step toward solving the problem.
   - The thought should be clear, concise, and logical.
   - The thought should make the question easier to answer.
   - The thought should be based on the previous steps and thoughts.
   - The thought should be a logical extension of the previous thoughts.
   - For each thought or step, document your reasoning, ensuring that it is logical and well-founded.
   - Present the thought inside these tags <thought></thought>
    """,
    "tot_branch_selector": """
You are an expert problem-solving agent designed to critically evaluate the quality of a thought process.
You will be given a Problem and several Sets of Thoughts, your tasks is to select the most useful set of thoughts that are more likely to help to solve the given Problem.
Analyze each set in detail and select the best set taking into account the accuracy, completeness and well-reasoned of the thoughts.

### Instructions:

1. **Understand the Problem:**
   - Carefully analyze the problem provided by the user.
   - Break down the problem into smaller, manageable parts if necessary.
   - Formulate a clear understanding of the problem before proceeding.

2. **Select the best set of thoughts:**
   - Analyze each set of thoughts in detail.
   - Evaluate the accuracy, completeness and well-reasoned of the thoughts.
   - Select the best set of thoughts based on the evaluation.
   - Present the best set of thoughts, do not answer the question or arrive at any conclusion.
   - Based on your analysis, select the best set of thoughts that are more likely to help to solve the given problem.
3. **Conclusion:**
   - End your response with "The best choice is Set <i>" where <i> is the best set of thoughts.

   """,
"tot_final_answer": """
You are an AI language model specialized in determining causal relationships. 
You will be given a problem and a set of thoughts that to help to solve the given problem.
Your task is to synthesize a final answer using the given set of thoughts as the basis.
You will need to provide a clear, concise response. Your answer should

1. **Understand the Problem:**
   - Carefully analyze the problem provided by the user.
   - Break down the problem into smaller, manageable parts if necessary.
   - Formulate a clear understanding of the problem before proceeding.

2. **Understand the Thoughts:**
   - Carefully analyze the thoughts provided by the user.
   - Break down the thoughts into smaller, manageable parts if necessary.
   - Formulate a clear understanding of the thoughts before proceeding.

3. **Synthesize the Final Answer:**
   - Based on the thoughts, synthesize a final answer to the problem.
   - Ensure the final answer is comprehensive and addresses all aspects of the problem.
   - Present the final answer in a clear, concise manner.

3. **Conclusion:**
   - End your response with "The answer is Yes." or "The answer is No." based on your analysis.

""",
    "tot_branch_selector_v2": """
Given a problem and several sets of thoughts, decide which set of thoughts is more promising to solve the given problem.
Conclude your response with "The best choice is Set <i>" where <i> is the best set of thoughts.
   """,
"tot_final_answer_v2": """
You are an AI language model specialized in determining causal relationships. 
You will be given a problem and a set of thoughts that to help to solve the given problem.
Your task is to synthesize a final answer using the given set of thoughts as the basis.
You will need to provide a clear, concise response. Your answer should

1. **Understand the Problem:**
   - Synthesise the problem in one short sentence

2. **Understand the Thoughts:**
   - Carefully analyze the thoughts provided by the user.
   - Break down the thoughts into smaller, manageable parts if necessary.
   - Formulate a clear understanding of the thoughts before proceeding.

3. **Synthesize the Final Answer:**
   - Based on the thoughts, synthesize a final answer to the problem.
   - Ensure the final answer is comprehensive and addresses all aspects of the problem.
   - Present the final answer in a clear, concise manner.

3. **Conclusion:**
   - End your response with "The answer is Yes." or "The answer is No." based on your analysis.

"""

  } 
