# Data structure used for ToT prompting
Tot method requieres multiple calls to the LLM to generate the final answer. Ideally, this process could be perfomed in a single script,
however, for debugging purposes, it is useful to record each step of the process.

The data structure used for this purpose is a jsonl file with the following format:

```json
{
    "name": "Tree of Thoughts analysis",
    "description": "This file contains the responses of the LLM to the ToT prompt for a given task.",
    "dataset" : "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/causal_judgement",
    "max_depth": 3,
    "prompts_templates": [
        {
            "name": "tot_generator",
            "prompt": "ToT_generator.txt"
        },
        {
            "name": "tot_evaluator",
            "prompt": "ToT_evaluator.txt"
        },
        {
            "name": "tot_further_development",
            "prompt": "ToT_further_development.txt"
        },
        {
            "name": "tot_selector",
            "prompt": "ToT_selector.txt"
        },
        {
            "name": "tot_final_answer",
            "prompt": "ToT_final_answer.txt"
        }
    ],
    "results": [
        {
            "input": "Original input from the dataset",
            "input_question": "The question extracted from the input",
            "input_text": "Input minus the question",
            "thoughts": {
                "prompt": "tot_generator",
                "input": "Input of the LLM for the ToT Generator prompt",
                "output": "Output of the LLM for the ToT Generator prompt",
                "thoughts": ["thought_1", "thought_2", "thought_3", "thought_4", "thought_5"],
                "scores": [
                    {
                        "prompt": "tot_evaluator",
                        "input": "thought_1",
                        "output": "Output of the LLM for the ToT Evaluator prompt",
                        "score": "Score of the thought"
                    }
                ]
            },
            "branches": [
                {
                    "fully_developed_input": "Original input + all thoughts",
                    "dead_branch": "True if branch was has broken thoughts",
                    "avg_score": "Average score of the thoughts",
                    "thoughts": ["thought_1"],
                    "scores": [
                        {
                            "prompt": "tot_evaluator",
                            "input": "last output",
                            "output": "Output of the LLM for the ToT Evaluator prompt",
                            "score": "Score of the thought"
                        }
                    ],
                    "nodes": [
                        {
                            "prompt": "tot_further_development",
                            "input": "intput + thought_1",
                            "output": "Output of the LLM for the ToT Evaluator prompt",
                            "thoughts": ["thought_1"],
                            "scores": [
                                {
                                    "prompt": "tot_evaluator",
                                    "input": "last output",
                                    "output": "Output of the LLM for the ToT Evaluator prompt",
                                    "score": "Score of the thought"
                                }
                            ],
                            "nodes": [
                                {
                                    "prompt": "tot_further_development",
                                    "input": "last output",
                                    "output": "Output of the LLM for the ToT Further Development prompt",
                                    "thoughts": ["thought_1"],
                                    "scores": [
                                        {
                                            "prompt": "tot_evaluator",
                                            "input": "last output",
                                            "output": "Output of the LLM for the ToT Evaluator prompt",
                                            "score": "Score of the thought"
                                        }
                                    ]
                                }
                            ]
                        }   
                    ]
                }
            ]
        }
    ]
}
```


