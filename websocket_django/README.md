# Django WebSocket Chat Application with AI Assistant

This is a Django application with WebSocket integration using Django Channels, featuring an AI-powered assistant that automatically responds to all messages using OpenAI's GPT.

## Features
- Real-time WebSocket communication
- Multi-room chat support
- User-friendly interface
- Redis as message broker
- AI Assistant:
  - Automatically responds to all messages using OpenAI's GPT
  - No special commands or mentions required

## Setup Instructions

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Add your API key:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

4. **Install Redis (if not already installed):**
   - On Ubuntu/Debian: `sudo apt-get install redis-server`
   - On macOS: `brew install redis`
   - On Windows: Download from https://github.com/microsoftarchive/redis/releases

5. **Start Redis server:**
   ```bash
   redis-server
   ```

6. **Run database migrations:**
   ```bash
   ./venv/bin/python manage.py migrate
   ```

7. **Start the Django development server:**
   ```bash
   ./venv/bin/python manage.py runserver
   ```

8. **Access the application:**
   - Open your browser and go to: http://localhost:8000/chat/
   - Enter a room name to create or join a chat room
   - Open multiple browser windows to test real-time messaging

## Project Structure
- `websocket_project/` - Main Django project settings
- `chat/` - Chat application with WebSocket consumer
- `chat/consumers.py` - WebSocket consumer handling connections
- `chat/routing.py` - WebSocket URL routing
- `chat/templates/` - HTML templates for the chat interface

## WebSocket Endpoint
- WebSocket connections are established at: `ws://localhost:8000/ws/chat/{room_name}/`

## Testing WebSocket Connection
1. Enter a room name on the homepage
2. Set your username
3. Start sending messages
4. Open the same room in another browser window to see real-time messaging
5. The AI assistant will automatically respond to all messages

## Dependencies
- Django 5.0.1
- Channels 4.0.0
- channels-redis 4.1.0
- Daphne 4.0.0 (ASGI server)
- Redis 5.0.1
- openai 1.12.0 (for GPT integration)
- python-dotenv 1.0.0 (for environment variables)

## Using the AI Assistant

### Automatic AI Responses
- Simply type any message and send it
- The AI assistant will automatically respond to every message
- No special commands or mentions needed
- Example: Just type "Tell me a joke" and press Enter

### Notes
- The AI assistant maintains conversation context within each room
- Each user's messages are tracked separately
- API key must be properly configured in the .env file
- If the assistant is not responding, check the console for API key errors
- All messages in the chat room will receive AI responses