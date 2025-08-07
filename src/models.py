"""
数据模型定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BilibiliUser(BaseModel):
    """B站用户信息模型"""
    mid: int = Field(..., description="用户ID")
    uname: str = Field(..., description="用户名")
    sign: str = Field(default="", description="个人签名")
    face: str = Field(default="", description="头像URL")
    official_verify: Dict[str, Any] = Field(default_factory=dict, description="认证信息")
    vip: Dict[str, Any] = Field(default_factory=dict, description="大会员信息")
    follow_time: str = Field(default="", description="关注时间")
    
    class Config:
        extra = "allow"


class FollowingResponse(BaseModel):
    """关注列表响应模型"""
    code: int
    message: str
    ttl: int
    data: Dict[str, Any]
    
    @property
    def users(self) -> List[BilibiliUser]:
        """获取用户列表"""
        if self.data and "list" in self.data:
            return [BilibiliUser(**user) for user in self.data["list"]]
        return []
    
    @property
    def total(self) -> int:
        """获取总数"""
        return self.data.get("total", 0) if self.data else 0


class TagGroup(BaseModel):
    """分组信息模型"""
    tagid: int = Field(..., description="分组ID")
    name: str = Field(..., description="分组名称")
    count: int = Field(default=0, description="分组内用户数量")
    tip: str = Field(default="", description="分组提示")


class TagsResponse(BaseModel):
    """分组列表响应模型"""
    code: int
    message: str
    ttl: int
    data: List[TagGroup]


class CreateTagResponse(BaseModel):
    """创建分组响应模型"""
    code: int
    message: str
    ttl: int
    data: Dict[str, int]
    
    @property
    def tagid(self) -> Optional[int]:
        """获取创建的分组ID"""
        return self.data.get("tagid") if self.data else None


class BatchGroupResponse(BaseModel):
    """批量分组响应模型"""
    code: int
    message: str
    ttl: int


class AIAnalysisResult(BaseModel):
    """AI分析结果模型"""
    mid: int = Field(..., description="用户ID")
    uname: str = Field(..., description="用户名")
    sign: str = Field(default="", description="个人签名")
    category: str = Field(..., description="分类标签")
    confidence: float = Field(default=0.0, description="置信度")
    reason: str = Field(default="", description="分类原因")


class GroupingTask(BaseModel):
    """分组任务模型"""
    category: str = Field(..., description="分类名称")
    users: List[BilibiliUser] = Field(..., description="用户列表")
    tagid: Optional[int] = Field(default=None, description="分组ID")
    created: bool = Field(default=False, description="是否已创建分组")
    grouped: bool = Field(default=False, description="是否已完成分组")


class Config(BaseModel):
    """配置模型"""
    # B站相关配置
    vmid: str = Field(..., description="用户ID")
    cookie: str = Field(..., description="登录Cookie")
    csrf_token: str = Field(..., description="CSRF Token")
    
    # AI相关配置
    openai_api_key: str = Field(..., description="OpenAI API Key")
    openai_base_url: str = Field(default="https://api.openai.com/v1", description="OpenAI API Base URL")
    model_name: str = Field(default="gpt-3.5-turbo", description="使用的模型名称")
    
    # 请求配置
    request_delay: float = Field(default=1.0, description="请求间隔(秒)")
    max_retries: int = Field(default=3, description="最大重试次数")
    timeout: int = Field(default=30, description="请求超时时间(秒)")
    
    # 分页配置
    page_size: int = Field(default=24, description="每页数量")
    max_pages: int = Field(default=100, description="最大页数")

    # AI分析配置
    ai_batch_size: int = Field(default=10, description="AI分析批次大小")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Statistics(BaseModel):
    """统计信息模型"""
    total_users: int = Field(default=0, description="总用户数")
    analyzed_users: int = Field(default=0, description="已分析用户数")
    created_groups: int = Field(default=0, description="创建的分组数")
    grouped_users: int = Field(default=0, description="已分组用户数")
    unknown_users: int = Field(default=0, description="未知分类用户数")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    
    @property
    def duration(self) -> Optional[float]:
        """获取执行时长(秒)"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """获取成功率"""
        if self.total_users == 0:
            return 0.0
        return (self.analyzed_users - self.unknown_users) / self.total_users * 100
