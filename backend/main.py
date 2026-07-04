from llm_client import review_diff_with_groq
from github_client import fetch_pr_diff
from fastapi import FastAPI, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Repository, PullRequest, Review
import hmac
import hashlib
import os
from dotenv import load_dotenv



load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "PR Risk Assistant backend is alive"}

@app.post("/webhook")
async def github_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.body()
        payload = await request.json()

        action = payload.get("action")
        if action not in ["opened", "synchronize"]:
            return {"message": f"Ignored action: {action}"}

        pr_data = payload.get("pull_request", {})
        repo_data = payload.get("repository", {})

        github_repo_id = repo_data.get("id")
        repo_owner = repo_data.get("owner", {}).get("login")
        repo_name = repo_data.get("name")

        pr_number = pr_data.get("number")
        pr_title = pr_data.get("title")
        pr_author = pr_data.get("user", {}).get("login")

        result = await db.execute(
            select(Repository).where(Repository.github_repo_id == github_repo_id)
        )
        repo = result.scalar_one_or_none()

        if not repo:
            repo = Repository(
                github_repo_id=github_repo_id,
                owner=repo_owner,
                name=repo_name
            )
            db.add(repo)
            await db.flush()

        pull_request = PullRequest(
            repo_id=repo.id,
            pr_number=pr_number,
            title=pr_title,
            author=pr_author,
            status="open"
        )
        db.add(pull_request)
        await db.commit()

        # Phase 3: Fetch the actual code diff
        diff = await fetch_pr_diff(repo_owner, repo_name, pr_number)

        # Phase 4: Send diff to Groq for review
        review_data = await review_diff_with_groq(diff)

        # Save the review to database
        from models import Review
        review = Review(
            pr_id=pull_request.id,
            summary=review_data.get("summary", ""),
            risk_score=float(review_data.get("risk_score", 5)),
            bugs=review_data.get("bugs"),
            security_issues=review_data.get("security_issues"),
            test_gaps=review_data.get("test_gaps")
        )
        db.add(review)
        await db.commit()

        return {
            "message": "PR reviewed and saved",
            "repo": f"{repo_owner}/{repo_name}",
            "pr_number": pr_number,
            "title": pr_title,
            "risk_score": review_data.get("risk_score"),
            "summary": review_data.get("summary")
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/prs")
async def list_pull_requests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PullRequest).order_by(PullRequest.created_at.desc())
    )
    prs = result.scalars().all()

    return [
        {
            "id": pr.id,
            "pr_number": pr.pr_number,
            "title": pr.title,
            "author": pr.author,
            "status": pr.status,
            "created_at": pr.created_at.isoformat() if pr.created_at else None
        }
        for pr in prs
    ]


@app.get("/prs/{pr_id}")
async def get_pull_request(pr_id: int, db: AsyncSession = Depends(get_db)):
    # Get the PR
    pr_result = await db.execute(
        select(PullRequest).where(PullRequest.id == pr_id)
    )
    pr = pr_result.scalar_one_or_none()

    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")

    # Get its review
    review_result = await db.execute(
        select(Review).where(Review.pr_id == pr_id)
    )
    review = review_result.scalar_one_or_none()

    return {
        "id": pr.id,
        "pr_number": pr.pr_number,
        "title": pr.title,
        "author": pr.author,
        "status": pr.status,
        "created_at": pr.created_at.isoformat() if pr.created_at else None,
        "review": {
            "summary": review.summary,
            "risk_score": review.risk_score,
            "bugs": review.bugs,
            "security_issues": review.security_issues,
            "test_gaps": review.test_gaps
        } if review else None
    }