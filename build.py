#!/usr/bin/env python3
"""
bilibili-ai-partition 打包脚本
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并显示输出"""
    print(f"🔧 执行: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8'
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        if e.stdout:
            print("标准输出:", e.stdout)
        if e.stderr:
            print("错误输出:", e.stderr)
        return False

def check_requirements():
    """检查构建要求"""
    print("📋 检查构建要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ 未安装PyInstaller，正在安装...")
        if not run_command("pip install pyinstaller"):
            return False
    
    # 检查UPX（可选）
    try:
        result = subprocess.run("upx --version", shell=True, capture_output=True)
        if result.returncode == 0:
            print("✅ UPX可用，将启用压缩")
        else:
            print("⚠️  UPX不可用，跳过压缩")
    except:
        print("⚠️  UPX不可用，跳过压缩")
    
    return True

def clean_build():
    """清理构建目录"""
    print("🧹 清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  删除: {dir_name}")
    
    # 清理.pyc文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")

    # 确保pip是最新版本
    if not run_command("python -m pip install --upgrade pip"):
        print("⚠️  pip升级失败，继续使用当前版本")

    # 安装项目依赖
    if not run_command("pip install -r requirements.txt"):
        print("❌ 依赖安装失败")
        return False

    # 确保PyInstaller已安装
    try:
        import PyInstaller
        print(f"✅ PyInstaller已安装: {PyInstaller.__version__}")
    except ImportError:
        print("📦 安装PyInstaller...")
        if not run_command("pip install pyinstaller>=5.13.0"):
            return False

    return True

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")

    # 首先尝试简单的spec文件
    spec_files = [
        "bilibili-ai-partition-simple.spec",
        "bilibili-ai-partition.spec"
    ]

    for spec_file in spec_files:
        if os.path.exists(spec_file):
            print(f"📄 使用spec文件: {spec_file}")
            if run_command(f"pyinstaller {spec_file}"):
                return True
            else:
                print(f"⚠️  使用 {spec_file} 构建失败，尝试下一个...")

    # 如果spec文件都失败，尝试直接命令行构建
    print("📄 尝试直接命令行构建...")
    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",
        "--name", "bilibili-ai-partition",
        "--add-data", ".env.example;.",
        "--add-data", "README.md;.",
        "--add-data", "requirements.txt;.",
        "--hidden-import", "src.cli",
        "--hidden-import", "src.config_manager",
        "--hidden-import", "src.grouping_service",
        "--hidden-import", "src.bilibili_client",
        "--hidden-import", "src.ai_analyzer",
        "--hidden-import", "src.interactive_config",
        "--hidden-import", "src.models",
        "--hidden-import", "src.utils",
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "pandas",
        "main.py"
    ]

    if run_command(" ".join(cmd)):
        return True

    print("❌ 所有构建方法都失败了")
    return False

def create_release_package():
    """创建发布包"""
    print("📦 创建发布包...")
    
    # 创建发布目录
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制可执行文件
    exe_path = Path("dist/bilibili-ai-partition.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / "bilibili-ai-partition.exe")
        print(f"✅ 复制可执行文件: {exe_path}")
    else:
        print("❌ 找不到可执行文件")
        return False
    
    # 复制必要文件
    files_to_copy = [
        ".env.example",
        "README.md",
        "requirements.txt"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, release_dir / file_name)
            print(f"  复制: {file_name}")
    
    # 创建使用说明
    usage_text = """# bilibili-ai-partition 使用说明

## 快速开始

1. 双击运行 `bilibili-ai-partition.exe`
2. 首次运行会显示配置向导
3. 按照提示完成配置
4. 开始智能分组

## 命令行使用

```bash
# 显示帮助
bilibili-ai-partition.exe --help

# 配置向导
bilibili-ai-partition.exe setup

# 开始分组（试运行）
bilibili-ai-partition.exe run --dry-run

# 正式分组
bilibili-ai-partition.exe run

# 查看配置状态
bilibili-ai-partition.exe status
```

## 配置文件

- `.env` - 主配置文件（从 .env.example 复制并修改）
- `ai_config.json` - AI配置（自动生成）

## 环境变量

可以通过设置环境变量来调整行为：

- `AI_BATCH_SIZE` - AI分析批次大小（默认10）
- `LOG_LEVEL` - 日志级别（DEBUG/INFO/WARNING/ERROR）

## 注意事项

1. 首次使用需要配置B站Cookie和AI API密钥
2. 建议先使用 `--dry-run` 模式测试
3. 大量关注用户可能需要较长时间处理
4. 确保网络连接稳定

## 问题反馈

如遇到问题，请检查：
1. 网络连接是否正常
2. Cookie是否有效
3. AI API配置是否正确
4. 查看日志文件获取详细错误信息
"""
    
    with open(release_dir / "使用说明.txt", "w", encoding="utf-8") as f:
        f.write(usage_text)
    
    print(f"✅ 发布包创建完成: {release_dir}")
    return True

def main():
    """主函数"""
    print("🚀 bilibili-ai-partition 构建脚本")
    print("=" * 50)
    
    # 检查构建要求
    if not check_requirements():
        print("❌ 构建要求检查失败")
        return 1
    
    # 清理构建目录
    clean_build()
    
    # 安装依赖
    if not install_dependencies():
        return 1
    
    # 构建可执行文件
    if not build_executable():
        return 1
    
    # 创建发布包
    if not create_release_package():
        return 1
    
    print("\n🎉 构建完成！")
    print("📁 发布文件位于 release/ 目录")
    print("💡 可以将整个 release/ 目录分发给用户")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
