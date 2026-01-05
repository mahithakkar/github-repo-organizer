#main.py
#This is your FastAPI application entry point

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from memory_storage import MemoryStorage
from typing import Optional

#Create FastAPI app instance
app = FastAPI(
    title="GitHub Repository Organizer",
    description="Organize your starred GitHub repositories with tags, notes, and status",
    version="1.0.0"
)

#Add CORS middleware (allows frontend to call your API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, PUT, DELETE
    allow_headers=["*"],
)

#Initialize storage (using in-memory storage for now)
#Later we'll swap this to PostgreSQL without changing any endpoints!
storage = MemoryStorage()


# ENDPOINTS (Routes)

@app.get("/")
async def root():
    """
    Health check endpoint - just confirms API is running
    Access at: http://localhost:8000/
    """
    return {
        "message": "GitHub Repository Organizer API",
        "status": "running",
        "docs": "http://localhost:8000/docs"
    }


@app.get("/repos")
async def get_all_repos(
    language: Optional[str] = None,
    tag: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get all repos with optional filters
    
    Query parameters (all optional):
    - language: Filter by programming language (e.g., "Python")
    - tag: Filter by custom tag (e.g., "backend")
    - status: Filter by status (e.g., "to-try", "tried", "using", "abandoned")
    
    Example: GET /repos?language=Python&tag=backend
    """
    # Get all repos from storage
    results = storage.get_all_repos()
    
    # Apply language filter if provided
    if language:
        results = [
            repo for repo in results 
            if repo["language"].lower() == language.lower()
        ]
    
    # Apply tag filter if provided
    if tag:
        results = [
            repo for repo in results
            if tag.lower() in [t.lower() for t in repo["tags"]]
        ]
    
    # Apply status filter if provided
    if status:
        results = [
            repo for repo in results
            if repo["status"].lower() == status.lower()
        ]
    
    return {
        "total": len(results),
        "repos": results
    }


@app.get("/repos/{repo_id}")
async def get_repo(repo_id: int):
    """
    Get a single repo by ID
    
    Example: GET /repos/1
    """
    repo = storage.get_repo(repo_id)
    
    if not repo:
        raise HTTPException(
            status_code=404,
            detail=f"Repo with id {repo_id} not found"
        )
    
    return repo


@app.post("/repos")
async def add_repo(repo: dict):
    """
    Add a new repository
    
    Body example:
    {
        "url": "https://github.com/user/repo",
        "name": "repo-name",
        "description": "Description here",
        "language": "Python",
        "tags": ["backend", "api"],
        "notes": "Good tutorial for FastAPI",
        "status": "to-try",
        "priority": "high"
    }
    """
    # Basic validation
    if "url" not in repo:
        raise HTTPException(
            status_code=400,
            detail="URL is required"
        )
    
    # Add repo using storage
    new_repo = storage.add_repo(repo)
    
    return {
        "message": "Repository added successfully",
        "repo": new_repo
    }


@app.put("/repos/{repo_id}")
async def update_repo(repo_id: int, updates: dict):
    """
    Update a repository's metadata (tags, notes, status, priority)
    
    Example: PUT /repos/1
    Body: {"tags": ["backend", "python"], "status": "using"}
    """
    try:
        updated_repo = storage.update_repo(repo_id, updates)
        return {
            "message": "Repository updated successfully",
            "repo": updated_repo
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/repos/{repo_id}")
async def delete_repo(repo_id: int):
    """
    Delete a repository
    
    Example: DELETE /repos/1
    """
    success = storage.delete_repo(repo_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Repo with id {repo_id} not found"
        )
    
    return {"message": f"Repository {repo_id} deleted successfully"}


@app.get("/repos/search/{query}")
async def search_repos(query: str):
    """
    Search repos by name, description, or tags
    
    Example: GET /repos/search/fastapi
    """
    results = storage.search_repos(query)
    
    return {
        "query": query,
        "total": len(results),
        "repos": results
    }


@app.get("/stats")
async def get_stats():
    """
    Get statistics about your repos
    
    Returns:
    - Total repos
    - Repos by language
    - Repos by status
    - Average priority
    """
    all_repos = storage.get_all_repos()
    
    # Count by language
    languages = {}
    for repo in all_repos:
        lang = repo.get("language", "Unknown")
        languages[lang] = languages.get(lang, 0) + 1
    
    # Count by status
    statuses = {}
    for repo in all_repos:
        status = repo.get("status", "unknown")
        statuses[status] = statuses.get(status, 0) + 1
    
    return {
        "total_repos": len(all_repos),
        "by_language": languages,
        "by_status": statuses
    }


#RUN THE APP
#To run: uvicorn main:app --reload
#Then visit: http://localhost:8000/docs