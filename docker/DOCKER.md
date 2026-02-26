# Docker Quick Start — Local AI Agents Workshop

No Python installation needed. Just Docker.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Git (to clone the repo)

## Getting Started

```bash
# 1. Clone the repo and enter the docker directory
git clone <repo-url>
cd local-ai-agents-workshop/docker

# 2. Add your API key
cp .env.example .env
# Open .env and set ANTHROPIC_API_KEY=sk-ant-...

# 3. Pull and start the base image (~130 MB — covers katas 01-03, 06-08)
docker compose up -d

# 4. Enter the container
docker exec -it workshop bash

# 5. Run a kata
python kata-01-anthropic-basics/solution.py
```

## Image Variants

| Image | Size | Covers |
|-------|------|--------|
| `base` (default) | ~130 MB | katas 01-03, 06-08 |
| `full` | ~880 MB | all katas, including 03b (browser) and 04-05 (RAG) |

Switch to the full image when you reach kata-04 or kata-03b:

```bash
# From the docker/ directory:
WORKSHOP_IMAGE=full docker compose up -d
docker exec -it workshop bash
```

The full image has the HuggingFace embedding model pre-downloaded, so kata-04/05
work without any first-run download delay.

## Kata-07: MCP Server (two terminals needed)

Kata-07 runs a local MCP server alongside the agent. Open two terminal windows:

```bash
# Terminal 1 — start the MCP server inside the container
docker exec -it workshop bash
python kata-07-atlassian-mcp/mcp_server.py

# Terminal 2 — run the agent
docker exec -it workshop bash
python kata-07-atlassian-mcp/solution.py
```

Port 8000 is already mapped to your host (`localhost:8000`).

## Stopping the Container

```bash
docker compose down
```

Data written to `chroma_db/`, `storage/`, and `screenshots/` is preserved in
Docker named volumes across container restarts.

## Building Locally (optional)

If you prefer to build the images yourself instead of pulling from the registry:

```bash
# From the repo root:
docker build -f docker/Dockerfile.base . -t workshop:base
docker build -f docker/Dockerfile.full . -t workshop:full
```

Then update `docker-compose.yml` to use `image: workshop:base` (or `workshop:full`).

## Troubleshooting

**Container exits immediately:** Make sure you used `docker compose up -d` (detached
mode). The container needs `stdin_open: true` and `tty: true` to stay alive.

**API key not found:** Confirm `.env` exists in the `docker/` directory (not the repo
root) and contains `ANTHROPIC_API_KEY=sk-ant-...` with no surrounding quotes.

**Port 8000 already in use:** Stop whatever is using port 8000 on your host, or edit
`docker-compose.yml` to map a different host port (e.g., `"8001:8000"`).
