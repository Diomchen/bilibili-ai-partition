"""
命令行界面
"""
import asyncio
import sys
import os
from typing import Optional
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm

from .config_manager import ConfigManager, setup_logging, get_cookie_instructions, ErrorHandler
from .grouping_service import GroupingService
from .interactive_config import InteractiveConfig
from .models import Config

console = Console()

def show_banner():
    """显示程序横幅"""
    banner = """
╭─────────────────────────────────────────────────────────────╮
│                                                             │
│    🤖 哔哩哔哩关注列表智能分组工具                          │
│       bilibili-ai-partition v1.0.0                         │
│                                                             │
│    ✨ 使用AI智能分析并自动分组你的B站关注列表                │
│    🎯 支持多种分类：科技、游戏、音乐、美食等40+类别          │
│    ⚡ 高效批量处理，可配置分析批次大小                      │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
    """
    console.print(banner, style="bold cyan")

def show_help_info():
    """显示帮助信息"""
    help_text = """
📖 使用说明:
  • 首次运行需要配置B站Cookie和AI API
  • 支持试运行模式，不会实际修改分组
  • 可通过环境变量 AI_BATCH_SIZE 调整批次大小

🔧 配置文件:
  • .env - 环境变量配置
  • ai_config.json - AI配置（自动生成）

💡 提示: 使用 --help 查看所有命令选项
    """
    console.print(Panel(help_text, title="帮助信息", border_style="blue"))

def handle_exit():
    """处理程序退出"""
    console.print("\n👋 感谢使用 bilibili-ai-partition！", style="bold green")
    console.print("如有问题或建议，欢迎反馈 💬")

    # 在Windows下暂停，让用户看到消息
    if sys.platform == 'win32':
        try:
            input("\n按回车键退出...")
        except:
            pass

def interactive_main_menu(ctx):
    """交互式主菜单"""
    while True:
        try:
            # 显示主菜单
            console.print("\n" + "="*60)
            console.print("🎯 请选择操作:", style="bold cyan")
            console.print()
            console.print("1️⃣  配置向导 (首次使用)")
            console.print("2️⃣  查看配置状态")
            console.print("3️⃣  配置AI分析设置")
            console.print("4️⃣  开始智能分组 (试运行)")
            console.print("5️⃣  开始智能分组 (正式运行)")
            console.print("6️⃣  显示Cookie获取帮助")
            console.print("7️⃣  显示工具信息")
            console.print("0️⃣  退出程序")
            console.print("="*60)

            # 获取用户选择
            choice = Prompt.ask(
                "\n请输入选项编号",
                choices=["0", "1", "2", "3", "4", "5", "6", "7"],
                default="1"
            )

            # 执行对应操作
            if choice == "0":
                console.print("\n👋 再见！", style="bold green")
                break
            elif choice == "1":
                console.print("\n🚀 启动配置向导...", style="bold blue")
                ctx.invoke(setup)
            elif choice == "2":
                console.print("\n📊 查看配置状态...", style="bold blue")
                ctx.invoke(status)
            elif choice == "3":
                console.print("\n⚙️ 配置AI分析设置...", style="bold blue")
                configure_ai_settings(ctx)
            elif choice == "4":
                console.print("\n🧪 开始试运行...", style="bold yellow")
                ctx.invoke(run, dry_run=True)
            elif choice == "5":
                # 确认正式运行
                if Confirm.ask("\n⚠️  确定要开始正式分组吗？这将实际修改你的B站关注分组"):
                    console.print("\n🚀 开始正式分组...", style="bold green")
                    ctx.invoke(run, dry_run=False)
                else:
                    console.print("已取消操作", style="yellow")
            elif choice == "6":
                console.print("\n📖 Cookie获取帮助...", style="bold blue")
                ctx.invoke(cookie_help)
            elif choice == "7":
                console.print("\n ℹ️ 工具信息...", style="bold blue")
                ctx.invoke(info)

            # 操作完成后询问是否继续
            if choice != "0":
                console.print("\n" + "-"*60)
                if not Confirm.ask("是否继续使用", default=True):
                    console.print("\n👋 再见！", style="bold green")
                    break

        except KeyboardInterrupt:
            console.print("\n\n⚠️  用户取消操作", style="yellow")
            break
        except Exception as e:
            console.print(f"\n❌ 操作出错: {e}", style="red")
            if not Confirm.ask("是否继续", default=True):
                break

def configure_ai_settings(ctx):
    """配置AI分析设置"""
    try:
        from src.config_manager import ConfigManager
        import os

        config_manager = ConfigManager()

        # 显示当前设置
        console.print("\n" + "="*50)
        console.print("⚙️ AI分析设置配置", style="bold cyan")
        console.print("="*50)

        # 获取当前AI批次大小
        current_batch_size = int(os.getenv("AI_BATCH_SIZE", "10"))
        console.print(f"\n📊 当前AI批次大小: {current_batch_size}")

        # 显示说明
        console.print("\n💡 AI批次大小说明:")
        console.print("  • 批次大小决定AI每次分析多少个用户")
        console.print("  • 较大批次: 处理更快，但API成本更高")
        console.print("  • 较小批次: 更安全，但处理时间更长")
        console.print("\n📋 推荐设置:")
        console.print("  • 测试环境: 5-8 个用户/批次")
        console.print("  • 正常使用: 10-15 个用户/批次")
        console.print("  • 大量用户: 20-30 个用户/批次")

        # 让用户选择是否修改
        if not Confirm.ask(f"\n是否要修改当前的批次大小 ({current_batch_size})", default=False):
            console.print("保持当前设置不变", style="yellow")
            return

        # 获取新的批次大小
        while True:
            try:
                new_batch_size = Prompt.ask(
                    "\n请输入新的AI批次大小",
                    default=str(current_batch_size)
                )

                new_batch_size = int(new_batch_size)

                if new_batch_size < 1:
                    console.print("❌ 批次大小必须大于0", style="red")
                    continue
                elif new_batch_size > 50:
                    console.print("⚠️  批次大小过大可能导致API超时", style="yellow")
                    if not Confirm.ask("确定要使用这个大小吗", default=False):
                        continue

                break

            except ValueError:
                console.print("❌ 请输入有效的数字", style="red")

        # 确认修改
        console.print(f"\n📝 将要修改:")
        console.print(f"  当前批次大小: {current_batch_size}")
        console.print(f"  新的批次大小: {new_batch_size}")

        if new_batch_size != current_batch_size:
            if Confirm.ask("\n确认修改", default=True):
                # 设置环境变量
                os.environ["AI_BATCH_SIZE"] = str(new_batch_size)

                # 尝试更新.env文件
                try:
                    env_file = ".env"
                    if os.path.exists(env_file):
                        # 读取现有内容
                        with open(env_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()

                        # 查找并更新AI_BATCH_SIZE行
                        updated = False
                        for i, line in enumerate(lines):
                            if line.strip().startswith('AI_BATCH_SIZE='):
                                lines[i] = f'AI_BATCH_SIZE={new_batch_size}\n'
                                updated = True
                                break

                        # 如果没找到，添加新行
                        if not updated:
                            lines.append(f'\nAI_BATCH_SIZE={new_batch_size}\n')

                        # 写回文件
                        with open(env_file, 'w', encoding='utf-8') as f:
                            f.writelines(lines)

                        console.print(f"✅ 已更新 .env 文件", style="green")
                    else:
                        # 创建新的.env文件
                        with open(env_file, 'w', encoding='utf-8') as f:
                            f.write(f'AI_BATCH_SIZE={new_batch_size}\n')
                        console.print(f"✅ 已创建 .env 文件", style="green")

                except Exception as e:
                    console.print(f"⚠️  无法更新.env文件: {e}", style="yellow")
                    console.print("设置仅在本次运行中生效", style="yellow")

                console.print(f"✅ AI批次大小已设置为: {new_batch_size}", style="green")
                console.print("\n💡 提示: 新设置将在下次分析时生效")

            else:
                console.print("已取消修改", style="yellow")
        else:
            console.print("批次大小未改变", style="yellow")

    except Exception as e:
        console.print(f"❌ 配置AI设置时出错: {e}", style="red")


class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self):
        self.progress = None
        self.current_task = None
    
    def start(self):
        """开始进度跟踪"""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        )
        self.progress.start()
    
    def stop(self):
        """停止进度跟踪"""
        if self.progress:
            self.progress.stop()
    
    def update_progress(self, stage: str, current: int, total: int):
        """更新进度"""
        if not self.progress:
            return
        
        if self.current_task is None:
            self.current_task = self.progress.add_task(stage, total=total)
        else:
            self.progress.update(self.current_task, description=stage, completed=current, total=total)


@click.group(invoke_without_command=True)
@click.option('--config', '-c', default='.env', help='配置文件路径')
@click.option('--log-level', default='INFO', help='日志级别')
@click.option('--log-file', help='日志文件路径')
@click.version_option(version="1.0.0", prog_name="bilibili-ai-partition")
@click.pass_context
def cli(ctx, config, log_level, log_file):
    """哔哩哔哩关注列表智能分组工具"""
    ctx.ensure_object(dict)
    ctx.obj['config_file'] = config
    ctx.obj['log_level'] = log_level
    ctx.obj['log_file'] = log_file

    # 设置日志
    setup_logging(log_level, log_file)

    # 显示横幅
    show_banner()

    # 如果没有提供子命令，启动交互式主菜单
    if ctx.invoked_subcommand is None:
        # 注册退出处理
        import atexit
        atexit.register(handle_exit)

        # 启动交互式主菜单
        interactive_main_menu(ctx)


@cli.command()
@click.pass_context
def init(ctx):
    """初始化配置文件"""
    config_file = ctx.obj['config_file']

    console.print(Panel.fit("🚀 初始化配置文件", style="bold blue"))

    config_manager = ConfigManager(config_file)

    # 检查配置文件是否已存在
    if os.path.exists(config_file):
        if not click.confirm(f"配置文件 {config_file} 已存在，是否覆盖？"):
            console.print("❌ 初始化已取消", style="yellow")
            return

    # 创建示例配置文件
    config_manager.create_sample_env_file(config_file)

    console.print(f"✅ 配置文件已创建: {config_file}", style="green")
    console.print("\n📋 请编辑配置文件并填入以下信息：")
    console.print("• BILIBILI_COOKIE: 哔哩哔哩登录Cookie")
    console.print("• OPENAI_API_KEY: OpenAI API密钥")

    if click.confirm("\n是否显示Cookie获取说明？"):
        console.print(Panel(get_cookie_instructions(), title="Cookie获取说明", style="cyan"))


@cli.command()
@click.pass_context
def setup(ctx):
    """交互式配置向导"""
    config_file = ctx.obj['config_file']

    try:
        config_manager = ConfigManager(config_file)
        interactive_config = InteractiveConfig(config_manager)

        # 运行交互式设置
        cookie, ai_config = asyncio.run(interactive_config.run_interactive_setup())

        if cookie and ai_config:
            # 保存Cookie到环境文件
            config_manager.save_bilibili_cookie(cookie)
            console.print("\n🎉 配置完成！现在可以运行工具了", style="green")
        else:
            console.print("\n⚠️  配置未完成，请重新运行setup命令", style="yellow")

    except Exception as e:
        console.print(f"❌ 配置失败: {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """显示配置状态"""
    config_file = ctx.obj['config_file']

    try:
        config_manager = ConfigManager(config_file)
        interactive_config = InteractiveConfig(config_manager)
        interactive_config.show_config_status()

    except Exception as e:
        console.print(f"❌ 检查配置状态失败: {str(e)}", style="red")


@cli.command()
@click.pass_context
def validate(ctx):
    """验证配置"""
    config_file = ctx.obj['config_file']
    
    console.print(Panel.fit("🔍 验证配置", style="bold blue"))
    
    try:
        config_manager = ConfigManager(config_file)
        config = config_manager.create_config_from_env()
        validation_result = config_manager.validate_config(config)
        
        if validation_result['valid']:
            console.print("✅ 配置验证通过", style="green")
            
            # 显示配置摘要
            table = Table(title="配置摘要")
            table.add_column("配置项", style="cyan")
            table.add_column("值", style="white")
            
            table.add_row("用户ID", config.vmid)
            table.add_row("AI模型", config.model_name)
            table.add_row("请求延迟", f"{config.request_delay}秒")
            table.add_row("每页数量", str(config.page_size))
            table.add_row("最大页数", str(config.max_pages))
            
            console.print(table)
        else:
            console.print("❌ 配置验证失败", style="red")
            for issue in validation_result['issues']:
                console.print(f"  • {issue}", style="red")
        
        if validation_result['warnings']:
            console.print("\n⚠️  警告:", style="yellow")
            for warning in validation_result['warnings']:
                console.print(f"  • {warning}", style="yellow")
    
    except Exception as e:
        error_msg = ErrorHandler.handle_config_error(e)
        console.print(f"❌ {error_msg}", style="red")


@cli.command()
@click.option('--dry-run', is_flag=True, help='试运行模式，不执行实际分组操作')
@click.option('--interactive', is_flag=True, help='交互式配置模式')
@click.pass_context
def run(ctx, dry_run, interactive):
    """运行智能分组"""
    config_file = ctx.obj['config_file']

    if dry_run:
        console.print(Panel.fit("🧪 试运行模式 - 智能分组", style="bold yellow"))
    else:
        console.print(Panel.fit("🚀 开始智能分组", style="bold green"))

    try:
        config_manager = ConfigManager(config_file)
        config = None

        # 如果启用交互模式或配置不完整，使用交互式配置
        if interactive:
            interactive_config = InteractiveConfig(config_manager)
            cookie, ai_config = asyncio.run(interactive_config.run_interactive_setup())

            if cookie and ai_config:
                config = config_manager.create_config_interactive(cookie, ai_config)
            else:
                console.print("❌ 交互式配置失败", style="red")
                return
        else:
            # 尝试从环境变量加载配置
            try:
                config = config_manager.create_config_from_env()
            except ValueError as e:
                console.print(f"❌ 配置错误: {e}", style="red")
                console.print("💡 提示: 使用 --interactive 选项进行交互式配置", style="cyan")
                console.print("💡 或者运行 'setup' 命令完成配置", style="cyan")
                return

        # 验证配置
        validation_result = config_manager.validate_config(config)
        if not validation_result['valid']:
            console.print("❌ 配置验证失败，请先修复配置问题", style="red")
            for issue in validation_result['issues']:
                console.print(f"  • {issue}", style="red")
            return

        # 创建服务
        service = GroupingService(config)

        # 设置进度跟踪
        progress_tracker = ProgressTracker()
        service.set_progress_callback(progress_tracker.update_progress)

        # 运行分组
        progress_tracker.start()
        try:
            statistics = asyncio.run(service.run_intelligent_grouping(dry_run))
        finally:
            progress_tracker.stop()

        # 显示结果
        display_results(statistics, service.get_final_statistics(), dry_run)

    except Exception as e:
        console.print(f"❌ 执行失败: {str(e)}", style="red")
        sys.exit(1)


def display_results(statistics, final_stats, dry_run):
    """显示执行结果"""
    if dry_run:
        console.print(Panel.fit("🧪 试运行完成", style="bold yellow"))
    else:
        console.print(Panel.fit("🎉 智能分组完成", style="bold green"))
    
    # 创建结果表格
    table = Table(title="执行统计")
    table.add_column("指标", style="cyan")
    table.add_column("数值", style="white")
    
    for key, value in final_stats.items():
        table.add_row(key, str(value))
    
    console.print(table)
    
    # 显示成功率
    success_rate = statistics.success_rate
    if success_rate >= 80:
        style = "green"
        emoji = "🎯"
    elif success_rate >= 60:
        style = "yellow"
        emoji = "⚠️"
    else:
        style = "red"
        emoji = "❌"
    
    console.print(f"\n{emoji} 分类成功率: {success_rate:.1f}%", style=style)
    
    if not dry_run and statistics.grouped_users > 0:
        console.print(f"✅ 成功分组 {statistics.grouped_users} 个用户到 {statistics.created_groups} 个分组", style="green")


@cli.command()
@click.pass_context
def info(ctx):
    """显示工具信息"""
    console.print(Panel.fit("ℹ️  工具信息", style="bold blue"))
    
    info_text = Text()
    info_text.append("哔哩哔哩关注列表智能分组工具\n", style="bold")
    info_text.append("版本: 1.0.0\n")
    info_text.append("作者: AI Assistant\n\n")
    info_text.append("功能特性:\n", style="bold")
    info_text.append("• 自动获取哔哩哔哩关注列表\n")
    info_text.append("• AI智能分析UP主类型\n")
    info_text.append("• 自动创建分组并批量分配\n")
    info_text.append("• 支持试运行模式\n")
    info_text.append("• 详细的进度跟踪和统计\n\n")
    info_text.append("使用流程:\n", style="bold")
    info_text.append("方式一 (推荐):\n", style="cyan")
    info_text.append("1. bilibili-grouper setup    # 交互式配置向导\n")
    info_text.append("2. bilibili-grouper run      # 运行分组\n\n")
    info_text.append("方式二 (传统):\n", style="cyan")
    info_text.append("1. bilibili-grouper init     # 初始化配置文件\n")
    info_text.append("2. 手动编辑 .env 文件\n")
    info_text.append("3. bilibili-grouper validate # 验证配置\n")
    info_text.append("4. bilibili-grouper run      # 运行分组\n\n")
    info_text.append("其他命令:\n", style="cyan")
    info_text.append("• bilibili-grouper status    # 查看配置状态\n")
    info_text.append("• bilibili-grouper run --interactive  # 临时交互式配置\n")
    
    console.print(Panel(info_text, style="cyan"))


@cli.command()
def cookie_help():
    """显示Cookie获取帮助"""
    console.print(Panel(get_cookie_instructions(), title="Cookie获取说明", style="cyan"))


if __name__ == '__main__':
    cli()
