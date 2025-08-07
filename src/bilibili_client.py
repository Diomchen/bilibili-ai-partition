"""
哔哩哔哩API客户端
"""
import asyncio
import aiohttp
import json
import urllib.parse
from typing import List, Optional, Dict, Any
from asyncio_throttle import Throttler
import logging

from .models import (
    BilibiliUser, FollowingResponse, TagGroup, TagsResponse, 
    CreateTagResponse, BatchGroupResponse, Config
)

logger = logging.getLogger(__name__)


class BilibiliAPIError(Exception):
    """B站API错误"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API Error {code}: {message}")


class BilibiliClient:
    """哔哩哔哩API客户端"""
    
    BASE_URL = "https://api.bilibili.com"
    
    def __init__(self, config: Config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.throttler = Throttler(rate_limit=1, period=config.request_delay)
        
        # 构建通用请求头
        self.headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.7",
            "origin": "https://space.bilibili.com",
            "priority": "u=1, i",
            "referer": "https://space.bilibili.com/",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Cookie": self.config.cookie
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """发起HTTP请求"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async with statement.")
        
        async with self.throttler:
            for attempt in range(self.config.max_retries):
                try:
                    async with self.session.request(method, url, **kwargs) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("code") != 0:
                                raise BilibiliAPIError(data.get("code", -1), data.get("message", "Unknown error"))
                            return data
                        else:
                            logger.warning(f"HTTP {response.status} for {url}, attempt {attempt + 1}")
                            if attempt == self.config.max_retries - 1:
                                response.raise_for_status()
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    logger.warning(f"Request failed for {url}, attempt {attempt + 1}: {e}")
                    if attempt == self.config.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)  # 指数退避
        
        raise RuntimeError("Max retries exceeded")
    
    async def get_followings(self, page: int = 1, page_size: int = 24) -> FollowingResponse:
        """获取关注列表"""
        url = f"{self.BASE_URL}/x/relation/followings"
        params = {
            "order": "desc",
            "order_type": "",
            "vmid": self.config.vmid,
            "pn": str(page),
            "ps": str(page_size),
            "gaia_source": "main_web",
            "web_location": "333.1387"
        }
        
        logger.info(f"Fetching followings page {page} with {page_size} items")
        data = await self._make_request("GET", url, params=params)
        return FollowingResponse(**data)
    
    async def get_all_followings(self) -> List[BilibiliUser]:
        """获取所有关注用户"""
        all_users = []
        page = 1
        
        while page <= self.config.max_pages:
            try:
                response = await self.get_followings(page, self.config.page_size)
                users = response.users
                
                if not users:
                    logger.info(f"No more users found at page {page}")
                    break
                
                all_users.extend(users)
                logger.info(f"Fetched {len(users)} users from page {page}, total: {len(all_users)}")
                
                # 检查是否已获取所有用户
                if len(all_users) >= response.total:
                    logger.info(f"Fetched all {response.total} users")
                    break
                
                page += 1
                
            except BilibiliAPIError as e:
                logger.error(f"Failed to fetch page {page}: {e}")
                break
        
        logger.info(f"Total fetched users: {len(all_users)}")
        return all_users
    
    async def get_tags(self) -> TagsResponse:
        """获取用户分组列表"""
        url = f"{self.BASE_URL}/x/relation/tags"
        params = {
            "only_master": "true",
            "web_location": "333.1387"
        }
        
        logger.info("Fetching user tags")
        data = await self._make_request("GET", url, params=params)
        return TagsResponse(**data)
    
    async def create_tag(self, tag_name: str) -> CreateTagResponse:
        """创建分组"""
        url = f"{self.BASE_URL}/x/relation/tag/create"
        
        # 构建查询参数
        device_req = {
            "platform": "web",
            "device": "pc", 
            "spmid": "333.1387"
        }
        params = {
            "x-bili-device-req-json": json.dumps(device_req, separators=(',', ':'))
        }
        
        # 构建表单数据
        data = {
            "tag": tag_name,
            "csrf": self.config.csrf_token
        }
        
        # 设置Content-Type
        headers = {"content-type": "application/x-www-form-urlencoded"}
        
        logger.info(f"Creating tag: {tag_name}")
        response_data = await self._make_request(
            "POST", url, 
            params=params, 
            data=data, 
            headers=headers
        )
        return CreateTagResponse(**response_data)
    
    async def batch_group_users(self, user_mids: List[int], tag_id: int) -> BatchGroupResponse:
        """批量分组用户"""
        url = f"{self.BASE_URL}/x/relation/tags/addUsers"
        
        # 构建查询参数
        device_req = {
            "platform": "web",
            "device": "pc",
            "spmid": "333.1387"
        }
        params = {
            "x-bili-device-req-json": json.dumps(device_req, separators=(',', ':'))
        }
        
        # 构建表单数据
        data = {
            "fids": ",".join(map(str, user_mids)),
            "tagids": str(tag_id),
            "csrf": self.config.csrf_token
        }
        
        # 设置Content-Type
        headers = {"content-type": "application/x-www-form-urlencoded"}
        
        logger.info(f"Batch grouping {len(user_mids)} users to tag {tag_id}")
        response_data = await self._make_request(
            "POST", url,
            params=params,
            data=data,
            headers=headers
        )
        return BatchGroupResponse(**response_data)
    
    async def check_existing_tags(self) -> Dict[str, int]:
        """检查已存在的分组，返回分组名到ID的映射"""
        try:
            response = await self.get_tags()
            return {tag.name: tag.tagid for tag in response.data}
        except Exception as e:
            logger.error(f"Failed to fetch existing tags: {e}")
            return {}
    
    async def ensure_tag_exists(self, tag_name: str, existing_tags: Dict[str, int]) -> int:
        """确保分组存在，如果不存在则创建"""
        if tag_name in existing_tags:
            logger.info(f"Tag '{tag_name}' already exists with ID {existing_tags[tag_name]}")
            return existing_tags[tag_name]
        
        try:
            response = await self.create_tag(tag_name)
            tag_id = response.tagid
            if tag_id:
                logger.info(f"Created tag '{tag_name}' with ID {tag_id}")
                existing_tags[tag_name] = tag_id  # 更新缓存
                return tag_id
            else:
                raise ValueError(f"Failed to get tag ID for '{tag_name}'")
        except Exception as e:
            logger.error(f"Failed to create tag '{tag_name}': {e}")
            raise
