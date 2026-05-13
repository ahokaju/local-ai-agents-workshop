"""
Kata 11: AgentCore Code Interpreter - Starter Template

Complete the TODOs to add AgentCore's sandboxed Code Interpreter to a
Strands agent. The agent will write and execute Python code in a secure
AWS microVM — safe, isolated, no local execution risk.

Prerequisites:
    pip install 'strands-agents[bedrock]' strands-agents-tools bedrock-agentcore boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1   (must match the region your key was created in)
"""

import os

from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError
# TODO 1: Import AgentCoreCodeInterpreter from strands_tools.code_interpreter
# from strands_tools.code_interpreter import AgentCoreCodeInterpreter
# TODO 1 (cont): Import Agent from strands and BedrockModel from strands.models.bedrock
# from strands import Agent
# from strands.models.bedrock import BedrockModel

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for pretty terminal output."""
    HEADER = '\033[96m'
    PROMPT = '\033[93m'
    RESPONSE = '\033[92m'
    STATS = '\033[95m'
    TODO = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def header(cls, text):
        return f"{cls.BOLD}{cls.HEADER}{text}{cls.RESET}"

    @classmethod
    def prompt(cls, text):
        return f"{cls.PROMPT}{text}{cls.RESET}"

    @classmethod
    def response(cls, text):
        return f"{cls.RESPONSE}{text}{cls.RESET}"

    @classmethod
    def stats(cls, text):
        return f"{cls.STATS}{text}{cls.RESET}"

    @classmethod
    def todo(cls, text):
        return f"{cls.TODO}{text}{cls.RESET}"


def build_agent():
    """Create a Strands data-science agent with the AgentCore Code Interpreter.

    Steps:
        1. Instantiate AgentCoreCodeInterpreter(region=AWS_REGION)
        2. Create BedrockModel with DEFAULT_MODEL, max_tokens=4096
        3. Create Agent with model, tools=[code_interpreter_tool.code_interpreter],
           and a system prompt instructing it to always run code for computations
    """
    # TODO 2: Instantiate AgentCoreCodeInterpreter
    # code_interpreter_tool = AgentCoreCodeInterpreter(region=AWS_REGION)

    # TODO 3: Create BedrockModel
    # model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=4096)

    # TODO 4: Create Agent with the code interpreter tool and a strong system prompt
    # agent = Agent(
    #     model=model,
    #     tools=[code_interpreter_tool.code_interpreter],
    #     system_prompt=(
    #         "You are a data science assistant. Always write and execute Python code "
    #         "to verify calculations. Show the code and the execution results."
    #     )
    # )
    # return agent

    print(Colors.todo("TODO 2-4: Implement build_agent()"))
    return None


def main():
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 11: AgentCore Code Interpreter"))
    print(Colors.header(f" Region: {AWS_REGION}  |  Model: {DEFAULT_MODEL}"))
    print(Colors.header("=" * 70))
    print(Colors.stats("\nCode runs in an isolated AWS sandbox — no local execution.\n"))

    try:
        agent = build_agent()

        if not agent:
            print(Colors.todo("\nComplete TODOs 2-4 to enable the agent."))
            return

        # TODO 5a: Demo 1 — ask the agent to compute the first 15 Fibonacci numbers and their sum
        print(Colors.header("Demo 1: Mathematics"))
        print("-" * 40)
        prompt1 = "Calculate the first 15 Fibonacci numbers and find their sum."
        print(Colors.prompt(f"User: {prompt1}"))
        # response1 = agent(prompt1)
        # print(Colors.response(f"Agent: {response1}"))
        print(Colors.todo("TODO 5a: Call agent(prompt1) and print the response"))

        # TODO 5b: Demo 2 — statistical analysis on random normal distribution
        print(Colors.header("\nDemo 2: Statistical Analysis"))
        print("-" * 40)
        prompt2 = (
            "Generate 1000 random numbers from a normal distribution (mean=5, std=2) "
            "and compute: mean, std dev, min, max, and 95th percentile."
        )
        print(Colors.prompt(f"User: {prompt2}"))
        # response2 = agent(prompt2)
        # print(Colors.response(f"Agent: {response2}"))
        print(Colors.todo("TODO 5b: Call agent(prompt2) and print the response"))

        # TODO 5c: Demo 3 — implement and run bubble sort
        print(Colors.header("\nDemo 3: Algorithm Implementation"))
        print("-" * 40)
        prompt3 = (
            "Implement the bubble sort algorithm and sort this list: "
            "[64, 34, 25, 12, 22, 11, 90]. Count the number of swaps."
        )
        print(Colors.prompt(f"User: {prompt3}"))
        # response3 = agent(prompt3)
        # print(Colors.response(f"Agent: {response3}"))
        print(Colors.todo("TODO 5c: Call agent(prompt3) and print the response"))

    except NoCredentialsError:
        print("\nError: AWS credentials not configured.")
        print("Set AWS_BEARER_TOKEN_BEDROCK and AWS_REGION environment variables.")

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 11 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
