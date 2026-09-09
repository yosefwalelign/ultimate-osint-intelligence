"""Behavior Profiling - AI-powered user behavior analysis using Gemma 3.1B"""

import logging
import asyncio
from typing import Dict, List, Optional
import aiohttp
import json

logger = logging.getLogger(__name__)

# Free AI APIs for unlimited requests
AI_PROVIDERS = {
    'together_ai': {
        'url': 'https://api.together.xyz/inference',
        'model': 'togethercomputer/llama-2-7b-chat',
        'free_tier': True,
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'huggingface': {
        'url': 'https://api-inference.huggingface.co/models/',
        'model': 'mistralai/Mistral-7B-Instruct-v0.1',
        'free_tier': True,
        'api_key_env': 'HUGGINGFACE_API_KEY'
    },
    'deepseek': {
        'url': 'https://api.deepseek.com/v1/chat/completions',
        'model': 'deepseek-chat',
        'free_tier': True,
        'api_key_env': 'DEEPSEEK_API_KEY'
    }
}


class BehaviorProfiler:
    """AI-powered behavior analysis using free LLM APIs"""

    def __init__(self, provider: str = 'together_ai'):
        self.provider = AI_PROVIDERS.get(provider, AI_PROVIDERS['together_ai'])
        self.api_key = None
        self._load_api_key()

    def _load_api_key(self):
        """Load API key from environment"""
        import os
        env_var = self.provider.get('api_key_env')
        if env_var:
            self.api_key = os.getenv(env_var)

    async def profile_user(self, user_data: Dict) -> Dict:
        """Profile user behavior using AI"""
        try:
            # Prepare analysis prompt
            prompt = self._prepare_prompt(user_data)
            
            # Get AI analysis
            analysis = await self._call_ai_api(prompt)
            
            return {
                'profile': analysis,
                'data_sources': list(user_data.keys()),
                'confidence': self._calculate_confidence(user_data)
            }
        except Exception as e:
            logger.error(f"Behavior profiling error: {e}")
            return {'error': str(e)}

    def _prepare_prompt(self, user_data: Dict) -> str:
        """Prepare analysis prompt for LLM"""
        prompt = f"""
Analyze the following OSINT data and provide a behavioral profile:

Data:
{json.dumps(user_data, indent=2)}

Provide analysis on:
1. Professional profile and work habits
2. Social media behavior patterns
3. Technical skill level
4. Geographic indicators
5. Personality traits (based on available data)
6. Risk assessment
7. Anomalies or suspicious patterns

Format response as JSON with these keys:
- professional_profile
- social_patterns
- technical_level
- geography
- personality_traits
- risk_score (0-100)
- anomalies
- summary
        """
        return prompt

    async def _call_ai_api(self, prompt: str) -> Dict:
        """Call AI API for analysis"""
        try:
            if self.provider.get('url') == 'https://api.together.xyz/inference':
                return await self._together_ai_call(prompt)
            elif 'huggingface' in self.provider.get('url', ''):
                return await self._huggingface_call(prompt)
            elif 'deepseek' in self.provider.get('url', ''):
                return await self._deepseek_call(prompt)
        except Exception as e:
            logger.error(f"AI API call error: {e}")
            return {}

    async def _together_ai_call(self, prompt: str) -> Dict:
        """Call Together AI API (Mistral, Llama)"""
        headers = {'Authorization': f'Bearer {self.api_key}'}
        payload = {
            'model': 'mistralai/Mistral-7B-Instruct-v0.1',
            'prompt': prompt,
            'max_tokens': 1024,
            'temperature': 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.provider['url'], 
                                   headers=headers, 
                                   json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._parse_response(data.get('output', {}).get('choices', [{}])[0].get('text', ''))
                else:
                    logger.warning(f"API error: {resp.status}")
                    return {}

    async def _huggingface_call(self, prompt: str) -> Dict:
        """Call Hugging Face Inference API"""
        headers = {'Authorization': f'Bearer {self.api_key}'}
        url = f"{self.provider['url']}{self.provider['model']}"
        payload = {'inputs': prompt}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response_text = data[0].get('generated_text', '') if data else ''
                    return self._parse_response(response_text)
                else:
                    logger.warning(f"API error: {resp.status}")
                    return {}

    async def _deepseek_call(self, prompt: str) -> Dict:
        """Call DeepSeek API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'deepseek-chat',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 1024,
            'temperature': 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.provider['url'], 
                                   headers=headers, 
                                   json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response_text = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    return self._parse_response(response_text)
                else:
                    logger.warning(f"API error: {resp.status}")
                    return {}

    def _parse_response(self, response_text: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON from response
            if '{' in response_text and '}' in response_text:
                json_str = response_text[response_text.find('{'):response_text.rfind('}')+1]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback to text response
        return {'analysis': response_text}

    def _calculate_confidence(self, user_data: Dict) -> float:
        """Calculate confidence in analysis based on data completeness"""
        data_completeness = len([v for v in user_data.values() if v]) / len(user_data)
        return min(data_completeness * 0.9, 0.95)  # Max 95% confidence


async def profile_behavior(user_data: Dict, provider: str = 'together_ai') -> Dict:
    """Main profiling function"""
    profiler = BehaviorProfiler(provider)
    return await profiler.profile_user(user_data)
