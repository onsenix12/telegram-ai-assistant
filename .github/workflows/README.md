# GitHub Actions Workflows

This directory contains GitHub Actions workflow files for Continuous Integration and Deployment of the Telegram AI Assistant.

## Workflow Status

| Workflow | Status |
|----------|--------|
| CI/CD Pipeline | ![CI/CD Pipeline Status](https://github.com/yourusername/telegram-ai-assistant/actions/workflows/ci-cd.yml/badge.svg) |

## Available Workflows

### CI/CD Pipeline (`ci-cd.yml`)

This workflow runs when code is pushed to the main branch or when a pull request is created.

Steps:
1. **Test**: Runs the test suite
2. **Build**: Builds the Docker image
3. **Push**: Pushes the Docker image to Docker Hub (only on main branch)
4. **Deploy**: Deploys the application to the server (disabled by default)

## Setting Up Required Secrets

To use these workflows, you need to set up the following secrets in your GitHub repository:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `ANTHROPIC_API_KEY`: Your Claude AI API key
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: A Docker Hub access token with push privileges
- `SERVER_HOST`: Your deployment server's IP or hostname
- `SERVER_USERNAME`: SSH username for the deployment server
- `SERVER_SSH_KEY`: Private SSH key for server access
- `SERVER_PORT`: SSH port (usually 22)