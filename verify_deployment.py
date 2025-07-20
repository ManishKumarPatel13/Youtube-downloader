#!/usr/bin/env python3
"""
Deployment verification script for YouTube Downloader
This script checks if the application is ready for deployment
"""

import sys
import os

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} - NOT FOUND")
        return False

def check_syntax(filepath):
    """Check Python file syntax"""
    try:
        with open(filepath, 'r') as f:
            compile(f.read(), filepath, 'exec')
        print(f"✓ Syntax check passed: {filepath}")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in {filepath}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking {filepath}: {e}")
        return False

def main():
    print("YouTube Downloader - Deployment Verification")
    print("=" * 50)
    
    # Check required files
    required_files = [
        ('requirements.txt', 'Dependencies file'),
        ('main.py', 'Application entry point'),
        ('app.py', 'Flask application'),
        ('routes.py', 'Route definitions'),
        ('youtube_service.py', 'YouTube service'),
        ('render.yaml', 'Render configuration'),
        ('templates/index.html', 'Main template'),
        ('static/js/app.js', 'Frontend JavaScript'),
        ('static/css/style.css', 'Styles')
    ]
    
    files_ok = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            files_ok = False
    
    # Check Python file syntax
    python_files = ['main.py', 'app.py', 'routes.py', 'youtube_service.py']
    syntax_ok = True
    
    print("\nSyntax Verification:")
    print("-" * 20)
    for pyfile in python_files:
        if os.path.exists(pyfile):
            if not check_syntax(pyfile):
                syntax_ok = False
    
    # Check requirements.txt content
    print("\nDependency Check:")
    print("-" * 16)
    try:
        with open('requirements.txt', 'r') as f:
            deps = f.read().strip().split('\n')
            required_deps = ['flask', 'yt-dlp', 'gunicorn']
            
            for dep in required_deps:
                found = any(dep.lower() in line.lower() for line in deps)
                if found:
                    print(f"✓ {dep} found in requirements.txt")
                else:
                    print(f"✗ {dep} missing from requirements.txt")
                    syntax_ok = False
    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")
        syntax_ok = False
    
    # Summary
    print("\nDeployment Readiness:")
    print("-" * 21)
    
    if files_ok and syntax_ok:
        print("🟢 READY FOR DEPLOYMENT")
        print("\nNext steps:")
        print("1. Commit and push changes to GitHub")
        print("2. Deploy to Render")
        print("3. Test the /test_ytdlp endpoint")
        print("4. Try downloading videos with less popular URLs")
        return 0
    else:
        print("🔴 NOT READY - Fix the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
