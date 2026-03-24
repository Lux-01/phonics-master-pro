#!/usr/bin/env python3
"""
Analyze workspace and report file statistics, duplicates, and stale files.
"""
import os
import json
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict

def get_file_info(filepath):
    """Get file metadata."""
    stat = os.stat(filepath)
    return {
        "path": filepath,
        "size": stat.st_size,
        "mtime": stat.st_mtime,
        "days_old": (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
    }

def get_file_hash(filepath):
    """Get MD5 hash of file content."""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def analyze_directory(base_path="."):
    """Analyze workspace directory."""
    files = []
    duplicates = defaultdict(list)
    
    for root, dirs, filenames in os.walk(base_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in filenames:
            filepath = os.path.join(root, filename)
            info = get_file_info(filepath)
            files.append(info)
            
            # Check for duplicates (only for files < 10MB)
            if info['size'] < 10_000_000:
                file_hash = get_file_hash(filepath)
                if file_hash:
                    duplicates[file_hash].append(filepath)
    
    # Categorize files
    stale = [f for f in files if f['days_old'] > 30]
    recent = [f for f in files if f['days_old'] <= 7]
    active = [f for f in files if 7 < f['days_old'] <= 30]
    
    # Find duplicates
    dup_groups = [paths for paths in duplicates.values() if len(paths) > 1]
    
    return {
        "total_files": len(files),
        "total_size": sum(f['size'] for f in files),
        "categories": {
            "active": len(active),
            "recent": len(recent),
            "stale": len(stale)
        },
        "duplicates": dup_groups,
        "largest_files": sorted(files, key=lambda x: x['size'], reverse=True)[:10],
        "oldest_files": sorted(files, key=lambda x: x['mtime'])[:10]
    }

def print_report(results):
    """Print formatted report."""
    print("=" * 60)
    print("📊 WORKSPACE ANALYSIS REPORT")
    print("=" * 60)
    
    print(f"\nTotal Files: {results['total_files']}")
    print(f"Total Size: {results['total_size'] / (1024*1024):.2f} MB")
    
    print("\n📁 Categories:")
    print(f"  Recent (< 7 days): {results['categories']['recent']}")
    print(f"  Active (7-30 days): {results['categories']['active']}")
    print(f"  Stale (> 30 days): {results['categories']['stale']}")
    
    if results['duplicates']:
        print(f"\n⚠️ Duplicates Found: {len(results['duplicates'])} groups")
        for group in results['duplicates'][:5]:
            print(f"  - {len(group)} files: {', '.join(group[:2])}...")
    else:
        print("\n✅ No duplicates found")
    
    print("\n🔝 Largest Files:")
    for f in results['largest_files'][:5]:
        size_mb = f['size'] / (1024*1024)
        print(f"  - {f['path']}: {size_mb:.2f} MB")
    
    print("\n👴 Oldest Files:")
    for f in results['oldest_files'][:5]:
        age = f['days_old']
        print(f"  - {f['path']}: {age} days old")

if __name__ == "__main__":
    results = analyze_directory("/home/skux/.openclaw/workspace")
    print_report(results)
    
    # Save state
    state_path = "/home/skux/.openclaw/workspace/memory/workspace_state.json"
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, 'w') as f:
        json.dump({
            "lastScan": datetime.now().isoformat(),
            "fileCount": results['total_files'],
            "categories": results['categories'],
            "duplicates": len(results['duplicates'])
        }, f, indent=2)
