# Kata 11: AgentCore Code Interpreter

## Objective

Add AgentCore's built-in Code Interpreter as a tool to a Strands agent. Instead of writing unsafe local `eval()` calls or predefined `@tool` functions, the agent writes arbitrary Python code and executes it in a secure, sandboxed AWS microVM. The agent autonomously decides when to write code vs. answer from knowledge.

## Learning Goals

- Import and initialize `AgentCoreCodeInterpreter` from `strands_tools`
- Attach `code_interpreter_tool.code_interpreter` as a Strands tool
- Write a system prompt that guides the LLM to use code for computation
- Understand how the LLM decides when to write and run code
- Compare sandboxed cloud execution vs. local `@tool` functions (kata-03)
- Recognize the security benefits of isolated code execution

## Prerequisites

- Completed Kata 03 (Custom Tools) — understand the `@tool` pattern
- AWS account with Bedrock + AgentCore enabled
- `AWS_BEARER_TOKEN_BEDROCK` and `AWS_REGION` environment variables set

```bash
pip install 'strands-agents[bedrock]' strands-agents-tools bedrock-agentcore boto3 python-dotenv
export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
export AWS_REGION=us-east-1
```

## Time Estimate

20–30 minutes

## Difficulty

⭐⭐ (Intermediate)

---

## Background

### The Problem with Local Code Execution

In kata-03, you used `@tool` functions — predefined Python functions the agent can call. That works well for known operations, but what about arbitrary computations?

Options:
- **`eval()`** — dangerous, allows arbitrary code injection
- **`@tool` wrappers** — safe but must be pre-written for every operation
- **AgentCore Code Interpreter** — the LLM writes code, AWS runs it in isolation

### How AgentCore Code Interpreter Works

```
User prompt
    ↓
Strands Agent (LLM)
    ↓ decides: "I should write Python code for this"
    ↓ generates code
    ↓ calls code_interpreter tool
AgentCore Code Interpreter
    ↓ sends code to isolated AWS microVM
    ↓ executes in sandboxed Python environment
    ↓ returns stdout/result
Strands Agent
    ↓ incorporates result into response
Final answer (with code + output shown)
```

### Security Model

The code runs in a **completely isolated microVM** on AWS:
- No access to your local filesystem, environment variables, or network
- Each invocation gets a fresh, clean environment
- Execution time and memory are capped
- Results are returned as text output

### Kata-03 vs Kata-12: Tool Comparison

| Aspect | Kata-03 `@tool` | Kata-12 Code Interpreter |
|--------|----------------|-------------------------|
| Code author | You (pre-written) | The LLM (runtime) |
| Operations | Fixed set | Arbitrary Python |
| Execution | Local Python | AWS sandboxed microVM |
| Security | Your responsibility | AWS-managed isolation |
| Flexibility | Limited | Unlimited |
| Setup | `@tool` decorator | `AgentCoreCodeInterpreter` |

---

## Level 1: Challenge

Build a Python script that:

1. Imports `AgentCoreCodeInterpreter` and creates an instance with the correct region
2. Creates a Strands agent with the code interpreter tool
3. Writes a system prompt instructing the agent to always write code for computations
4. Runs 3 different prompts:
   - A math problem (Fibonacci, factorials, prime numbers, etc.)
   - A statistics problem (distributions, percentiles, correlation, etc.)
   - An algorithm challenge (sorting, searching, dynamic programming, etc.)
5. Verifies that responses include actual Python code + execution output

### Success Criteria

- [ ] Agent output includes Python code blocks (not just text estimates)
- [ ] Agent output includes actual execution results from the sandbox
- [ ] All 3 problem types produce code-verified answers
- [ ] The agent uses the code interpreter autonomously without manual prompting

---

## Level 2: Step-by-Step Guide

### Step 1: Initialize the Code Interpreter

```python
from strands_tools.code_interpreter import AgentCoreCodeInterpreter

code_interpreter_tool = AgentCoreCodeInterpreter(region=AWS_REGION)
```

### Step 2: Build the Agent

```python
from strands import Agent
from strands.models.bedrock import BedrockModel

agent = Agent(
    model=BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=4096),
    tools=[code_interpreter_tool.code_interpreter],
    system_prompt="""You are a data science assistant. When asked about calculations,
    statistics, or programming problems, always write and execute Python code to
    verify your answers. Show both the code and the results."""
)
```

> **Why `max_tokens=4096`?** Code + explanation takes more tokens than text-only responses. Set it high enough to avoid truncation.

### Step 3: Run Computations

```python
# Math: the agent writes Python to compute Fibonacci
response = agent("Calculate the first 15 Fibonacci numbers and find their sum.")
print(response)

# Statistics: the agent generates random data and computes statistics
response = agent(
    "Generate 1000 random numbers from a normal distribution (mean=5, std=2) "
    "and compute: mean, std dev, min, max, and 95th percentile."
)
print(response)

# Algorithms: the agent implements and runs bubble sort
response = agent(
    "Implement the bubble sort algorithm and sort this list: "
    "[64, 34, 25, 12, 22, 11, 90]. Count the number of swaps."
)
print(response)
```

---

## Running the Solution

```bash
python solution.py
```

Expected output for each demo includes:
1. The Python code the agent wrote
2. The output from executing that code in the AWS sandbox
3. A natural language explanation incorporating the results

Example (truncated):
```
Demo 1: Mathematics
User: Calculate the first 15 Fibonacci numbers and find their sum.
Agent: I'll calculate this by running Python code.

```python
def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[-1] + fib[-2])
    return fib[:n]

sequence = fibonacci(15)
print("Sequence:", sequence)
print("Sum:", sum(sequence))
```

Output:
Sequence: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
Sum: 986

The first 15 Fibonacci numbers sum to **986**.
```

---

## Extension Challenges

1. **Data visualization**: Ask the agent to create a histogram or scatter plot (returns base64 image)
2. **File processing**: Pass CSV data in the prompt and ask the agent to analyze it
3. **Comparison**: Ask the same math question to an agent *without* the code interpreter — compare answer quality
4. **Custom libraries**: Check which Python libraries are available in the sandbox (pandas, numpy, scipy)

---

## Key Concepts

### Why the System Prompt Matters

Without a strong system prompt, the LLM may answer math questions from knowledge (e.g., stating Fibonacci numbers from memory) rather than running code. The system prompt "always write and execute code to verify" is essential to force code execution behavior.

### The Agent's Decision Process

When the agent sees a math question, it:
1. Recognizes it could answer from knowledge
2. But the system prompt says "always run code"
3. So it generates a code block
4. Calls the `code_interpreter` tool with that code
5. Gets real output back
6. Incorporates the verified result into its response

This is tool use in action — the same mechanism as kata-03, but the "tool" is a general-purpose Python executor rather than a predefined function.

---

## Resources

- [AgentCore Code Interpreter Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter.html)
- [strands-agents-tools](https://pypi.org/project/strands-agents-tools/)
- [Strands Tool Use](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/)
