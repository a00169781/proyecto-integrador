# Chain of Thought
This document contains the Chain of Thought prompt used to solve the causal judgement task from the [BigBench Causal Judgement dataset](https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/causal_judgement).

We used Chain of Thought method to solve the task. Chain of Thought is a technique that involves breaking down a problem into smaller steps and reasoning through each step to arrive at a solution. Chain of Thought increases the performance of LLMs by allowing them to reason through the problem and provide more accurate and detailed answers.

## Strategy overview

We provide a prompt where the LLM is asked to reason through the problem and provide a detailed answer.

The prompt is the following:

```
You are an AI language model tasked with answering questions about causation from the perspective of a typical person. When presented with a causation question, please follow these steps:

1. **Understand the Question:**
   - Identify the proposed cause and effect in the question.
   - Determine what is being asked and any common assumptions involved.

2. **Typical Person's Reasoning:**
   - Consider how an average person might perceive the relationship between the cause and effect.
   - Use everyday knowledge, beliefs, and intuitive reasoning that a typical person might apply.
   - Provide a brief explanation reflecting this common-sense reasoning.

3. **Determine the Primary and Secondary Causes:**
   - Identify the primary cause and any secondary causes that might be involved.
   - Consider the relative strength of the relationship between the cause and effect.

4. **Conclusion:**
   - Summarize your reasoning and state whether the typical person would believe the cause leads to the effect.
   - End your response with "The answer is Yes." or "The answer is No." based on this perspective.
```


## Results
The performance of the Chain of Thought model around 67% correct.
