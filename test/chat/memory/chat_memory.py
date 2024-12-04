# memory/chat_memory.py

class ChatMemory:
    def __init__(self):
        self.history = []

    def add_interaction(self, user_input, bot_response):
        """Adds a user-bot interaction to the memory."""
        self.history.append({"user": user_input, "bot": bot_response})

    def get_context(self, limit=None):
        """
        Retrieves the conversation history as a string.
        If limit is provided, only the last `limit` number of interactions will be returned.
        """
        context = "\n".join([f"User: {entry['user']}\nBot: {entry['bot']}" for entry in self.history])
        return context if limit is None else "\n".join(context.splitlines()[-limit:])

