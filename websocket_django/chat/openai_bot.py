import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from the project root
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Workaround for proxy issue - patch httpx to remove proxy detection
import httpx
original_client_init = httpx.Client.__init__
original_async_client_init = httpx.AsyncClient.__init__

def patched_client_init(self, *args, **kwargs):
    # Remove proxies argument if present
    kwargs.pop('proxies', None)
    kwargs.pop('proxy', None)
    return original_client_init(self, *args, **kwargs)

def patched_async_client_init(self, *args, **kwargs):
    # Remove proxies argument if present
    kwargs.pop('proxies', None)
    kwargs.pop('proxy', None)
    return original_async_client_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_client_init
httpx.AsyncClient.__init__ = patched_async_client_init

# Now import OpenAI after patching
from openai import OpenAI

class OpenAIBot:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"Loading OpenAI API key from {env_path}")
        print(f"API key found: {'Yes' if api_key else 'No'}")
        print(f"API key length: {len(api_key) if api_key else 0}")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        if not api_key.startswith('sk-'):
            print("Warning: API key doesn't start with 'sk-', it might be invalid")
            
        try:
            # Initialize with clean parameters to avoid proxy issues
            self.client = OpenAI(api_key=api_key)
            print("OpenAI client initialized successfully")
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            print(f"Error details: {type(e).__name__}: {str(e)}")
            raise
        
        self.conversation_history = {}
    
    async def get_response(self, message, room_name, username):
        # Maintain conversation history per room
        if room_name not in self.conversation_history:
            self.conversation_history[room_name] = []
        
        # Add user message to history
        self.conversation_history[room_name].append({
            "role": "user",
            "content": f"{username}: {message}"
        })
        
        # Keep only last 20 messages to manage context
        if len(self.conversation_history[room_name]) > 20:
            self.conversation_history[room_name] = self.conversation_history[room_name][-20:]
        
        try:
            # Create messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant in a chat room. Keep your responses concise and friendly."
                }
            ]
            
            # Add conversation history
            for msg in self.conversation_history[room_name][-10:]:
                messages.append(msg)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content
            
            # Add bot response to history
            self.conversation_history[room_name].append({
                "role": "assistant",
                "content": bot_response
            })
            
            return bot_response
            
        except Exception as e:
            print(f"Error getting OpenAI response: {e}")
            print(f"Error type: {type(e).__name__}")
            if hasattr(e, 'response'):
                print(f"Response status: {getattr(e.response, 'status_code', 'N/A')}")
                print(f"Response body: {getattr(e.response, 'text', 'N/A')}")
            return f"Sorry, I'm having trouble responding right now. Error: {str(e)}"
    
    def clear_room_history(self, room_name):
        if room_name in self.conversation_history:
            del self.conversation_history[room_name]