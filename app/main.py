from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import repos, query, webhooks
from .queues import start_background_worker

# Create FastAPI instance
app = FastAPI(
    title="Repository Analysis API",
    description="API para análisis de repositorios con ingesta, consultas y grafos",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(repos.router)
app.include_router(query.router)
app.include_router(webhooks.router)

# Start background worker on startup
@app.on_event("startup")
async def startup_event():
    """Initialize background services"""
    start_background_worker()


@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Repository Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "POST /repos": "Register a repository",
            "GET /repos/{repo_id}/status": "Get repository status",
            "POST /query": "Query repository",
            "GET /repos/{repo_id}/graph": "Get repository graph (optional)",
            "DELETE /repos/{repo_id}": "Delete repository"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}
