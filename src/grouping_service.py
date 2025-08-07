"""
智能分组服务 - 核心业务逻辑
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from .models import (
    BilibiliUser, AIAnalysisResult, GroupingTask, 
    Statistics, Config
)
from .bilibili_client import BilibiliClient
from .ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)


class GroupingService:
    """智能分组服务"""
    
    def __init__(self, config: Config):
        self.config = config
        self.statistics = Statistics()
        self.progress_callback: Optional[Callable[[str, int, int], None]] = None
    
    def set_progress_callback(self, callback: Callable[[str, int, int], None]):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def _update_progress(self, stage: str, current: int, total: int):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(stage, current, total)
    
    async def fetch_all_followings(self, client: BilibiliClient) -> List[BilibiliUser]:
        """获取所有关注用户"""
        logger.info("开始获取关注列表...")
        self._update_progress("获取关注列表", 0, 100)
        
        try:
            users = await client.get_all_followings()
            self.statistics.total_users = len(users)
            
            logger.info(f"成功获取 {len(users)} 个关注用户")
            self._update_progress("获取关注列表", 100, 100)
            
            return users
        except Exception as e:
            logger.error(f"获取关注列表失败: {e}")
            raise
    
    async def analyze_users(self, analyzer: AIAnalyzer, users: List[BilibiliUser]) -> List[AIAnalysisResult]:
        """分析用户分类"""
        logger.info("开始AI分析用户分类...")
        self._update_progress("AI分析分类", 0, len(users))
        
        try:
            # 过滤掉没有用户名的用户
            valid_users = [user for user in users if user.uname.strip()]
            if len(valid_users) < len(users):
                logger.warning(f"过滤掉 {len(users) - len(valid_users)} 个无效用户")
            
            # 设置进度回调并使用配置中的批次大小进行分析
            analyzer.set_progress_callback(self._update_progress)
            results = await analyzer.analyze_all_users(valid_users)
            
            self.statistics.analyzed_users = len(results)
            
            # 统计未知分类数量
            unknown_count = sum(1 for r in results if r.category == "未知")
            self.statistics.unknown_users = unknown_count
            
            logger.info(f"AI分析完成，成功分类 {len(results) - unknown_count}/{len(results)} 个用户")
            return results
            
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            raise
    
    async def create_groups_and_assign(self, client: BilibiliClient, analysis_results: List[AIAnalysisResult]) -> Dict[str, GroupingTask]:
        """创建分组并分配用户"""
        logger.info("开始创建分组并分配用户...")
        
        # 按分类分组
        analyzer = AIAnalyzer(self.config)  # 临时创建用于分组
        category_groups = analyzer.group_by_category(analysis_results)
        
        # 过滤掉"未知"分类和用户数量太少的分类
        min_users_per_group = 2  # 最少2个用户才创建分组
        filtered_groups = {
            category: results 
            for category, results in category_groups.items() 
            if category != "未知" and len(results) >= min_users_per_group
        }
        
        if not filtered_groups:
            logger.warning("没有足够的用户创建分组")
            return {}
        
        logger.info(f"将创建 {len(filtered_groups)} 个分组")
        
        # 获取现有分组
        existing_tags = await client.check_existing_tags()
        
        grouping_tasks = {}
        total_groups = len(filtered_groups)
        current_group = 0
        
        for category, results in filtered_groups.items():
            current_group += 1
            self._update_progress("创建分组", current_group, total_groups)
            
            try:
                # 确保分组存在
                tag_id = await client.ensure_tag_exists(category, existing_tags)
                
                # 创建分组任务
                users = []
                for result in results:
                    # 从原始用户列表中找到对应用户
                    user = BilibiliUser(
                        mid=result.mid,
                        uname=result.uname,
                        sign=result.sign
                    )
                    users.append(user)
                
                task = GroupingTask(
                    category=category,
                    users=users,
                    tagid=tag_id,
                    created=True,
                    grouped=False
                )
                
                grouping_tasks[category] = task
                logger.info(f"准备将 {len(users)} 个用户分配到分组 '{category}' (ID: {tag_id})")
                
            except Exception as e:
                logger.error(f"创建分组 '{category}' 失败: {e}")
                continue
        
        self.statistics.created_groups = len(grouping_tasks)
        return grouping_tasks
    
    async def execute_batch_grouping(self, client: BilibiliClient, grouping_tasks: Dict[str, GroupingTask]):
        """执行批量分组"""
        logger.info("开始执行批量分组...")
        
        total_tasks = len(grouping_tasks)
        current_task = 0
        total_grouped_users = 0
        
        for category, task in grouping_tasks.items():
            current_task += 1
            self._update_progress("批量分组", current_task, total_tasks)
            
            try:
                if not task.tagid:
                    logger.error(f"分组 '{category}' 没有有效的tag_id")
                    continue
                
                # 提取用户ID
                user_mids = [user.mid for user in task.users]
                
                # 分批处理，避免单次请求用户过多
                batch_size = 50  # 每批最多50个用户
                
                for i in range(0, len(user_mids), batch_size):
                    batch_mids = user_mids[i:i + batch_size]
                    
                    try:
                        await client.batch_group_users(batch_mids, task.tagid)
                        logger.info(f"成功将 {len(batch_mids)} 个用户分配到分组 '{category}'")
                        
                        # 添加延迟避免请求过于频繁
                        if i + batch_size < len(user_mids):
                            await asyncio.sleep(1)
                            
                    except Exception as e:
                        logger.error(f"批量分组失败 (分组: {category}, 批次: {i//batch_size + 1}): {e}")
                        continue
                
                task.grouped = True
                total_grouped_users += len(task.users)
                logger.info(f"分组 '{category}' 完成，共分配 {len(task.users)} 个用户")
                
            except Exception as e:
                logger.error(f"分组 '{category}' 执行失败: {e}")
                continue
        
        self.statistics.grouped_users = total_grouped_users
        logger.info(f"批量分组完成，共分配 {total_grouped_users} 个用户到 {len(grouping_tasks)} 个分组")
    
    async def run_intelligent_grouping(self, dry_run: bool = False) -> Statistics:
        """运行智能分组流程"""
        self.statistics.start_time = datetime.now()
        
        try:
            logger.info("开始智能分组流程...")
            
            # 初始化客户端和分析器
            async with BilibiliClient(self.config) as client:
                analyzer = AIAnalyzer(self.config)
                
                # 步骤1: 获取关注列表
                users = await self.fetch_all_followings(client)
                if not users:
                    logger.warning("没有获取到关注用户")
                    return self.statistics
                
                # 步骤2: AI分析分类
                analysis_results = await self.analyze_users(analyzer, users)
                if not analysis_results:
                    logger.warning("没有分析结果")
                    return self.statistics
                
                # 如果是试运行，只显示分析结果
                if dry_run:
                    logger.info("试运行模式，不执行实际分组操作")
                    self._print_analysis_summary(analysis_results)
                    return self.statistics
                
                # 步骤3: 创建分组
                grouping_tasks = await self.create_groups_and_assign(client, analysis_results)
                if not grouping_tasks:
                    logger.warning("没有创建任何分组")
                    return self.statistics
                
                # 步骤4: 执行批量分组
                await self.execute_batch_grouping(client, grouping_tasks)
                
                logger.info("智能分组流程完成!")
                
        except Exception as e:
            logger.error(f"智能分组流程失败: {e}")
            raise
        finally:
            self.statistics.end_time = datetime.now()
        
        return self.statistics
    
    def _print_analysis_summary(self, analysis_results: List[AIAnalysisResult]):
        """打印分析摘要"""
        analyzer = AIAnalyzer(self.config)
        category_groups = analyzer.group_by_category(analysis_results)
        
        logger.info("=== 分析结果摘要 ===")
        for category, results in category_groups.items():
            logger.info(f"{category}: {len(results)} 个用户")
            # 显示前几个用户作为示例
            for i, result in enumerate(results[:3]):
                logger.info(f"  - {result.uname} (置信度: {result.confidence:.2f})")
            if len(results) > 3:
                logger.info(f"  ... 还有 {len(results) - 3} 个用户")
    
    def get_final_statistics(self) -> Dict[str, Any]:
        """获取最终统计信息"""
        stats = {
            "总用户数": self.statistics.total_users,
            "已分析用户数": self.statistics.analyzed_users,
            "创建分组数": self.statistics.created_groups,
            "已分组用户数": self.statistics.grouped_users,
            "未知分类用户数": self.statistics.unknown_users,
            "成功率": f"{self.statistics.success_rate:.1f}%"
        }
        
        if self.statistics.duration:
            stats["执行时长"] = f"{self.statistics.duration:.1f}秒"
        
        return stats
