import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import settings


class MoltbookClient:
    def __init__(self):
        self.base = settings.moltbook_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def has_api_key(self) -> bool:
        return bool(settings.moltbook_agent_api_key)
    
    def _get_headers(self, api_key: Optional[str] = None) -> Dict[str, str]:
        key = api_key or settings.moltbook_public_key or ""
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
    
    async def get_recent_posts(self, limit: int = 20) -> List[Dict[str, Any]]:
        headers = self._get_headers()
        resp = await self.client.get(
            f"{self.base}/rest/v1/posts?order=created_at.desc&limit={limit}",
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()
    
    async def get_post_comments(self, post_id: str) -> List[Dict[str, Any]]:
        headers = self._get_headers()
        resp = await self.client.get(
            f"{self.base}/rest/v1/comments?post_id=eq.{post_id}&order=created_at.desc",
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()
    
    async def get_votes(self, post_id: str) -> List[Dict[str, Any]]:
        try:
            headers = self._get_headers()
            resp = await self.client.get(
                f"{self.base}/rest/v1/votes?post_id=eq.{post_id}",
                headers=headers
            )
            if resp.status_code == 401:
                return []
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []
    
    async def create_post(self, title: str, content: str) -> Dict[str, Any]:
        if not settings.moltbook_agent_api_key:
            raise ValueError("MOLTBOOK_AGENT_API_KEY not set")
        
        headers = self._get_headers(settings.moltbook_agent_api_key)
        payload = {
            "title": title,
            "content": content,
            "author_name": settings.moltbook_agent_name,
            "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        resp = await self.client.post(
            f"{self.base}/rest/v1/posts",
            headers=headers,
            json=payload
        )
        resp.raise_for_status()
        return resp.json()
    
    async def comment(self, post_id: str, content: str) -> Dict[str, Any]:
        if not settings.moltbook_agent_api_key:
            raise ValueError("MOLTBOOK_AGENT_API_KEY not set")
        
        headers = self._get_headers(settings.moltbook_agent_api_key)
        payload = {
            "post_id": post_id,
            "content": content,
            "author_name": settings.moltbook_agent_name
        }
        resp = await self.client.post(
            f"{self.base}/rest/v1/comments",
            headers=headers,
            json=payload
        )
        resp.raise_for_status()
        return resp.json()
    
    async def vote(self, post_id: str, direction: str = "up") -> Dict[str, Any]:
        if not settings.moltbook_agent_api_key:
            raise ValueError("MOLTBOOK_AGENT_API_KEY not set")
        
        headers = self._get_headers(settings.moltbook_agent_api_key)
        payload = {"post_id": post_id, "direction": direction}
        resp = await self.client.post(
            f"{self.base}/rest/v1/votes",
            headers=headers,
            json=payload
        )
        resp.raise_for_status()
        return resp.json()
    
    async def get_agents(self) -> List[Dict[str, Any]]:
        headers = self._get_headers()
        resp = await self.client.get(
            f"{self.base}/rest/v1/agents?select=name,karma,posts_count",
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()
    
    async def close(self):
        await self.client.aclose()
