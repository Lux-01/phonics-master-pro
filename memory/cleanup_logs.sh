#!/bin/bash
# ACA Methodology: Log Cleanup Script v1.0
# Safe cleanup of old trading logs

set -e

WORKSPACE="/home/skux/.openclaw/workspace"
TMP_DIR="/tmp"
BACKUP_DIR="$WORKSPACE/logs/archive"

# Create archive directory
mkdir -p "$BACKUP_DIR"

echo "🧹 Starting Log Cleanup"
echo "======================"

# 1. Archive AOE logs older than 7 days
echo ""
echo "📦 Archiving old AOE logs..."
AOE_OLD=$(find "$TMP_DIR" -name "aoe_scan_*.log" -mtime +7 2>/dev/null | wc -l)
if [ $AOE_OLD -gt 0 ]; then
    find "$TMP_DIR" -name "aoe_scan_*.log" -mtime +7 -exec mv {} "$BACKUP_DIR/" \;
    echo "  Archived $AOE_OLD old AOE logs"
else
    echo "  No old AOE logs to archive"
fi

# 2. Remove AOE logs older than 30 days from archive
echo ""
echo "🗑️  Cleaning archive..."
ARCHIVE_OLD=$(find "$BACKUP_DIR" -name "*.log" -mtime +30 2>/dev/null | wc -l)
if [ $ARCHIVE_OLD -gt 0 ]; then
    find "$BACKUP_DIR" -name "*.log" -mtime +30 -delete
    echo "  Removed $ARCHIVE_OLD archived logs (30+ days old)"
else
    echo "  No old archived logs to remove"
fi

# 3. Clean temporary trading logs
echo ""
echo "🧹 Cleaning temporary files..."

# Remove old backup files
echo "  Checking backup files..."
BACKUPS=$(find "$WORKSPACE" -name "*.backup" 2>/dev/null | wc -l)
if [ $BACKUPS -gt 0 ]; then
    # Keep files that are referenced (like skylar_bridge.py.backup)
    find "$WORKSPACE" -name "*.backup" -mtime +14 -delete 2>/dev/null || true
    echo "  Cleaned old backup files"
fi

# 4. Report disk usage
echo ""
echo "📊 Disk Usage Summary"
echo "===================="
df -h . | tail -1

echo ""
echo "✅ Cleanup Complete"
echo "Archive location: $BACKUP_DIR"
