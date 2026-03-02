"""
Kata 12: AgentCore Code Interpreter - Solution

Add AgentCore's sandboxed Code Interpreter as a tool to a Strands agent.
The agent writes and executes Python code in a secure AWS microVM — no unsafe
eval(), no local execution risk.

Prerequisites:
    pip install 'strands-agents[bedrock]' strands-agents-tools bedrock-agentcore boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1   (must match the region your key was created in)

    To use eu-central-1: set AWS_REGION=eu-central-1 and change DEFAULT_MODEL
    prefix from "us." to "eu.".
"""

import os

from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands_tools.code_interpreter import AgentCoreCodeInterpreter

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


def build_agent() -> Agent:
    """Create a Strands data-science agent with the AgentCore Code Interpreter."""
    code_interpreter_tool = AgentCoreCodeInterpreter(region=AWS_REGION)

    model = BedrockModel(
        model_id=DEFAULT_MODEL,
        region_name=AWS_REGION,
        max_tokens=4096,
    )

    agent = Agent(
        model=model,
        tools=[code_interpreter_tool.code_interpreter],
        system_prompt=(
            "You are a data science and programming assistant. "
            "When asked about calculations, statistics, algorithms, or programming problems, "
            "always write and execute Python code to verify your answers. "
            "Show the code you write and include the execution results in your response. "
            "Never give a numerical answer without running code to confirm it."
        )
    )
    return agent


def main():
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 12: AgentCore Code Interpreter - Solution"))
    print(Colors.header(f" Region: {AWS_REGION}  |  Model: {DEFAULT_MODEL}"))
    print(Colors.header("=" * 70))
    print(Colors.stats("\nCode runs in an isolated AWS sandbox — no local execution.\n"))

    try:
        agent = build_agent()

        # Demo 1: Mathematical computation
        print(Colors.header("Demo 1: Mathematics"))
        print("-" * 40)
        prompt1 = (
            "Calculate the first 15 Fibonacci numbers and find their sum. "
            "Show the sequence and the total."
        )
        print(Colors.prompt(f"User: {prompt1}"))
        response1 = agent(prompt1)
        print(Colors.response(f"Agent: {response1}"))

        # Demo 2: Statistical analysis
        print(Colors.header("\nDemo 2: Statistical Analysis"))
        print("-" * 40)
        prompt2 = (
            "Generate 1000 random numbers from a normal distribution (mean=5, std=2). "
            "Compute: mean, standard deviation, minimum, maximum, and 95th percentile. "
            "Verify the results match the expected distribution."
        )
        print(Colors.prompt(f"User: {prompt2}"))
        response2 = agent(prompt2)
        print(Colors.response(f"Agent: {response2}"))

        # Demo 3: Algorithm implementation
        print(Colors.header("\nDemo 3: Algorithm Implementation"))
        print("-" * 40)
        prompt3 = (
            "Implement the bubble sort algorithm and sort this list: [64, 34, 25, 12, 22, 11, 90]. "
            "Show the step-by-step sorting process and count how many swaps were made."
        )
        print(Colors.prompt(f"User: {prompt3}"))
        response3 = agent(prompt3)
        print(Colors.response(f"Agent: {response3}"))

        # Demo 4: Data analysis
        print(Colors.header("\nDemo 4: Data Analysis"))
        print("-" * 40)
        prompt4 = (
            "Create a dataset of 12 months of fictional IoT sensor readings: "
            "temperature ranging 15-35°C with seasonal variation. "
            "Find the month with highest average, the month with lowest, "
            "and compute the year-over-year trend (assume readings are for 2024)."
        )
        print(Colors.prompt(f"User: {prompt4}"))
        response4 = agent(prompt4)
        print(Colors.response(f"Agent: {response4}"))

    except NoCredentialsError:
        print("\nError: AWS credentials not configured.")
        print("Set AWS_BEARER_TOKEN_BEDROCK and AWS_REGION environment variables.")

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 12 Complete!"))
    print(Colors.header("=" * 70))
    print(Colors.stats("\nKey insight: The agent wrote and ran real Python code in a sandboxed"))
    print(Colors.stats("AWS microVM. Compare with kata-03's local @tool approach."))


if __name__ == "__main__":
    main()
