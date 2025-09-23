#!/usr/bin/env python3
"""
Prepare LinkedIn Ghost Jobs ETL project for GitHub
Cleans temporary files and ensures project is ready for version control
"""

import os
import shutil
from pathlib import Path

def clean_temporary_files():
    """Remove temporary files and directories"""
    project_root = Path(__file__).parent
    
    # Files and directories to clean
    temp_patterns = [
        # Log files
        "logs/*.log*",
        # Database files
        "*.db",
        "*.sqlite*",
        # Temporary data
        "data/raw/*.json",
        "data/transformed/*.json",
        # Notebook temporaries
        "notebooks/*_updated.ipynb",
        "notebooks/executed_*.ipynb",
        "notebooks/conclusion_*.json",
        "notebooks/conclusion_*.py",
        # Python cache
        "**/__pycache__",
        "**/*.pyc",
        # IDE files
        ".vscode/settings.json",
    ]
    
    cleaned_count = 0
    
    for pattern in temp_patterns:
        for path in project_root.glob(pattern):
            try:
                if path.is_file():
                    path.unlink()
                    print(f"🗑️  Removed file: {path.relative_to(project_root)}")
                    cleaned_count += 1
                elif path.is_dir():
                    shutil.rmtree(path)
                    print(f"🗑️  Removed directory: {path.relative_to(project_root)}")
                    cleaned_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {path}: {e}")
    
    return cleaned_count

def ensure_directory_structure():
    """Ensure required directories exist with .gitkeep files"""
    project_root = Path(__file__).parent
    
    required_dirs = [
        "data/raw",
        "data/transformed", 
        "data/outputs",
        "logs"
    ]
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        gitkeep_file = full_path / ".gitkeep"
        if not gitkeep_file.exists():
            gitkeep_file.write_text("# Keep this directory in git\n")
            print(f"📁 Created .gitkeep in {dir_path}")

def main():
    """Main preparation function"""
    print("🚀 Preparing LinkedIn Ghost Jobs ETL for GitHub...")
    print("=" * 50)
    
    # Clean temporary files
    cleaned_count = clean_temporary_files()
    print(f"\n✅ Cleaned {cleaned_count} temporary files/directories")
    
    # Ensure directory structure
    ensure_directory_structure()
    
    print("\n🎉 Project is ready for GitHub!")
    print("\nNext steps:")
    print("1. git add .")
    print("2. git commit -m 'Clean project for GitHub'")
    print("3. git push origin main")

if __name__ == "__main__":
    main()