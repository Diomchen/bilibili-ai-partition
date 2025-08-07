#!/usr/bin/env python3
"""
哔哩哔哩关注列表智能分组工具 (bilibili-ai-partition)
主程序入口
"""
import sys
import os
import traceback
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

def main():
    """主函数，包含错误处理和用户友好的界面"""
    try:
        # 设置控制台编码
        if sys.platform == 'win32':
            import locale
            try:
                # 尝试设置UTF-8编码
                os.system('chcp 65001 >nul 2>&1')
            except:
                pass

        # 导入CLI模块
        from src.cli import cli

        # 运行CLI
        cli()

    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保所有依赖都已正确安装")
        input("\n按回车键退出...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)

if __name__ == '__main__':
    main()
