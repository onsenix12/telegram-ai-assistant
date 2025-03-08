# SMU Master's Program AI Learning Assistant

A Telegram bot that assists SMU Master's Program students with course information, learning materials, and answering complex questions about their studies.

![CI/CD Pipeline](https://github.com/yourusername/telegram-ai-assistant/actions/workflows/ci-cd.yml/badge.svg)

## Features

- Provides information about SMU Master's Program courses (IS621-IS625)
- Answers questions about assignments, projects, and exams
- Recommends learning materials and resources
- Handles complex, multi-part questions using Claude AI
- Maintains conversation context for natural dialogue

## Setup

### Local Development

1. **Install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   Create a `.env` file in the project root with:
   ```
   TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   ANTHROPIC_API_KEY="your_claude_api_key"
   ```

3. **Run the bot**:
   ```bash
   python run_bot.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

2. **Check logs**:
   ```bash
   docker-compose logs -f bot
   ```

## Testing

- Run basic component tests:
  ```bash
  python test_bot.py
  ```

- Test the multi-part question handler with Claude:
  ```bash
  python test_multi_part.py
  ```

- Test Claude API directly:
  ```bash
  python test_claude_api.py
  ```

- Run all tests with pytest:
  ```bash
  pytest tests/
  ```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

1. **Test**: Runs all tests to ensure code quality
2. **Build**: Builds a Docker image and pushes it to Docker Hub
3. **Deploy**: Automatically deploys to the production server

### Setup GitHub Actions

1. Add the following secrets to your GitHub repository:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `ANTHROPIC_API_KEY`: Your Claude AI API key
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token
   - `SERVER_HOST`: Your server's hostname or IP
   - `SERVER_USERNAME`: SSH username for your server
   - `SERVER_SSH_KEY`: Private SSH key for server access
   - `SERVER_PORT`: SSH port (usually 22)

2. Configure your server path in `.github/workflows/ci-cd.yml`

### Manual Deployment

To deploy manually:

```bash
# On your server
export DOCKERHUB_USERNAME=your_username
export DOCKER_IMAGE=$DOCKERHUB_USERNAME/telegram-ai-assistant:latest
./deploy.sh
```

## File Structure

- `src/` - Main source code
  - `nlp/` - Natural language processing components
    - `Multi_part_Question_Handler.py` - Handles complex multi-part questions
    - `claude_integration.py` - Integration with Claude AI
    - `context_manager.py` - Maintains conversation context
    - `intent_classifier.py` - Classifies user intents
    - `entity_extractor.py` - Extracts entities from messages
  - `models.py` - Data models for users and interactions
  - `dialog/` - Conversation handling
  - `error/` - Error handling and logging
  - `monitoring/` - System monitoring and metrics
  - `admin/` - Admin dashboard and tools
  - `integrations/` - External service integrations
- `tests/` - Test files
- `run_bot.py` - Main entry point to run the bot
- `.github/workflows/` - CI/CD configuration
- `docker-compose.yml` - Docker configuration for development
- `docker-compose.prod.yml` - Docker configuration for production
- `deploy.sh` - Server deployment script
