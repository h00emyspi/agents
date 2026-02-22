import os
from typing import Optional


class Settings:
    def __init__(self):
        self.moltbook_url = os.getenv("MOLTBOOK_SUPABASE_URL", "https://ehxbxtjliybbloantpwq.supabase.co")
        self.moltbook_public_key = os.getenv("MOLTBOOK_PUBLIC_KEY", "sb_publishable_4ZaiilhgPir-2ns8Hxg5Tw_JqZU_G6-")
        self.moltbook_agent_name = os.getenv("MOLTBOOK_AGENT_NAME", "")
        self.moltbook_agent_api_key = os.getenv("MOLTBOOK_AGENT_API_KEY", None)
        self.openai_api_key = os.getenv("OPENAI_API_KEY", None)
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///C:/Users/BMW/tssss/moltbook-ai-agent/moltbook_agent.db")
        self.poll_interval = int(os.getenv("POLL_INTERVAL", "300"))
        self.learning_interval = int(os.getenv("LEARNING_INTERVAL", "3600"))
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")


settings = Settings()
