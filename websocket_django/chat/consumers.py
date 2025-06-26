import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .openai_bot import OpenAIBot

class ChatConsumer(AsyncWebsocketConsumer):
    openai_bot = None
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print(f"[DEBUG] Received WebSocket message: {text_data}")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json.get('username', 'Anonymous')
        print(f"[DEBUG] Message: '{message}' from user: '{username}'")

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )
        
        # Process all messages with AI bot (no mention required)
        print(f"[DEBUG] Processing message with AI bot...")
        
        # Initialize OpenAI bot if not already done
        if ChatConsumer.openai_bot is None:
            print("[DEBUG] Initializing OpenAI bot...")
            try:
                ChatConsumer.openai_bot = OpenAIBot()
                print("[DEBUG] OpenAI bot initialized successfully")
            except Exception as e:
                print(f"[ERROR] Failed to initialize OpenAI bot: {e}")
                print(f"[ERROR] Error type: {type(e).__name__}")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': f'AI bot initialization failed: {str(e)}',
                        'username': 'System'
                    }
                )
                return
        else:
            print("[DEBUG] OpenAI bot already initialized")
        
        # Get bot response
        try:
            print(f"[DEBUG] Sending message to bot: '{message}'")
            print("[DEBUG] Calling bot.get_response()...")
            bot_response = await ChatConsumer.openai_bot.get_response(
                message, 
                self.room_name, 
                username
            )
            print(f"[DEBUG] Bot response received: '{bot_response}'")
            
            # Send bot response to room
            print("[DEBUG] Sending bot response to room...")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': bot_response,
                    'username': 'AI Assistant'
                }
            )
            print("[DEBUG] Bot response sent successfully")
        except Exception as e:
            print(f"[ERROR] Error getting AI bot response: {e}")
            print(f"[ERROR] Error type: {type(e).__name__}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f'Sorry, I encountered an error: {str(e)}',
                    'username': 'AI Assistant'
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))