#!/usr/bin/env python3
"""
Manual release creation script
Use this if GitHub Actions has permission issues
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run command and return result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output,
            text=True,
            check=True
        )
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr if capture_output else str(e)

def check_gh_cli():
    """Check if GitHub CLI is installed"""
    success, output = run_command("gh --version")
    if success:
        print(f"✅ GitHub CLI found: {output.strip().split()[0]}")
        return True
    else:
        print("❌ GitHub CLI not found. Please install it:")
        print("   https://cli.github.com/")
        return False

def check_git_status():
    """Check git status and get current tag"""
    # Check if we're in a git repository
    success, _ = run_command("git status")
    if not success:
        print("❌ Not in a git repository")
        return None
    
    # Get current tag
    success, tag = run_command("git describe --tags --exact-match HEAD")
    if success:
        tag = tag.strip()
        print(f"✅ Current tag: {tag}")
        return tag
    else:
        print("⚠️  No tag found on current commit")
        # Get latest tag
        success, latest_tag = run_command("git describe --tags --abbrev=0")
        if success:
            latest_tag = latest_tag.strip()
            print(f"📋 Latest tag: {latest_tag}")
            use_latest = input(f"Use latest tag '{latest_tag}'? (y/N): ").lower()
            if use_latest == 'y':
                return latest_tag
        
        # Manual tag input
        manual_tag = input("Enter tag name (e.g., v1.0.0): ").strip()
        if manual_tag:
            return manual_tag
        
        return None

def check_release_files():
    """Check if release files exist"""
    release_dir = Path("release")
    if not release_dir.exists():
        print("❌ Release directory not found. Run build.py first.")
        return False
    
    required_files = [
        "bilibili-ai-partition.exe",
        "README.md",
        "requirements.txt",
        ".env.example",
        "Usage-Instructions.txt"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = release_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            size_mb = size / (1024 * 1024)
            print(f"✅ {file} ({size_mb:.1f} MB)")
        else:
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def create_release(tag):
    """Create GitHub release"""
    print(f"\n🚀 Creating release for tag: {tag}")
    
    # Create release with files
    cmd = [
        "gh", "release", "create", tag,
        "release/bilibili-ai-partition.exe",
        "release/README.md", 
        "release/requirements.txt",
        "release/.env.example",
        "release/Usage-Instructions.txt",
        "--title", f"Release {tag}",
        "--notes", f"""## 🎉 bilibili-ai-partition {tag}

### 📦 Quick Start
1. Download `bilibili-ai-partition.exe`
2. Double-click to run
3. Follow the configuration wizard
4. Start intelligent grouping

### ✨ Features
- 🤖 AI-powered UP analysis
- 📊 Automatic group creation and assignment
- 🔍 Dry-run mode for testing
- ⚙️ Configurable AI batch size

### 🔒 Security Notes
- Keep your Cookie and API keys secure
- Don't use in public environments
- Regularly rotate your credentials

### 📋 Files Included
- `bilibili-ai-partition.exe` - Main executable (~23MB)
- `README.md` - Detailed documentation
- `requirements.txt` - Dependencies list
- `.env.example` - Configuration template
- `Usage-Instructions.txt` - Quick usage guide
"""
    ]
    
    print("Running:", " ".join(cmd[:5]) + " ...")
    success, output = run_command(" ".join(cmd), capture_output=False)
    
    if success:
        print(f"✅ Release {tag} created successfully!")
        print(f"🔗 View at: https://github.com/{get_repo_info()}/releases/tag/{tag}")
        return True
    else:
        print(f"❌ Failed to create release: {output}")
        return False

def get_repo_info():
    """Get repository owner/name"""
    success, output = run_command("gh repo view --json owner,name")
    if success:
        try:
            repo_data = json.loads(output)
            return f"{repo_data['owner']['login']}/{repo_data['name']}"
        except:
            pass
    
    # Fallback to git remote
    success, output = run_command("git remote get-url origin")
    if success:
        url = output.strip()
        if "github.com" in url:
            # Extract owner/repo from URL
            if url.endswith(".git"):
                url = url[:-4]
            parts = url.split("/")
            if len(parts) >= 2:
                return f"{parts[-2]}/{parts[-1]}"
    
    return "unknown/unknown"

def main():
    """Main function"""
    print("🏷️  Manual GitHub Release Creator")
    print("=" * 50)
    
    # Check prerequisites
    if not check_gh_cli():
        return 1
    
    # Check git status and get tag
    tag = check_git_status()
    if not tag:
        print("❌ No tag specified")
        return 1
    
    # Check release files
    if not check_release_files():
        print("\n💡 Run 'python build.py' to create release files")
        return 1
    
    # Confirm creation
    print(f"\n📋 Ready to create release:")
    print(f"   Tag: {tag}")
    print(f"   Repository: {get_repo_info()}")
    print(f"   Files: 5 files in release/ directory")
    
    confirm = input("\nProceed with release creation? (y/N): ").lower()
    if confirm != 'y':
        print("❌ Release creation cancelled")
        return 1
    
    # Create release
    if create_release(tag):
        print("\n🎉 Release created successfully!")
        return 0
    else:
        print("\n❌ Release creation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
