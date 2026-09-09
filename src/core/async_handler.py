"""Asynchronous Request Handler for OSINT Operations"""

import asyncio
import logging
from typing import List, Dict, Callable, Any, Optional, Coroutine
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import time

logger = logging.getLogger(__name__)


class AsyncHandler:
    """Handles asynchronous operations for OSINT scanning"""
    
    def __init__(self, max_workers: int = 50, timeout: int = 30):
        """Initialize async handler"""
        self.max_workers = max_workers
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"AsyncHandler initialized with {max_workers} workers")
    
    async def execute_parallel_tasks(
        self, 
        tasks: List[Coroutine],
        batch_size: int = 10
    ) -> List[Any]:
        """Execute multiple tasks in parallel with rate limiting"""
        results = []
        try:
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                results.extend(batch_results)
                # Rate limiting between batches
                if i + batch_size < len(tasks):
                    await asyncio.sleep(0.5)
            
            logger.info(f"Executed {len(tasks)} tasks in parallel")
            return results
        except Exception as e:
            logger.error(f"Parallel execution error: {e}")
            return results
    
    async def fetch_with_retry(
        self,
        url: str,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=self.timeout) as response:
                        if response.status == 200:
                            return {
                                'status': response.status,
                                'data': await response.text(),
                                'headers': dict(response.headers)
                            }
                        elif response.status == 429:  # Rate limited
                            wait_time = 2 ** attempt
                            logger.warning(f"Rate limited, waiting {wait_time}s")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.warning(f"HTTP {response.status}: {url}")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            except Exception as e:
                logger.error(f"Fetch error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
        
        return None
    
    async def run_with_timeout(
        self,
        coro: Coroutine,
        timeout: Optional[int] = None
    ) -> Optional[Any]:
        """Run coroutine with timeout"""
        timeout = timeout or self.timeout
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {timeout}s")
            return None
        except Exception as e:
            logger.error(f"Operation error: {e}")
            return None
