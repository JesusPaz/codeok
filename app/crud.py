from typing import List, Optional, Dict, Any
from .database import get_supabase_client
from .models import (
    GitHubProfile, Repository, PullRequest, 
    RepoStatus, PullRequestStatus
)
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubProfileCRUD:
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "github_profiles"

    async def create_or_update(self, profile_data: Dict[str, Any]) -> GitHubProfile:
        """Create or update a GitHub profile"""
        try:
            # Check if profile exists
            existing = self.client.table(self.table).select("*").eq("github_id", profile_data["github_id"]).execute()
            
            if existing.data:
                # Update existing profile
                updated = self.client.table(self.table).update({
                    "username": profile_data["username"],
                    "avatar_url": profile_data.get("avatar_url"),
                    "name": profile_data.get("name"),
                    "email": profile_data.get("email"),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("github_id", profile_data["github_id"]).execute()
                
                return GitHubProfile(**updated.data[0])
            else:
                # Create new profile
                new_profile = self.client.table(self.table).insert({
                    "github_id": profile_data["github_id"],
                    "username": profile_data["username"],
                    "avatar_url": profile_data.get("avatar_url"),
                    "name": profile_data.get("name"),
                    "email": profile_data.get("email"),
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }).execute()
                
                return GitHubProfile(**new_profile.data[0])
                
        except Exception as e:
            logger.error(f"Error creating/updating GitHub profile: {e}")
            raise

    async def get_by_github_id(self, github_id: int) -> Optional[GitHubProfile]:
        """Get profile by GitHub ID"""
        try:
            result = self.client.table(self.table).select("*").eq("github_id", github_id).execute()
            if result.data:
                return GitHubProfile(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting GitHub profile: {e}")
            raise


class RepositoryCRUD:
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "repositories"

    async def create(self, repo_data: Dict[str, Any]) -> Repository:
        """Create a new repository"""
        try:
            new_repo = self.client.table(self.table).insert({
                "github_id": repo_data["github_id"],
                "name": repo_data["name"],
                "full_name": repo_data["full_name"],
                "url": repo_data["url"],
                "branch": repo_data.get("branch", "main"),
                "status": RepoStatus.PENDING.value,
                "owner_id": repo_data["owner_id"],
                "description": repo_data.get("description"),
                "is_private": repo_data.get("is_private", False),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            
            return Repository(**new_repo.data[0])
        except Exception as e:
            logger.error(f"Error creating repository: {e}")
            raise

    async def get_by_id(self, repo_id: int) -> Optional[Repository]:
        """Get repository by ID"""
        try:
            result = self.client.table(self.table).select("*").eq("id", repo_id).execute()
            if result.data:
                return Repository(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting repository: {e}")
            raise

    async def get_by_github_id(self, github_id: int) -> Optional[Repository]:
        """Get repository by GitHub ID"""
        try:
            result = self.client.table(self.table).select("*").eq("github_id", github_id).execute()
            if result.data:
                return Repository(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting repository by GitHub ID: {e}")
            raise

    async def update_status(self, repo_id: int, status: RepoStatus, message: Optional[str] = None) -> Repository:
        """Update repository status"""
        try:
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if message:
                update_data["error_message"] = message
            
            if status == RepoStatus.READY:
                update_data["processed_at"] = datetime.utcnow().isoformat()
            
            updated = self.client.table(self.table).update(update_data).eq("id", repo_id).execute()
            
            return Repository(**updated.data[0])
        except Exception as e:
            logger.error(f"Error updating repository status: {e}")
            raise

    async def list_by_owner(self, owner_id: int, page: int = 1, per_page: int = 10) -> List[Repository]:
        """List repositories by owner with pagination"""
        try:
            offset = (page - 1) * per_page
            result = self.client.table(self.table).select("*").eq("owner_id", owner_id).range(offset, offset + per_page - 1).execute()
            
            return [Repository(**repo) for repo in result.data]
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            raise

    async def delete(self, repo_id: int) -> bool:
        """Delete repository"""
        try:
            self.client.table(self.table).delete().eq("id", repo_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting repository: {e}")
            raise


class PullRequestCRUD:
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "pull_requests"

    async def create_or_update(self, pr_data: Dict[str, Any]) -> PullRequest:
        """Create or update a pull request"""
        try:
            # Check if PR exists
            existing = self.client.table(self.table).select("*").eq("github_id", pr_data["github_id"]).execute()
            
            if existing.data:
                # Update existing PR
                updated = self.client.table(self.table).update({
                    "title": pr_data["title"],
                    "body": pr_data.get("body"),
                    "status": pr_data["status"],
                    "base_branch": pr_data["base_branch"],
                    "head_branch": pr_data["head_branch"],
                    "updated_at": datetime.utcnow().isoformat(),
                    "closed_at": pr_data.get("closed_at"),
                    "merged_at": pr_data.get("merged_at")
                }).eq("github_id", pr_data["github_id"]).execute()
                
                return PullRequest(**updated.data[0])
            else:
                # Create new PR
                new_pr = self.client.table(self.table).insert({
                    "github_id": pr_data["github_id"],
                    "number": pr_data["number"],
                    "title": pr_data["title"],
                    "body": pr_data.get("body"),
                    "status": pr_data["status"],
                    "repository_id": pr_data["repository_id"],
                    "author_id": pr_data["author_id"],
                    "base_branch": pr_data["base_branch"],
                    "head_branch": pr_data["head_branch"],
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }).execute()
                
                return PullRequest(**new_pr.data[0])
                
        except Exception as e:
            logger.error(f"Error creating/updating pull request: {e}")
            raise

    async def get_by_id(self, pr_id: int) -> Optional[PullRequest]:
        """Get pull request by ID"""
        try:
            result = self.client.table(self.table).select("*").eq("id", pr_id).execute()
            if result.data:
                return PullRequest(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting pull request: {e}")
            raise

    async def list_by_repository(self, repository_id: int, page: int = 1, per_page: int = 10) -> List[PullRequest]:
        """List pull requests by repository with pagination"""
        try:
            offset = (page - 1) * per_page
            result = self.client.table(self.table).select("*").eq("repository_id", repository_id).range(offset, offset + per_page - 1).execute()
            
            return [PullRequest(**pr) for pr in result.data]
        except Exception as e:
            logger.error(f"Error listing pull requests: {e}")
            raise

    async def mark_as_processed(self, pr_id: int) -> PullRequest:
        """Mark pull request as processed"""
        try:
            updated = self.client.table(self.table).update({
                "processed": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", pr_id).execute()
            
            return PullRequest(**updated.data[0])
        except Exception as e:
            logger.error(f"Error marking PR as processed: {e}")
            raise


# CRUD instances
github_profile_crud = GitHubProfileCRUD()
repository_crud = RepositoryCRUD()
pull_request_crud = PullRequestCRUD()
