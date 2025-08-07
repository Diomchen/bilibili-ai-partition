#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple build script for GitHub Actions
Avoids all unicode characters that might cause encoding issues
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return result"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            check=True, 
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return False

def clean_build():
    """Clean build directories"""
    print("Cleaning build directories...")
    
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed: {dir_name}")

def build_executable():
    """Build executable using spec file"""
    print("Building executable...")
    
    spec_file = "bilibili-ai-partition-simple.spec"
    if not os.path.exists(spec_file):
        print(f"Spec file not found: {spec_file}")
        return False
    
    print(f"Using spec file: {spec_file}")
    return run_command(f"pyinstaller {spec_file}")

def create_release_package():
    """Create release package"""
    print("Creating release package...")
    
    # Create release directory
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Copy executable
    exe_path = Path("dist/bilibili-ai-partition.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / "bilibili-ai-partition.exe")
        print(f"Copied executable: {exe_path}")
    else:
        print("Executable not found")
        return False
    
    # Copy other files
    files_to_copy = [
        "README.md",
        "requirements.txt"
    ]
    
    # Copy .env.example if it exists
    if os.path.exists(".env.example"):
        files_to_copy.append(".env.example")
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, release_dir / file_name)
            print(f"  Copied: {file_name}")
    
    # Create usage instructions in English to avoid encoding issues
    usage_text = """# bilibili-ai-partition Usage Instructions

## Quick Start

1. Double-click bilibili-ai-partition.exe to run
2. Follow the configuration wizard on first run
3. Complete the setup as prompted
4. Start intelligent grouping

## Command Line Usage

```bash
# Show help
bilibili-ai-partition.exe --help

# Configuration wizard
bilibili-ai-partition.exe setup

# Start grouping (dry run)
bilibili-ai-partition.exe run --dry-run

# Actual grouping
bilibili-ai-partition.exe run

# Check configuration status
bilibili-ai-partition.exe status
```

## Configuration Files

- .env - Main configuration file (copy from .env.example and modify)
- ai_config.json - AI configuration (auto-generated)

## Environment Variables

You can adjust behavior by setting environment variables:

- AI_BATCH_SIZE - AI analysis batch size (default 10)
- LOG_LEVEL - Log level (DEBUG/INFO/WARNING/ERROR)

## Notes

1. First-time use requires configuring Bilibili Cookie and AI API key
2. Recommend using --dry-run mode for testing first
3. Large number of followed users may take longer to process
4. Ensure stable network connection

## Troubleshooting

If you encounter issues, please check:
1. Network connection is normal
2. Cookie is valid
3. AI API configuration is correct
4. Check log files for detailed error information
"""
    
    usage_file = release_dir / "Usage-Instructions.txt"
    with open(usage_file, "w", encoding="utf-8") as f:
        f.write(usage_text)
    
    print(f"Release package created: {release_dir}")
    return True

def main():
    """Main function"""
    print("bilibili-ai-partition Simple Build Script")
    print("=" * 50)
    
    # Clean build directories
    clean_build()
    
    # Build executable
    if not build_executable():
        print("Build failed")
        return 1
    
    # Create release package
    if not create_release_package():
        print("Package creation failed")
        return 1
    
    print("\nBuild completed successfully!")
    print("Release files are in release/ directory")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
