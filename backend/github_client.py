import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
print(f"Token loaded: {GITHUB_TOKEN[:10] if GITHUB_TOKEN else 'NOT FOUND'}")

async def fetch_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    """
    Calls GitHub API and returns the raw diff of a pull request.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"  # this tells GitHub: give me the diff format
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
        
        return response.text  # this is the raw diff text