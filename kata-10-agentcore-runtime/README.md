# Kata 10: AgentCore Runtime

## Objective

Wrap any Strands agent with `BedrockAgentCoreApp` to instantly create a production-ready HTTP server — with built-in health checks, JSON request/response handling, and the same interface as SageMaker inference endpoints. Test locally, then understand the path to deploying on AWS serverless infrastructure.

## Learning Goals

- Understand what AgentCore Runtime is and why it exists
- Use `BedrockAgentCoreApp` from `bedrock_agentcore.runtime`
- Register an agent handler with `@app.entrypoint`
- Test the `/ping` (health check) and `/invocations` (inference) endpoints
- Understand session isolation: each user session = dedicated isolated environment in production
- See the production deployment path: Docker → ECR → `create_agent_runtime()`

## Prerequisites

- Completed Kata 02 (Strands Introduction)
- AWS account with Bedrock enabled
- `AWS_BEARER_TOKEN_BEDROCK` and `AWS_REGION` environment variables set

```bash
pip install 'strands-agents[bedrock]' bedrock-agentcore boto3 python-dotenv
export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
export AWS_REGION=us-east-1
```

## Time Estimate

20–30 minutes

## Difficulty

⭐⭐ (Intermediate)

---

## Background

### What is AgentCore Runtime?

AgentCore Runtime turns any Python agent into a containerized microservice. In production, it:

- Runs your agent in an isolated AWS microVM per user session
- Provides SageMaker-compatible `/ping` and `/invocations` HTTP endpoints
- Handles concurrency, session routing, and scaling automatically
- Integrates with IAM for authentication

Locally, `app.run()` starts a lightweight HTTP server on port 8080 so you can develop and test before deploying.

### SageMaker Interface

AgentCore Runtime uses the same HTTP contract as SageMaker real-time inference:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ping` | GET | Health check — returns `{"status": "healthy"}` |
| `/invocations` | POST | Run the agent — body is JSON, response is JSON |

This means any tool that can call a SageMaker endpoint can also call your AgentCore agent.

### Session Isolation

In production, each unique `session_id` in the payload routes to its own isolated microVM. This means:
- Conversation history is scoped per session
- One user's agent state cannot affect another's
- Sessions can run concurrently without conflicts

### Production Deployment Path

```
Local testing (kata-10)
    ↓ docker build + docker push → ECR
    ↓ bedrock-agentcore create_agent_runtime()
    ↓ Invoke via agentcore endpoint URL
Serverless production agent
```

---

## Level 1: Challenge

Build a Python script that:

1. Imports `BedrockAgentCoreApp` and creates an app instance
2. Creates a Strands `Agent` with a `BedrockModel` and a system prompt
3. Defines an `invoke(payload)` function decorated with `@app.entrypoint`
4. Extracts `prompt` and `session_id` from the payload, calls the agent, returns a response dict
5. Starts the server with `app.run()`
6. Tests both `/ping` and `/invocations` endpoints with `curl`

### Success Criteria

- [ ] Server starts on `http://localhost:8080`
- [ ] `GET /ping` returns `{"status": "healthy"}` (HTTP 200)
- [ ] `POST /invocations` with `{"prompt": "..."}` returns a JSON response from the agent
- [ ] Multiple invocations work correctly (no state corruption between calls)

---

## Level 2: Step-by-Step Guide

### Step 1: Import and Initialize

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models.bedrock import BedrockModel

app = BedrockAgentCoreApp()
```

### Step 2: Create Your Agent

```python
agent = Agent(
    model=BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=1024),
    system_prompt="You are a helpful assistant specializing in AWS services."
)
```

### Step 3: Register the Entrypoint

```python
@app.entrypoint
def invoke(payload: dict) -> dict:
    """Handle agent invocation requests from AgentCore Runtime."""
    prompt = payload.get("prompt", "Hello!")
    session_id = payload.get("session_id", "local")

    result = agent(prompt)
    return {
        "response": str(result),
        "session_id": session_id,
    }
```

### Step 4: Start the Server

```python
if __name__ == "__main__":
    app.run()  # Starts on http://localhost:8080
```

### Step 5: Test with curl

```bash
# Health check
curl http://localhost:8080/ping

# Inference
curl -X POST http://localhost:8080/invocations \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "What is AWS AgentCore?", "session_id": "test-001"}'

# Another call with different session
curl -X POST http://localhost:8080/invocations \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "Explain Bedrock Knowledge Bases in 2 sentences.", "session_id": "alice"}'
```

---

## Running the Solution

```bash
# Terminal 1: start the server
python solution.py

# Terminal 2: test it
curl http://localhost:8080/ping
curl -X POST http://localhost:8080/invocations \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "What is AWS AgentCore?"}'
```

Expected output (Terminal 1):
```
Kata 10: AgentCore Runtime - Solution
AgentCore Runtime starting on http://localhost:8080
[test-001] User: What is AWS AgentCore?
[test-001] Agent: AWS AgentCore is a managed service that...
```

Expected response (Terminal 2):
```json
{
  "response": "AWS AgentCore is a managed service that ...",
  "session_id": "test-001"
}
```

---

## Extension Challenges

1. **Add tools**: Attach a `@tool` (like the weather tool from kata-03) to the agent and verify it works via the HTTP endpoint
2. **Streaming**: Explore the streaming response option in AgentCore Runtime
3. **Authentication**: Add a simple API key check inside the `invoke` function before processing
4. **Multi-agent routing**: Use `payload.get("agent_type")` to route to different specialized agents

---

## Key Concepts

### Why Not Just Use Flask/FastAPI?

You could wrap an agent with Flask. AgentCore Runtime adds:
- **Standardized interface** — same contract as SageMaker (tools/CI/CD work unchanged)
- **Session management** — built-in per-session isolation in production
- **AWS integration** — IAM auth, CloudWatch metrics, VPC networking out of the box
- **Deployment automation** — `create_agent_runtime()` handles container orchestration

### @app.entrypoint vs @app.route

AgentCore Runtime uses a single entrypoint model (one handler for all invocations), not a router. This keeps the interface simple and consistent with how production AgentCore deployments work.

---

## Resources

- [AgentCore Runtime Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html)
- [bedrock-agentcore Python SDK](https://pypi.org/project/bedrock-agentcore/)
- [SageMaker Inference Interface](https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html)
