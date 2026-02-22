from pydantic import BaseModel, Field, SecretStr
from typing import Optional


class Settings(BaseModel):
    moltbook_url: str = Field(default="https://ehxbxtjliybbloantpwq.supabase.co")
    moltbook_public_key: Optional[str] = Field(default=None, env="MOLTBOOK_PUBLIC_KEY")
    moltbook_agent_name: str = Field(default="", env="MOLTBOOK_AGENT_NAME")
    moltbook_agent_api_key: Optional[str] = Field(default=None, env="MOLTBOOK_AGENT_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    database_url: str = Field(default="sqlite:///./moltbook_agent.db")
    poll_interval: int = Field(default=300)
    learning_interval: int = Field(default=3600)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
