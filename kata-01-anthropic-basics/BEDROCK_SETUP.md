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

The script uses `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` (a cross-region inference profile for EU). If your key was issued for a different region, update `DEFAULT_MODEL` and `AWS_REGION` accordingly.

Common model IDs by region:

| Region | Model ID prefix |
|--------|-----------------|
| EU (eu-central-1) | `eu.anthropic.claude-...` |
| US (us-east-1) | `us.anthropic.claude-...` |
| AP (ap-southeast-1) | `ap.anthropic.claude-...` |

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
