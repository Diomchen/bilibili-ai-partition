"""
AI分析模块 - 用于分析UP主信息并生成分类标签
"""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from asyncio_throttle import Throttler

from .models import BilibiliUser, AIAnalysisResult, Config

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI分析器"""

    # 预定义的分类标签
    PREDEFINED_CATEGORIES = [
        "科技", "游戏", "音乐", "舞蹈", "美食", "旅游", "时尚", "美妆",
        "教育", "知识", "财经", "投资", "创业", "职场", "生活", "娱乐",
        "影视", "动漫", "体育", "健身", "汽车", "数码", "摄影", "艺术",
        "设计", "编程", "AI", "科学", "历史", "文学", "心理", "医学",
        "法律", "新闻", "时事", "搞笑", "萌宠", "母婴", "家居", "手工",
        "未知"
    ]

    def __init__(self, config: Config):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url
        )
        # 限制AI请求频率，避免超出限制
        self.throttler = Throttler(rate_limit=10, period=60)  # 每分钟最多10次请求
        self.progress_callback = None  # 进度回调函数

    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def _build_analysis_prompt(self, users: List[BilibiliUser]) -> str:
        """构建分析提示词"""
        user_info = []
        for user in users:
            info = f"用户名: {user.uname}"
            if user.sign.strip():
                info += f", 签名: {user.sign}"
            user_info.append(info)
        
        categories_str = "、".join(self.PREDEFINED_CATEGORIES[:-1])  # 排除"未知"
        
        prompt = f"""请分析以下B站UP主的用户名和签名，为每个UP主分配最合适的分类标签。

可选分类标签：{categories_str}

分析规则：
1. 根据用户名和签名的内容特征进行分类
2. 优先考虑明显的关键词和领域特征
3. 如果信息不足或无法明确分类，请标记为"未知"
4. 每个用户只能分配一个最主要的分类标签
5. 请提供简短的分类理由

UP主信息：
{chr(10).join(user_info)}

请以JSON格式返回分析结果，格式如下：
{{
    "results": [
        {{
            "uname": "用户名",
            "category": "分类标签",
            "confidence": 0.8,
            "reason": "分类理由"
        }}
    ]
}}

注意：confidence为置信度(0-1之间的浮点数)，reason为简短的分类理由。"""
        
        return prompt

    def _clean_ai_response(self, content: str) -> str:
        """清理AI响应内容，移除思考标签和其他非JSON内容"""
        import re

        # 移除 <think>...</think> 标签及其内容
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)

        # 移除其他可能的XML标签
        content = re.sub(r'<[^>]+>', '', content)

        # 移除多余的空白字符
        content = content.strip()

        # 尝试找到JSON部分
        # 查找第一个 { 和最后一个 }
        start_idx = content.find('{')
        end_idx = content.rfind('}')

        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            content = content[start_idx:end_idx + 1]

        return content

    async def analyze_users_batch(self, users: List[BilibiliUser]) -> List[AIAnalysisResult]:
        """批量分析用户"""
        if not users:
            return []
        
        async with self.throttler:
            try:
                prompt = self._build_analysis_prompt(users)
                
                logger.info(f"Analyzing {len(users)} users with AI")
                
                response = await self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的内容分类专家，擅长根据用户名和签名信息对B站UP主进行准确分类。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from AI")

                # 处理思考模型的响应格式，移除 <think></think> 标签
                cleaned_content = self._clean_ai_response(content)

                # 解析JSON响应
                try:
                    result_data = json.loads(cleaned_content)
                    results = result_data.get("results", [])
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse AI response as JSON: {e}")
                    logger.error(f"Original content: {content}")
                    logger.error(f"Cleaned content: {cleaned_content}")
                    # 如果解析失败，返回未知分类
                    return [
                        AIAnalysisResult(
                            mid=user.mid,
                            uname=user.uname,
                            sign=user.sign,
                            category="未知",
                            confidence=0.0,
                            reason="AI响应解析失败"
                        )
                        for user in users
                    ]
                
                # 构建结果映射
                result_map = {result["uname"]: result for result in results}
                
                # 为每个用户生成分析结果
                analysis_results = []
                for user in users:
                    if user.uname in result_map:
                        result = result_map[user.uname]
                        category = result.get("category", "未知")
                        
                        # 验证分类是否在预定义列表中
                        if category not in self.PREDEFINED_CATEGORIES:
                            logger.warning(f"Unknown category '{category}' for user {user.uname}, using '未知'")
                            category = "未知"
                        
                        analysis_results.append(AIAnalysisResult(
                            mid=user.mid,
                            uname=user.uname,
                            sign=user.sign,
                            category=category,
                            confidence=float(result.get("confidence", 0.0)),
                            reason=result.get("reason", "")
                        ))
                    else:
                        # 如果AI没有返回该用户的结果，标记为未知
                        analysis_results.append(AIAnalysisResult(
                            mid=user.mid,
                            uname=user.uname,
                            sign=user.sign,
                            category="未知",
                            confidence=0.0,
                            reason="AI未返回分析结果"
                        ))
                
                logger.info(f"Successfully analyzed {len(analysis_results)} users")
                return analysis_results
                
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                # 如果AI分析失败，返回未知分类
                return [
                    AIAnalysisResult(
                        mid=user.mid,
                        uname=user.uname,
                        sign=user.sign,
                        category="未知",
                        confidence=0.0,
                        reason=f"AI分析失败: {str(e)}"
                    )
                    for user in users
                ]
    
    async def analyze_all_users(self, users: List[BilibiliUser], batch_size: Optional[int] = None) -> List[AIAnalysisResult]:
        """分析所有用户，分批处理"""
        # 如果没有指定批次大小，使用配置中的默认值
        if batch_size is None:
            batch_size = self.config.ai_batch_size

        all_results = []

        # 分批处理用户
        for i in range(0, len(users), batch_size):
            batch = users[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}/{(len(users) + batch_size - 1) // batch_size}")
            
            try:
                batch_results = await self.analyze_users_batch(batch)
                all_results.extend(batch_results)

                # 更新进度
                current_progress = min(i + batch_size, len(users))
                if self.progress_callback:
                    self.progress_callback("AI分析分类", current_progress, len(users))

                logger.info(f"已分析 {current_progress}/{len(users)} 个用户")

                # 添加延迟避免请求过于频繁
                if i + batch_size < len(users):
                    await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"Failed to analyze batch {i // batch_size + 1}: {e}")
                # 为失败的批次添加未知分类
                for user in batch:
                    all_results.append(AIAnalysisResult(
                        mid=user.mid,
                        uname=user.uname,
                        sign=user.sign,
                        category="未知",
                        confidence=0.0,
                        reason=f"批次分析失败: {str(e)}"
                    ))
        
        return all_results
    
    def group_by_category(self, analysis_results: List[AIAnalysisResult]) -> Dict[str, List[AIAnalysisResult]]:
        """按分类分组结果"""
        groups = {}
        for result in analysis_results:
            category = result.category
            if category not in groups:
                groups[category] = []
            groups[category].append(result)
        
        # 按分组大小排序
        sorted_groups = dict(sorted(groups.items(), key=lambda x: len(x[1]), reverse=True))
        
        logger.info(f"Grouped users into {len(sorted_groups)} categories:")
        for category, results in sorted_groups.items():
            logger.info(f"  {category}: {len(results)} users")
        
        return sorted_groups
    
    def get_statistics(self, analysis_results: List[AIAnalysisResult]) -> Dict[str, Any]:
        """获取分析统计信息"""
        total = len(analysis_results)
        if total == 0:
            return {"total": 0, "categories": {}, "unknown_count": 0, "success_rate": 0.0}
        
        categories = {}
        unknown_count = 0
        
        for result in analysis_results:
            category = result.category
            if category == "未知":
                unknown_count += 1
            
            if category not in categories:
                categories[category] = {"count": 0, "avg_confidence": 0.0}
            
            categories[category]["count"] += 1
        
        # 计算平均置信度
        for category in categories:
            category_results = [r for r in analysis_results if r.category == category]
            if category_results:
                avg_confidence = sum(r.confidence for r in category_results) / len(category_results)
                categories[category]["avg_confidence"] = avg_confidence
        
        success_rate = (total - unknown_count) / total * 100 if total > 0 else 0.0
        
        return {
            "total": total,
            "categories": categories,
            "unknown_count": unknown_count,
            "success_rate": success_rate
        }
