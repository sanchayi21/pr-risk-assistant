from llm_client import review_diff_with_groq
from github_client import fetch_pr_diff
from fastapi import FastAPI, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Repository, PullRequest, Review
import os
import logging
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"message": "PR Risk Assistant backend is alive"}


@app.post("/webhook")
async def github_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        payload = await request.json()

        action = payload.get("action")
        if action not in ["opened", "synchronize"]:
            logger.info(f"Ignored webhook action: {action}")
            return {"message": f"Ignored action: {action}"}

        pr_data = payload.get("pull_request", {})
        repo_data = payload.get("repository", {})

        github_repo_id = repo_data.get("id")
        repo_owner = repo_data.get("owner", {}).get("login")
        repo_name = repo_data.get("name")

        pr_number = pr_data.get("number")
        pr_title = pr_data.get("title")
        pr_author = pr_data.get("user", {}).get("login")

        logger.info(f"Received webhook: PR #{pr_number} - {pr_title} by {pr_author}")

        # Save or get the repository
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
            logger.info(f"New repo saved: {repo_owner}/{repo_name}")

        # Check if PR already exists
        existing_pr = await db.execute(
            select(PullRequest).where(
                PullRequest.repo_id == repo.id,
                PullRequest.pr_number == pr_number
            )
        )
        pull_request = existing_pr.scalars().first()

        if pull_request:
            logger.info(f"PR #{pr_number} already processed, skipping duplicate")
            return {"message": "PR already processed", "pr_number": pr_number}

        # Save the pull request
        pull_request = PullRequest(
            repo_id=repo.id,
            pr_number=pr_number,
            title=pr_title,
            author=pr_author,
            status="open"
        )
        db.add(pull_request)
        await db.commit()
        logger.info(f"PR #{pr_number} saved to database with id {pull_request.id}")

        # Fetch the actual code diff
        diff = await fetch_pr_diff(repo_owner, repo_name, pr_number)
        logger.info(f"Diff fetched for PR #{pr_number}, length: {len(diff)} chars")

        # Send diff to Groq for review
        review_data = await review_diff_with_groq(diff)
        logger.info(f"Groq review complete. Risk score: {review_data.get('risk_score')}")

        # Save the review to database
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
        logger.info(f"Review saved for PR #{pr_number}")

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
        logger.error(f"Webhook processing failed: {str(e)}")
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
    pr_result = await db.execute(
        select(PullRequest).where(PullRequest.id == pr_id)
    )
    pr = pr_result.scalar_one_or_none()

    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")

    review_result = await db.execute(
        select(Review).where(Review.pr_id == pr_id).order_by(Review.id.desc()).limit(1)
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