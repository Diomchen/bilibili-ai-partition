#!/usr/bin/env python3
"""
项目清理脚本
清理构建文件、缓存文件和临时文件
"""
import os
import shutil
import glob
from pathlib import Path

def clean_directory(path, description):
    """清理目录"""
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"✅ 已清理: {description} ({path})")
        except Exception as e:
            print(f"❌ 清理失败: {description} ({path}) - {e}")
    else:
        print(f"⚪ 不存在: {description} ({path})")

def clean_files(pattern, description):
    """清理匹配模式的文件"""
    files = glob.glob(pattern, recursive=True)
    if files:
        for file in files:
            try:
                os.remove(file)
                print(f"✅ 已删除: {file}")
            except Exception as e:
                print(f"❌ 删除失败: {file} - {e}")
        print(f"✅ 已清理: {description} ({len(files)} 个文件)")
    else:
        print(f"⚪ 未找到: {description}")

def main():
    """主清理函数"""
    print("🧹 开始清理项目...")
    print("=" * 50)
    
    # 清理构建目录
    clean_directory("build", "构建临时目录")
    clean_directory("dist", "分发目录")
    
    # 清理Python缓存
    clean_directory("src/__pycache__", "Python缓存")
    clean_files("**/__pycache__", "所有Python缓存目录")
    clean_files("**/*.pyc", "Python字节码文件")
    clean_files("**/*.pyo", "Python优化字节码文件")
    
    # 清理日志文件
    clean_files("*.log", "日志文件")
    clean_files("logs/*.log", "日志目录文件")
    
    # 清理临时文件
    clean_files("*.tmp", "临时文件")
    clean_files("temp/*", "临时目录文件")
    clean_files("tmp/*", "临时目录文件")
    
    # 清理IDE文件
    clean_directory(".vscode", "VSCode配置")
    clean_directory(".idea", "PyCharm配置")
    clean_files("*.swp", "Vim交换文件")
    clean_files("*.swo", "Vim交换文件")
    
    # 清理OS文件
    clean_files(".DS_Store", "macOS系统文件")
    clean_files("Thumbs.db", "Windows缩略图文件")
    clean_files("ehthumbs.db", "Windows缩略图文件")
    
    print("=" * 50)
    print("🎉 清理完成！")
    
    # 显示当前项目结构
    print("\n📁 当前项目结构:")
    for root, dirs, files in os.walk("."):
        # 跳过隐藏目录和release目录的详细内容
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'release']
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            if not file.startswith('.'):
                print(f"{subindent}{file}")

if __name__ == "__main__":
    main()
