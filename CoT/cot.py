# Libraries
from openai import OpenAI
import os, os.path
from datetime import datetime
import json
import requests
import re
import copy
from os import path
from utils import (
    save_dict_to_drive,
    load_dict_from_drive,
    cot_prompt
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=OPENAI_API_KEY,
)

prompt = cot_prompt()

cot_model_params = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Input"},
    ],
}


def run_cot(problem):
    input = problem["input"]
    completion = client.chat.completions.create(
        model=cot_model_params["model"],
        messages=[
            cot_model_params["messages"][0],
            {"role": "user", "content": input},
        ],
    )
    return completion.choices[0].message.content

def get_llm_answer(response, problem):
    llm_answer = re.findall(r"The answer is (Yes|No)\b",response, re.IGNORECASE)
    llm_answers = {
        "Yes":0,
        "No":0
    }

    for posible_answer in llm_answers:
        if posible_answer in llm_answer:
            llm_answers[posible_answer] = 1

    if len(llm_answer) == 1:
        score = problem['target_scores'][llm_answer[0]]
    else:
        return None
    
    node = {
        "input": problem["input"],
        "target_scores": problem['target_scores'],
        "llm_full_answer": response,
        "llm_answer": llm_answers,
        "score": score
    }
    return node


def get_percentage_correct(data):
    correct_results = 0
    for result in data["results"]:
        correct_results += result["score"]
    return correct_results/len(data['results'])

def run_full_pipeline(original_data):
    data = {}
    data["name"] = "chain of thought results to causal judgement task"
    data["description"] = "This file contains the results of the chain of thought LLM to the causal judgement task."
    data["dataset"] = "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/causal_judgement"
    data["prompt"] = prompt
    data["results"] = []
    for idx, problem in enumerate(original_data["examples"]):
        print(f"Processing question {idx+1}/{len(original_data['examples'])}")
        response = run_cot(problem)
        while get_llm_answer(response, problem) is None:
            print("No answer found, retrying...")
            response = run_cot(problem)
        node = get_llm_answer(response, problem)
        data["results"].append(copy.deepcopy(node))
        if idx == 0:
            pass
    return data


def main():
    original_data = load_dict_from_drive("../datasets/task_patched.json")
    data = run_full_pipeline(original_data)
    performance = get_percentage_correct(data)
    data["performance"] = performance
    save_dict_to_drive(data, "./output/chain_of_thought_results.json")
    print(f"Performance: {performance}")

if __name__ == "__main__":
    main()
