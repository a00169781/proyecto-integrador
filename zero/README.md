# Zero-shot
This document contains the zero-shot prompt used to solve the causal judgement task from the [BigBench Causal Judgement dataset](https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/causal_judgement).

We used zero-shot method as a baseline to compare the results with our most advanced models.

## Strategy overview

We simply create a single prompt that will be used to solve the task. The prompt is designed to understand the problem, identify the question and provide a clear and concise answer.

The prompt is the following:

```
You are an AI language model specialized in determining causal relationships. When presented with a question about causality, analyze the information carefully and provide a clear, concise response. Your answer should:

Reasoning: Begin with a brief explanation of whether and how the cause leads to the effect.
Conclusion: End with "The answer is Yes." or "The answer is No." based on your analysis.
```

## Results
The performance of the zero-shot model around 64% correct.
