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
    tot_prompt,
    extract_thoughts,
    extract_score,
    save_dict_to_drive,
    load_dict_from_drive,
)

depth = 3

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=OPENAI_API_KEY,
)

prompt_dict = tot_prompt()

tot_generator_model_params = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": prompt_dict["tot_generator"]},
        {"role": "user", "content": "Input"},
    ],
}

tot_further_development_model_params = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": prompt_dict["tot_further_development"]},
        {"role": "user", "content": "example['input'] + Thoughts"},
    ],
}

tot_evaluator_model_params = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": prompt_dict["tot_evaluator"]},
        {"role": "user", "content": "thought"},
    ],
}

tot_branch_selector_model_params = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": prompt_dict["tot_branch_selector"]},
        {"role": "user", "content": "sets of thoughts"},
    ],
}

tot_final_answer_model_params = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": prompt_dict["tot_final_answer_v2"]},
        {"role": "user", "content": "Problem and thoughts"},
    ],
}


def init_broken_branches(problem):
    input = problem["input"]
    result = {
        "input": input,
        "input_question": problem["input_question"],
        "input_text": problem["input_text"],
        "thoughts": {
            "prompt": "tot_generator",
            "input": input,
            "output": "",
            "thoughts": [],
        },
        "scores": [],
        "branches": [],
        "tot_answer": {"Yes": 0, "No": 0},
        "is_correct": 0,
        "re_run": 0,
    }
    completion = client.chat.completions.create(
        model=tot_generator_model_params["model"],
        messages=[
            tot_generator_model_params["messages"][0],
            {"role": "user", "content": input},
        ],
    )
    response = completion.choices[0].message.content
    thoughts = extract_thoughts(response)
    result["thoughts"]["output"] = response
    result["thoughts"]["thoughts"] = thoughts
    result["scores"] = []
    scores = []
    for thought in thoughts:
        tot_evaluator_query = f"""Problem: {input}
      Thought: {thought}
      """
        completion = client.chat.completions.create(
            model=tot_evaluator_model_params["model"],
            messages=[
                tot_evaluator_model_params["messages"][0],
                {"role": "user", "content": tot_evaluator_query},
            ],
        )
        score = completion.choices[0].message.content
        # print(thought)
        # print(score)
        result["scores"].append(
            {
                "prompt": "tot_evaluator",
                "input": tot_evaluator_query,
                "output": score,
                "score": extract_score(score),
            }
        )
        fully_developed_input = f"""Problem: {input}
      Thoughts: {thought}
      """
        if extract_score(score) < 0.8:
            dead_branch = True
        else:
            dead_branch = False
        avg_score = extract_score(score)
        result["branches"].append(
            {
                "fully_developed_input": fully_developed_input,
                "dead_branch": dead_branch,
                "avg_score": avg_score,
                "thoughts": [thought],
                "scores": [extract_score(score)],
                "nodes": [],
            }
        )
    return result
    # data['results'][idx] = copy.deepcopy(result)
    # if idx == 1:
    # Uncomment to stop the execution after the first 2 questions
    # break
    # pass


def further_develop_branches(problem, iteration_number):
    result = problem
    for iteration in range(iteration_number):
        print(f"Iteration {iteration+1}/{depth}")
        input = result["input"]
        for i, branch in enumerate(result["branches"]):

            if branch["dead_branch"] == True:
                continue

            thoughts_string = "\n".join(
                [f"{i+1}. {thought}" for i, thought in enumerate(branch["thoughts"])]
            )
            tot_further_development_query = f"""Problem: {input}
            Thoughts: {thoughts_string}
            """
            # print(tot_further_development_query)
            completion = client.chat.completions.create(
                model=tot_further_development_model_params["model"],
                messages=[
                    tot_further_development_model_params["messages"][0],
                    {"role": "user", "content": tot_further_development_query},
                ],
            )
            response = completion.choices[0].message.content
            # print(response)
            new_thoughts = extract_thoughts(response)
            # print(new_thoughts)
            for n, thought in enumerate(new_thoughts):
                # print(f"Processing thought {n+1}/{len(new_thoughts)}")
                tot_evaluator_query = f"""Problem: {input}
            Thought: {thought}
            """
                #          print(tot_evaluator_query)
                completion = client.chat.completions.create(
                    model=tot_evaluator_model_params["model"],
                    messages=[
                        tot_evaluator_model_params["messages"][0],
                        {"role": "user", "content": tot_evaluator_query},
                    ],
                )
                score_response = completion.choices[0].message.content
                score = extract_score(score_response)
                branch["nodes"].append(
                    {
                        "prompt": "tot_evaluator",
                        "input": tot_further_development_query,
                        "output": response,
                        "thoughts": new_thoughts,
                        "scores": [score],
                    }
                )
            branch["thoughts"] = branch["thoughts"] + new_thoughts
            branch["scores"] = branch["scores"] + [score]
            branch["avg_score"] = sum(branch["scores"]) / len(branch["scores"])
            branch_thoughts_string = "\n".join(
                [f"{i+1}. {thought}" for i, thought in enumerate(branch["thoughts"])]
            )
            fully_developed_input_string = f"""Problem: {input}
            Thoughts: {branch_thoughts_string}
            """
            branch["fully_developed_input"] = fully_developed_input_string
            for score in branch["scores"]:
                if score < 0.8:
                    branch["dead_branch"] = True
                    break
    return result


def branch_selector(problem):
    result = problem
    branch_map = {
        "A": 0,
        "B": 1,
        "C": 2,
        "D": 3,
        "E": 4,
        "F": 5,
        "G": 6,
        "H": 7,
        "I": 8,
        "J": 9,
    }
    branch_map_inv = {v: k for k, v in branch_map.items()}

    input = result["input"]
    thoughts_sets = []
    for branch_idx, branch in enumerate(result["branches"]):
        # print(f"Processing branch {i+1}/{len(result['branches'])}")
        if branch_idx == 1:
            pass

        if branch["dead_branch"] == True:
            continue

        thoughts_string = ";".join(
            [f"{thought}" for i, thought in enumerate(branch["thoughts"])]
        )
        thoughts_set_string = f"Set {branch_map_inv[branch_idx]}: {thoughts_string}"
        thoughts_sets.append(thoughts_set_string)

    thoughts_sets_string = "\n".join(thoughts_sets)
    tot_branch_selector_query = f"""Problem: {input}
    Sets of Thoughts:
    {thoughts_sets_string}
    """
    best_set = None
    output = None
    # print(tot_branch_selector_query)
    if len(thoughts_sets) == 1:
        best_set_match = re.search(r"^Set (A|B|C|D|E|F|G|H|I|J)", thoughts_sets[0])
        best_set = branch_map[best_set_match.group(1)]
        print(f"Only one set of thoughts, selecting set {best_set}")
    elif len(thoughts_sets) == 0:
        print("All branches are dead")
    else:
        completion = client.chat.completions.create(
            model=tot_branch_selector_model_params["model"],
            messages=[
                tot_branch_selector_model_params["messages"][0],
                {"role": "user", "content": tot_branch_selector_query},
            ],
        )
        response = completion.choices[0].message.content
        output = response
        # print(response)
        # Extract the best set number from the response
        best_set_match = re.search(
            r"best choice is set\s+(A|B|C|D|E|F|G|H|I|J)", response, re.IGNORECASE
        )
        if not best_set_match:
            best_set_match = re.search(
                r"best choice is\s+\*\*set\*\*\s+(A|B|C|D|E|F|G|H|I|J)",
                response,
                re.IGNORECASE,
            )
        if not best_set_match:
            best_set_match = re.search(
                r"best choice is\s+\*\*set\*\*\s+(A|B|C|D|E|F|G|H|I|J)",
                response,
                re.IGNORECASE,
            )
        if not best_set_match:
            best_set_match = re.search(
                r"best choice is\s+<set>\s+(A|B|C|D|E|F|G|H|I|J)",
                response,
                re.IGNORECASE,
            )

        if best_set_match:
            best_set = branch_map[best_set_match.group(1)]
            print(f"Best set selected: {best_set}")

    if best_set is None:
        print("Could not determine best set from response")
        # Update the result with the best branch

    result["selected_branch"] = best_set
    result["branch_selection"] = {
        "prompt": "tot_branch_selector",
        "input": tot_branch_selector_query,
        "output": output,
        "best_set": best_set,
    }
    return result


def final_answer(problem, example):
    result = problem
    if example["input"] != problem["input"]:
        print("Input mismatch")
        print(example["input"])
        print(result["input"])
        return result

    if result["selected_branch"] is None:
        print("No best set selected, skipping...")
        return result

    final_answer_query = (
        f"""{result['branches'][result['selected_branch']]['fully_developed_input']}"""
    )

    completion = client.chat.completions.create(
        model=tot_final_answer_model_params["model"],
        messages=[
            tot_final_answer_model_params["messages"][0],
            {"role": "user", "content": final_answer_query},
        ],
    )
    response = completion.choices[0].message.content
    response_parsed = re.findall(r"The answer is (Yes|No)\b", response, re.IGNORECASE)
    tot_answers = {"Yes": 0, "No": 0}

    for posible_answer in tot_answers:
        if posible_answer in response_parsed:
            tot_answers[posible_answer] = 1

    if len(response_parsed) == 1:
        score = example["target_scores"][response_parsed[0]]
    else:
        score = 0

    result["final_answer"] = {
        "prompt": "tot_final_answer",
        "input": final_answer_query,
        "output": response,
        "parsed_output": response_parsed,
        "is_correct": score,
    }

    result["is_correct"] = score
    result["tot_answer"] = tot_answers
    return result


def print_percentage_correct(data):
    # get results with an answer
    results_with_answer = []
    for result in data["results"]:
        if "final_answer" in result:
            if len(result["final_answer"]["parsed_output"]) == 1:
                results_with_answer.append(result)

    print(f"Number of results with an answer: {len(results_with_answer)}")

    correct_results = [
        result for result in results_with_answer if result["is_correct"] == 1
    ]
    print(f"Number of correct results: {len(correct_results)}")

    # print the percentage of correct results
    print(
        f"Percentage of correct results: {len(correct_results)/len(results_with_answer)}"
    )


def run_full_pipeline(data, original_data, broken_answers, depth: int = 3):
    broken_answers_input = [broken_answer["input"] for broken_answer in broken_answers]
    for idx, problem in enumerate(data["results"]):
        if problem["input"] not in broken_answers_input:
            continue
        print(f"Processing question {idx+1}/{len(data['results'])}")
        print(problem["input"])
        result = init_broken_branches(problem)
        result = further_develop_branches(result, depth)
        result = branch_selector(result)
        result = final_answer(result, original_data["examples"][idx])
        data["results"][idx] = copy.deepcopy(result)
    return data


def rerun_answers(file_path_data, file_path_original_data, depth: int = 3):
    original_data = load_dict_from_drive(file_path_original_data)
    while True:
        data = load_dict_from_drive(file_path_data)
        no_best_set_selected = [
            result for result in data["results"] if result["selected_branch"] is None
        ]
        print(
            f"Number of results without a best set selected: {len(no_best_set_selected)}"
        )
        if len(no_best_set_selected) == 0:
            print("No more broken branches, exiting...")
            break
        broken_answers = no_best_set_selected
        data = run_full_pipeline(data, original_data, broken_answers)
        save_dict_to_drive(data, file_path_data)
    print_percentage_correct(data)


def main():
    rerun_answers("./output/test.json", "../datasets/task_patched.json")
    data = load_dict_from_drive("./output/test.json")
    print_percentage_correct(data)

if __name__ == "__main__":
    main()
