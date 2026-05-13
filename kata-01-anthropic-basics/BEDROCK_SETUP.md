# AWS Bedrock Setup for Kata 01

This guide explains how to configure and run `solution_bedrock.py`, which uses AWS Bedrock as the inference provider instead of the direct Anthropic API.

## Prerequisites

- Python 3.12
- An AWS account with Bedrock access enabled
- A Bedrock API key (`AWS_BEARER_TOKEN_BEDROCK`)

## Install Dependencies

```bash
pip install boto3 python-dotenv
```

## Environment Variables

Set the following two variables before running the script:

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_BEARER_TOKEN_BEDROCK` | Your Bedrock API key | `aws-bedrock-xxx...` |
| `AWS_REGION` | AWS region where the key was created | `eu-central-1` |

`boto3` picks up both variables automatically — no additional AWS credential files or IAM configuration are needed.

### macOS / Linux

```bash
export AWS_BEARER_TOKEN_BEDROCK="your-bedrock-api-key"
export AWS_REGION="eu-central-1"
```

### Windows CMD

```cmd
set AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
set AWS_REGION=eu-central-1
```

### Windows PowerShell

```powershell
$env:AWS_BEARER_TOKEN_BEDROCK="your-bedrock-api-key"
$env:AWS_REGION="eu-central-1"
```

### .env file (alternative)

Create a `.env` file in the `kata-01-anthropic-basics/` directory:

```
AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
AWS_REGION=eu-central-1
```

The script calls `load_dotenv()` automatically, so the file is loaded at startup.

## Run the Script

```bash
cd kata-01-anthropic-basics
python solution_bedrock.py
```

## Model Used

The scripts default to EU cross-region inference profiles (`eu-central-1`). If your Bedrock key was issued for a different region, you must update both `AWS_REGION` and `DEFAULT_MODEL` to match.

### Model IDs by Region

Cross-region inference profile IDs follow the pattern `<region-prefix>.anthropic.claude-<model>`:

| Model | EU (eu-central-1) | US (us-east-1) | AP (ap-southeast-1) |
|-------|-------------------|----------------|---------------------|
| Claude Sonnet 4.5 | `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | `ap.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| Claude Haiku 4.5 | `eu.anthropic.claude-haiku-4-5-20251001-v1:0` | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | `ap.anthropic.claude-haiku-4-5-20251001-v1:0` |
| Claude Haiku 3 | `eu.anthropic.claude-3-haiku-20240307-v1:0` | `us.anthropic.claude-3-haiku-20240307-v1:0` | `ap.anthropic.claude-3-haiku-20240307-v1:0` |

> **Important**: The region prefix in the model ID must match `AWS_REGION`. A key issued for `us-east-1` will not work with `eu.anthropic.*` model IDs and vice versa.

---

## Using us-east-1

If your Bedrock key was created in `us-east-1`, set the following environment variables:

### macOS / Linux

```bash
export AWS_BEARER_TOKEN_BEDROCK="your-bedrock-api-key"
export AWS_REGION="us-east-1"
```

### Windows CMD

```cmd
set AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
set AWS_REGION=us-east-1
```

### Windows PowerShell

```powershell
$env:AWS_BEARER_TOKEN_BEDROCK="your-bedrock-api-key"
$env:AWS_REGION="us-east-1"
```

### .env file

```
AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
AWS_REGION=us-east-1
```

### Update DEFAULT_MODEL in each script

Every `solution_bedrock.py` has a `DEFAULT_MODEL` constant at the top. When using `us-east-1`, change the `eu.` prefix to `us.`:

```python
# EU (default)
DEFAULT_MODEL = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"

# US — change to this when using us-east-1
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
```

Files to update:

| File | Current default model |
|------|-----------------------|
| `kata-01-anthropic-basics/solution_bedrock.py` | `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| `kata-02-strands-intro/solution_bedrock.py` | `anthropic.claude-3-haiku-20240307-v1:0` (no prefix — already region-agnostic) |
| `kata-03-strands-tools/solution_bedrock.py` | `anthropic.claude-3-haiku-20240307-v1:0` (no prefix — already region-agnostic) |
| `kata-03b-browser-tools/solution_bedrock.py` | `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| `kata-04-local-rag/solution_bedrock.py` | `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| `kata-05-rag-agent/solution_bedrock.py` | `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| `kata-06-atlassian-agent/solution_bedrock.py` | `eu.anthropic.claude-haiku-4-5-20251001-v1:0` |
| `kata-07-github-pr-agent/solution_bedrock.py` | `eu.anthropic.claude-haiku-4-5-20251001-v1:0` |

> **Tip**: `anthropic.claude-3-haiku-20240307-v1:0` (without a region prefix) is a base model ID that can be used directly in any region without a cross-region inference profile.

## Troubleshooting

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `NoCredentialsError` | `AWS_BEARER_TOKEN_BEDROCK` not set | Export the variable or add it to `.env` |
| `AccessDeniedException` | Wrong key or model not enabled | Verify the key in the AWS console; enable the model under Bedrock > Model access |
| `ThrottlingException` | Request rate exceeded | Wait a moment and retry |
| Region mismatch | Key created in a different region | Set `AWS_REGION` to match the region where the key was issued |

## Difference from solution.py

`solution_bedrock.py` mirrors `solution.py` in behaviour but uses the `boto3` Bedrock runtime client instead of the `anthropic` SDK:

| Aspect | solution.py | solution_bedrock.py |
|--------|-------------|---------------------|
| SDK | `anthropic` | `boto3` |
| Auth variable | `ANTHROPIC_API_KEY` | `AWS_BEARER_TOKEN_BEDROCK` + `AWS_REGION` |
| API method | `client.messages.create()` | `client.converse()` |
| Streaming | `client.messages.stream()` | `client.converse_stream()` |
| Usage keys | `response.usage.input_tokens` | `response["usage"]["inputTokens"]` |
