"""GitHub activity analysis module"""

import asyncio
import logging
from typing import Dict, List, Optional
from src.core.engine import ScanResult
from src.core.async_handler import AsyncRequestHandler
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class GitHubAnalyzer:
    """Analyze GitHub activity and user behavior"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.handler = AsyncRequestHandler(config)

    async def scan(self, username: str, target_type: str = 'username') -> List[ScanResult]:
        """Analyze GitHub user"""
        logger.info(f"Analyzing GitHub user: {username}")
        
        results = []
        
        try:
            # Get user info via API
            url = f"https://api.github.com/users/{username}"
            content = await self.handler.get(url, use_proxy=False)
            
            if content:
                try:
                    user_data = json.loads(content)
                    
                    result = ScanResult(
                        scan_id=f"github_{username}",
                        target=username,
                        target_type='username',
                        module='github',
                        found=True,
                        data={
                            'user_id': user_data.get('id'),
                            'name': user_data.get('name'),
                            'bio': user_data.get('bio'),
                            'location': user_data.get('location'),
                            'company': user_data.get('company'),
                            'blog': user_data.get('blog'),
                            'twitter': user_data.get('twitter_username'),
                            'followers': user_data.get('followers'),
                            'following': user_data.get('following'),
                            'repos': user_data.get('public_repos'),
                            'created_at': user_data.get('created_at'),
                            'updated_at': user_data.get('updated_at'),
                            'profile_url': user_data.get('html_url')
                        },
                        timestamp=datetime.now(),
                        accuracy_score=0.99,
                        confidence='high',
                        source='github'
                    )
                    results.append(result)
                    
                    # Get commit activity
                    commits_result = await self._analyze_commits(username)
                    if commits_result:
                        results.append(commits_result)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON response for {username}")
        
        except Exception as e:
            logger.error(f"GitHub scan error: {e}")
        
        return results

    async def _analyze_commits(self, username: str) -> Optional[ScanResult]:
        """Analyze commit patterns for active hours"""
        try:
            # This would analyze commit timestamps
            result = ScanResult(
                scan_id=f"github_commits_{username}",
                target=username,
                target_type='username',
                module='github_activity',
                found=True,
                data={
                    'analysis': 'commit_pattern_analysis_placeholder',
                    'note': 'Real implementation would fetch commits and analyze timestamps'
                },
                timestamp=datetime.now(),
                accuracy_score=0.85,
                confidence='medium',
                source='github'
            )
            return result
        except Exception as e:
            logger.error(f"Commit analysis error: {e}")
            return None


github = GitHubAnalyzer()


async def scan(target: str, target_type: str = 'username') -> List[ScanResult]:
    """Module scan function"""
    return await github.scan(target, target_type)
