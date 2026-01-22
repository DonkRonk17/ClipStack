#!/usr/bin/env python3
"""
ClipStack - Clipboard History Manager for Power Users

A CLI-first clipboard history manager that stores, searches, and recalls
your clipboard entries. Never lose a copied snippet again!

Features:
- Store 50+ clipboard entries with automatic capture
- Persist history across sessions (SQLite database)
- Quick CLI recall: clipstack get 3 (get 3rd most recent)
- Search clipboard history: clipstack search 'function'
- Copy specific entries back to active clipboard
- Cross-platform support (Windows, Linux, macOS)
- Zero dependencies for basic features (pyperclip optional)

Author: ATLAS (Team Brain)
For: Logan Smith / Metaphy LLC
Requested By: Logan Smith - "When coding or writing, I constantly copy 
              multiple things but can only access the most recent clipboard item."
Version: 1.0
Date: January 22, 2026
License: MIT
"""

import argparse
import datetime
import json
import os
import platform
import re
import sqlite3
import subprocess
import sys
import time
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

# Version info
__version__ = "1.0.0"
__author__ = "ATLAS (Team Brain)"

# ==============================================================================
# CONSTANTS
# ==============================================================================

DEFAULT_HISTORY_SIZE = 100
MAX_ENTRY_DISPLAY_LENGTH = 80
WATCH_POLL_INTERVAL = 0.5  # seconds

# ==============================================================================
# DATABASE MANAGER
# ==============================================================================

class ClipStackDB:
    """SQLite database manager for clipboard history."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to database file. Defaults to ~/.clipstack/history.db
        """
        if db_path is None:
            db_path = self._get_default_db_path()
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
    
    def _get_default_db_path(self) -> Path:
        """Get the default database path based on platform."""
        home = Path.home()
        return home / ".clipstack" / "history.db"
    
    def _init_db(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()
        
        # Main history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clipboard_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source TEXT DEFAULT 'clipboard',
                char_count INTEGER,
                word_count INTEGER,
                pinned INTEGER DEFAULT 0
            )
        """)
        
        # Index for faster searches
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON clipboard_history(timestamp DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_hash 
            ON clipboard_history(content_hash)
        """)
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        self.conn.commit()
    
    def add_entry(self, content: str, source: str = "clipboard") -> int:
        """
        Add a new clipboard entry.
        
        Args:
            content: The clipboard content
            source: Source of the entry (clipboard, manual, import)
            
        Returns:
            The ID of the new entry
        """
        if not content or not content.strip():
            return -1
        
        # Calculate hash to detect duplicates
        content_hash = str(hash(content))
        
        # Check if this exact content already exists as most recent
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id FROM clipboard_history 
            WHERE content_hash = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (content_hash,))
        
        existing = cursor.fetchone()
        if existing:
            # Update timestamp of existing entry instead of duplicating
            cursor.execute("""
                UPDATE clipboard_history 
                SET timestamp = ? 
                WHERE id = ?
            """, (datetime.datetime.now().isoformat(), existing['id']))
            self.conn.commit()
            return existing['id']
        
        # Add new entry
        timestamp = datetime.datetime.now().isoformat()
        char_count = len(content)
        word_count = len(content.split())
        
        cursor.execute("""
            INSERT INTO clipboard_history 
            (content, content_hash, timestamp, source, char_count, word_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (content, content_hash, timestamp, source, char_count, word_count))
        
        self.conn.commit()
        
        # Prune old entries
        self._prune_history()
        
        return cursor.lastrowid
    
    def _prune_history(self, max_entries: int = DEFAULT_HISTORY_SIZE):
        """Remove old entries beyond the history limit."""
        cursor = self.conn.cursor()
        
        # Keep pinned entries, delete oldest unpinned
        cursor.execute("""
            DELETE FROM clipboard_history 
            WHERE pinned = 0 AND id NOT IN (
                SELECT id FROM clipboard_history 
                WHERE pinned = 0 
                ORDER BY timestamp DESC 
                LIMIT ?
            )
        """, (max_entries,))
        
        self.conn.commit()
    
    def get_entry(self, position: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get entry by position (1 = most recent).
        
        Args:
            position: Position in history (1-indexed, 1 = most recent)
            
        Returns:
            Entry dict or None if not found
        """
        if position < 1:
            return None
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM clipboard_history 
            ORDER BY timestamp DESC 
            LIMIT 1 OFFSET ?
        """, (position - 1,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent clipboard entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of entry dicts
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM clipboard_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search clipboard history.
        
        Args:
            query: Search term (case-insensitive)
            limit: Maximum number of results
            
        Returns:
            List of matching entries
        """
        cursor = self.conn.cursor()
        
        # Try regex search first, fall back to simple LIKE
        try:
            pattern = re.compile(query, re.IGNORECASE)
            cursor.execute("""
                SELECT * FROM clipboard_history 
                ORDER BY timestamp DESC
            """)
            
            results = []
            for row in cursor.fetchall():
                if pattern.search(row['content']):
                    results.append(dict(row))
                    if len(results) >= limit:
                        break
            return results
            
        except re.error:
            # Invalid regex, use simple LIKE
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT * FROM clipboard_history 
                WHERE content LIKE ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (search_term, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_entry(self, entry_id: int) -> bool:
        """Delete a specific entry by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM clipboard_history WHERE id = ?", (entry_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def clear_history(self, keep_pinned: bool = True) -> int:
        """
        Clear clipboard history.
        
        Args:
            keep_pinned: If True, keep pinned entries
            
        Returns:
            Number of entries deleted
        """
        cursor = self.conn.cursor()
        
        if keep_pinned:
            cursor.execute("DELETE FROM clipboard_history WHERE pinned = 0")
        else:
            cursor.execute("DELETE FROM clipboard_history")
        
        count = cursor.rowcount
        self.conn.commit()
        return count
    
    def pin_entry(self, position: int) -> bool:
        """Pin an entry to prevent it from being pruned."""
        entry = self.get_entry(position)
        if not entry:
            return False
            
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE clipboard_history 
            SET pinned = 1 
            WHERE id = ?
        """, (entry['id'],))
        self.conn.commit()
        return True
    
    def unpin_entry(self, position: int) -> bool:
        """Unpin an entry."""
        entry = self.get_entry(position)
        if not entry:
            return False
            
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE clipboard_history 
            SET pinned = 0 
            WHERE id = ?
        """, (entry['id'],))
        self.conn.commit()
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get clipboard history statistics."""
        cursor = self.conn.cursor()
        
        # Total entries
        cursor.execute("SELECT COUNT(*) as count FROM clipboard_history")
        total = cursor.fetchone()['count']
        
        # Pinned entries
        cursor.execute("SELECT COUNT(*) as count FROM clipboard_history WHERE pinned = 1")
        pinned = cursor.fetchone()['count']
        
        # Total characters and words
        cursor.execute("""
            SELECT COALESCE(SUM(char_count), 0) as chars, 
                   COALESCE(SUM(word_count), 0) as words 
            FROM clipboard_history
        """)
        row = cursor.fetchone()
        total_chars = row['chars']
        total_words = row['words']
        
        # Date range
        cursor.execute("""
            SELECT MIN(timestamp) as oldest, MAX(timestamp) as newest 
            FROM clipboard_history
        """)
        row = cursor.fetchone()
        oldest = row['oldest']
        newest = row['newest']
        
        # Database size
        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
        
        return {
            'total_entries': total,
            'pinned_entries': pinned,
            'total_characters': total_chars,
            'total_words': total_words,
            'oldest_entry': oldest,
            'newest_entry': newest,
            'database_size_bytes': db_size,
            'database_path': str(self.db_path)
        }
    
    def export_history(self, format: str = 'json') -> str:
        """
        Export clipboard history.
        
        Args:
            format: Export format ('json' or 'txt')
            
        Returns:
            Exported data as string
        """
        entries = self.get_recent(limit=1000)
        
        if format == 'json':
            return json.dumps(entries, indent=2, default=str)
        else:
            # Plain text format
            lines = []
            for i, entry in enumerate(entries, 1):
                lines.append(f"=== Entry {i} ({entry['timestamp']}) ===")
                lines.append(entry['content'])
                lines.append("")
            return "\n".join(lines)
    
    def import_history(self, data: str, format: str = 'json') -> int:
        """
        Import clipboard history.
        
        Args:
            data: Import data string
            format: Data format ('json')
            
        Returns:
            Number of entries imported
        """
        if format != 'json':
            raise ValueError("Only JSON import is currently supported")
        
        entries = json.loads(data)
        count = 0
        
        for entry in entries:
            if 'content' in entry:
                self.add_entry(entry['content'], source='import')
                count += 1
        
        return count
    
    def close(self):
        """Close database connection."""
        self.conn.close()


# ==============================================================================
# CLIPBOARD ACCESS (Cross-Platform)
# ==============================================================================

class ClipboardAccess:
    """Cross-platform clipboard access."""
    
    def __init__(self):
        """Initialize clipboard access."""
        self.system = platform.system()
        self._pyperclip_available = self._check_pyperclip()
    
    def _check_pyperclip(self) -> bool:
        """Check if pyperclip is available."""
        try:
            import pyperclip
            return True
        except ImportError:
            return False
    
    def get_clipboard(self) -> Optional[str]:
        """
        Get current clipboard content.
        
        Returns:
            Clipboard content or None if unavailable
        """
        # Try pyperclip first
        if self._pyperclip_available:
            try:
                import pyperclip
                return pyperclip.paste()
            except Exception:
                pass
        
        # Platform-specific fallbacks
        try:
            if self.system == 'Windows':
                return self._get_windows_clipboard()
            elif self.system == 'Darwin':
                return self._get_macos_clipboard()
            else:
                return self._get_linux_clipboard()
        except Exception as e:
            return None
    
    def set_clipboard(self, content: str) -> bool:
        """
        Set clipboard content.
        
        Args:
            content: Text to copy to clipboard
            
        Returns:
            True if successful
        """
        # Try pyperclip first
        if self._pyperclip_available:
            try:
                import pyperclip
                pyperclip.copy(content)
                return True
            except Exception:
                pass
        
        # Platform-specific fallbacks
        try:
            if self.system == 'Windows':
                return self._set_windows_clipboard(content)
            elif self.system == 'Darwin':
                return self._set_macos_clipboard(content)
            else:
                return self._set_linux_clipboard(content)
        except Exception:
            return False
    
    def _get_windows_clipboard(self) -> Optional[str]:
        """Get clipboard on Windows using PowerShell."""
        try:
            result = subprocess.run(
                ['powershell', '-command', 'Get-Clipboard'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.rstrip('\r\n')
        except Exception:
            pass
        return None
    
    def _set_windows_clipboard(self, content: str) -> bool:
        """Set clipboard on Windows using PowerShell."""
        try:
            process = subprocess.Popen(
                ['powershell', '-command', 'Set-Clipboard -Value $input'],
                stdin=subprocess.PIPE,
                text=True
            )
            process.communicate(input=content, timeout=5)
            return process.returncode == 0
        except Exception:
            return False
    
    def _get_macos_clipboard(self) -> Optional[str]:
        """Get clipboard on macOS using pbpaste."""
        try:
            result = subprocess.run(
                ['pbpaste'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        return None
    
    def _set_macos_clipboard(self, content: str) -> bool:
        """Set clipboard on macOS using pbcopy."""
        try:
            process = subprocess.Popen(
                ['pbcopy'],
                stdin=subprocess.PIPE,
                text=True
            )
            process.communicate(input=content, timeout=5)
            return process.returncode == 0
        except Exception:
            return False
    
    def _get_linux_clipboard(self) -> Optional[str]:
        """Get clipboard on Linux using xclip or xsel."""
        # Try xclip first
        try:
            result = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-o'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass
        except Exception:
            pass
        
        # Try xsel as fallback
        try:
            result = subprocess.run(
                ['xsel', '--clipboard', '--output'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        
        return None
    
    def _set_linux_clipboard(self, content: str) -> bool:
        """Set clipboard on Linux using xclip or xsel."""
        # Try xclip first
        try:
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard'],
                stdin=subprocess.PIPE,
                text=True
            )
            process.communicate(input=content, timeout=5)
            if process.returncode == 0:
                return True
        except FileNotFoundError:
            pass
        except Exception:
            pass
        
        # Try xsel as fallback
        try:
            process = subprocess.Popen(
                ['xsel', '--clipboard', '--input'],
                stdin=subprocess.PIPE,
                text=True
            )
            process.communicate(input=content, timeout=5)
            return process.returncode == 0
        except Exception:
            pass
        
        return False


# ==============================================================================
# CLIPBOARD WATCHER (Daemon)
# ==============================================================================

class ClipboardWatcher:
    """Background clipboard watcher daemon."""
    
    def __init__(self, db: ClipStackDB, clipboard: ClipboardAccess):
        """Initialize watcher."""
        self.db = db
        self.clipboard = clipboard
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_content = ""
    
    def start(self):
        """Start watching clipboard in background."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop watching clipboard."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def _watch_loop(self):
        """Main watch loop."""
        while self._running:
            try:
                content = self.clipboard.get_clipboard()
                if content and content != self._last_content:
                    self.db.add_entry(content)
                    self._last_content = content
            except Exception:
                pass
            
            time.sleep(WATCH_POLL_INTERVAL)


# ==============================================================================
# MAIN CLI CLASS
# ==============================================================================

class ClipStack:
    """
    Main ClipStack interface.
    
    Provides both CLI and Python API access to clipboard history.
    
    Example:
        >>> cs = ClipStack()
        >>> cs.add("Hello, World!")
        >>> cs.list(limit=5)
        >>> cs.get(1)
        >>> cs.copy(1)
        >>> cs.search("Hello")
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize ClipStack.
        
        Args:
            db_path: Optional custom database path
        """
        self.db = ClipStackDB(db_path)
        self.clipboard = ClipboardAccess()
        self.watcher: Optional[ClipboardWatcher] = None
    
    def add(self, content: str, source: str = "manual") -> int:
        """
        Add content to clipboard history.
        
        Args:
            content: Text content to add
            source: Source identifier (manual, clipboard, import)
            
        Returns:
            Entry ID
        """
        return self.db.add_entry(content, source)
    
    def capture(self) -> Optional[int]:
        """
        Capture current clipboard content.
        
        Returns:
            Entry ID if captured, None if clipboard empty
        """
        content = self.clipboard.get_clipboard()
        if content:
            return self.db.add_entry(content, source="clipboard")
        return None
    
    def get(self, position: int = 1) -> Optional[str]:
        """
        Get clipboard entry by position.
        
        Args:
            position: Position in history (1 = most recent)
            
        Returns:
            Content string or None
        """
        entry = self.db.get_entry(position)
        return entry['content'] if entry else None
    
    def get_entry(self, position: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get full entry details by position.
        
        Args:
            position: Position in history (1 = most recent)
            
        Returns:
            Entry dict with all metadata
        """
        return self.db.get_entry(position)
    
    def list(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent clipboard entries.
        
        Args:
            limit: Maximum entries to return
            
        Returns:
            List of entry dicts
        """
        return self.db.get_recent(limit)
    
    def copy(self, position: int = 1) -> bool:
        """
        Copy entry back to system clipboard.
        
        Args:
            position: Position in history to copy
            
        Returns:
            True if successful
        """
        content = self.get(position)
        if content:
            return self.clipboard.set_clipboard(content)
        return False
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search clipboard history.
        
        Args:
            query: Search term (supports regex)
            limit: Maximum results
            
        Returns:
            List of matching entries
        """
        return self.db.search(query, limit)
    
    def delete(self, position: int) -> bool:
        """
        Delete entry by position.
        
        Args:
            position: Position to delete
            
        Returns:
            True if deleted
        """
        entry = self.db.get_entry(position)
        if entry:
            return self.db.delete_entry(entry['id'])
        return False
    
    def clear(self, keep_pinned: bool = True) -> int:
        """
        Clear clipboard history.
        
        Args:
            keep_pinned: Keep pinned entries
            
        Returns:
            Number of entries deleted
        """
        return self.db.clear_history(keep_pinned)
    
    def pin(self, position: int) -> bool:
        """Pin an entry to protect from pruning."""
        return self.db.pin_entry(position)
    
    def unpin(self, position: int) -> bool:
        """Unpin an entry."""
        return self.db.unpin_entry(position)
    
    def stats(self) -> Dict[str, Any]:
        """Get clipboard history statistics."""
        return self.db.get_stats()
    
    def export(self, format: str = 'json') -> str:
        """Export clipboard history."""
        return self.db.export_history(format)
    
    def import_history(self, data: str, format: str = 'json') -> int:
        """Import clipboard history."""
        return self.db.import_history(data, format)
    
    def start_watch(self):
        """Start background clipboard watcher."""
        if not self.watcher:
            self.watcher = ClipboardWatcher(self.db, self.clipboard)
        self.watcher.start()
    
    def stop_watch(self):
        """Stop background clipboard watcher."""
        if self.watcher:
            self.watcher.stop()
    
    def close(self):
        """Clean up resources."""
        self.stop_watch()
        self.db.close()


# ==============================================================================
# CLI FUNCTIONS
# ==============================================================================

def truncate_text(text: str, max_length: int = MAX_ENTRY_DISPLAY_LENGTH) -> str:
    """Truncate text for display."""
    # Replace newlines with visual marker
    text = text.replace('\n', ' [NL] ').replace('\r', '')
    
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display."""
    try:
        dt = datetime.datetime.fromisoformat(timestamp_str)
        now = datetime.datetime.now()
        
        # Same day - show time only
        if dt.date() == now.date():
            return dt.strftime("Today %H:%M")
        
        # Yesterday
        yesterday = now.date() - datetime.timedelta(days=1)
        if dt.date() == yesterday:
            return dt.strftime("Yesterday %H:%M")
        
        # This year - show date without year
        if dt.year == now.year:
            return dt.strftime("%b %d %H:%M")
        
        # Different year
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return timestamp_str[:16]


def cmd_list(args, cs: ClipStack):
    """List recent clipboard entries."""
    entries = cs.list(limit=args.last)
    
    if not entries:
        print("[INFO] No clipboard entries found.")
        print("[TIP] Use 'clipstack capture' to capture current clipboard")
        print("[TIP] Use 'clipstack watch' to auto-capture clipboard changes")
        return
    
    print(f"[CLIPBOARD HISTORY] Showing {len(entries)} most recent entries")
    print("-" * 70)
    
    for i, entry in enumerate(entries, 1):
        pinned = " [*]" if entry.get('pinned') else ""
        timestamp = format_timestamp(entry['timestamp'])
        content = truncate_text(entry['content'])
        chars = entry.get('char_count', 0)
        
        print(f"  {i:3d}{pinned}  {timestamp:18s}  ({chars:5d} chars)  {content}")
    
    print("-" * 70)
    print(f"[TIP] Use 'clipstack get <n>' to view full entry")
    print(f"[TIP] Use 'clipstack copy <n>' to copy entry back to clipboard")


def cmd_get(args, cs: ClipStack):
    """Get and display a specific entry."""
    entry = cs.get_entry(args.position)
    
    if not entry:
        print(f"[ERROR] No entry at position {args.position}")
        return 1
    
    if args.quiet:
        print(entry['content'])
    else:
        print(f"[ENTRY #{args.position}]")
        print(f"Timestamp: {format_timestamp(entry['timestamp'])}")
        print(f"Source: {entry.get('source', 'unknown')}")
        print(f"Characters: {entry.get('char_count', 0)}")
        print(f"Words: {entry.get('word_count', 0)}")
        print(f"Pinned: {'Yes' if entry.get('pinned') else 'No'}")
        print("-" * 40)
        print(entry['content'])
        print("-" * 40)
    
    return 0


def cmd_copy(args, cs: ClipStack):
    """Copy entry back to system clipboard."""
    success = cs.copy(args.position)
    
    if success:
        entry = cs.get_entry(args.position)
        content_preview = truncate_text(entry['content'], 50) if entry else ""
        print(f"[OK] Entry #{args.position} copied to clipboard")
        print(f"[CONTENT] {content_preview}")
    else:
        print(f"[ERROR] Failed to copy entry #{args.position}")
        return 1
    
    return 0


def cmd_search(args, cs: ClipStack):
    """Search clipboard history."""
    results = cs.search(args.query, limit=args.limit)
    
    if not results:
        print(f"[INFO] No entries found matching '{args.query}'")
        return
    
    print(f"[SEARCH RESULTS] Found {len(results)} matches for '{args.query}'")
    print("-" * 70)
    
    for i, entry in enumerate(results, 1):
        timestamp = format_timestamp(entry['timestamp'])
        content = truncate_text(entry['content'])
        
        # Highlight search term
        try:
            pattern = re.compile(f"({re.escape(args.query)})", re.IGNORECASE)
            content = pattern.sub(r"**\1**", content)
        except Exception:
            pass
        
        print(f"  {i:3d}  {timestamp:18s}  {content}")
    
    print("-" * 70)


def cmd_add(args, cs: ClipStack):
    """Manually add text to clipboard history."""
    content = " ".join(args.text)
    
    if not content.strip():
        print("[ERROR] No text provided")
        return 1
    
    entry_id = cs.add(content, source="manual")
    print(f"[OK] Added entry (ID: {entry_id})")
    print(f"[CONTENT] {truncate_text(content, 60)}")
    return 0


def cmd_capture(args, cs: ClipStack):
    """Capture current clipboard content."""
    entry_id = cs.capture()
    
    if entry_id:
        entry = cs.get_entry(1)
        content_preview = truncate_text(entry['content'], 60) if entry else ""
        print(f"[OK] Captured clipboard content")
        print(f"[CONTENT] {content_preview}")
    else:
        print("[INFO] Clipboard is empty or unavailable")
        return 1
    
    return 0


def cmd_clear(args, cs: ClipStack):
    """Clear clipboard history."""
    if not args.force:
        print("[WARNING] This will delete clipboard history!")
        print("Use --force to confirm, or --keep-pinned to preserve pinned entries")
        return 1
    
    count = cs.clear(keep_pinned=args.keep_pinned)
    
    if args.keep_pinned:
        print(f"[OK] Cleared {count} unpinned entries (pinned entries preserved)")
    else:
        print(f"[OK] Cleared {count} entries")
    
    return 0


def cmd_pin(args, cs: ClipStack):
    """Pin an entry."""
    success = cs.pin(args.position)
    
    if success:
        print(f"[OK] Pinned entry #{args.position}")
    else:
        print(f"[ERROR] Entry #{args.position} not found")
        return 1
    
    return 0


def cmd_unpin(args, cs: ClipStack):
    """Unpin an entry."""
    success = cs.unpin(args.position)
    
    if success:
        print(f"[OK] Unpinned entry #{args.position}")
    else:
        print(f"[ERROR] Entry #{args.position} not found")
        return 1
    
    return 0


def cmd_delete(args, cs: ClipStack):
    """Delete a specific entry."""
    success = cs.delete(args.position)
    
    if success:
        print(f"[OK] Deleted entry #{args.position}")
    else:
        print(f"[ERROR] Entry #{args.position} not found")
        return 1
    
    return 0


def cmd_stats(args, cs: ClipStack):
    """Display clipboard statistics."""
    stats = cs.stats()
    
    print("[CLIPSTACK STATISTICS]")
    print("-" * 40)
    print(f"  Total entries:    {stats['total_entries']}")
    print(f"  Pinned entries:   {stats['pinned_entries']}")
    print(f"  Total characters: {stats['total_characters']:,}")
    print(f"  Total words:      {stats['total_words']:,}")
    
    if stats['oldest_entry']:
        print(f"  Oldest entry:     {format_timestamp(stats['oldest_entry'])}")
    if stats['newest_entry']:
        print(f"  Newest entry:     {format_timestamp(stats['newest_entry'])}")
    
    size_kb = stats['database_size_bytes'] / 1024
    print(f"  Database size:    {size_kb:.1f} KB")
    print(f"  Database path:    {stats['database_path']}")
    print("-" * 40)
    
    return 0


def cmd_export(args, cs: ClipStack):
    """Export clipboard history."""
    data = cs.export(format=args.format)
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(data, encoding='utf-8')
        print(f"[OK] Exported to {output_path}")
    else:
        print(data)
    
    return 0


def cmd_import(args, cs: ClipStack):
    """Import clipboard history."""
    input_path = Path(args.file)
    
    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}")
        return 1
    
    data = input_path.read_text(encoding='utf-8')
    count = cs.import_history(data, format='json')
    
    print(f"[OK] Imported {count} entries from {input_path}")
    return 0


def cmd_watch(args, cs: ClipStack):
    """Watch clipboard and capture changes."""
    print("[CLIPSTACK WATCH MODE]")
    print("Monitoring clipboard for changes...")
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
    last_content = ""
    
    try:
        while True:
            content = cs.clipboard.get_clipboard()
            if content and content != last_content:
                entry_id = cs.add(content, source="watch")
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                preview = truncate_text(content, 50)
                print(f"[{timestamp}] Captured: {preview}")
                last_content = content
            
            time.sleep(WATCH_POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n[INFO] Stopped watching")
    
    return 0


def cmd_version(args, cs: ClipStack):
    """Show version information."""
    print(f"ClipStack v{__version__}")
    print(f"Author: {__author__}")
    print("Clipboard History Manager for Power Users")
    print("https://github.com/DonkRonk17/ClipStack")
    return 0


# ==============================================================================
# MAIN CLI ENTRY POINT
# ==============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='clipstack',
        description='ClipStack - Clipboard History Manager for Power Users',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clipstack list                  # List recent clipboard entries
  clipstack list --last 20        # Show last 20 entries
  clipstack get 1                 # Get most recent entry
  clipstack get 3 --quiet         # Get 3rd entry (content only)
  clipstack copy 2                # Copy 2nd entry back to clipboard
  clipstack search "function"     # Search for 'function'
  clipstack add "some text"       # Manually add text to history
  clipstack capture               # Capture current clipboard
  clipstack watch                 # Auto-capture clipboard changes
  clipstack clear --force         # Clear all history
  clipstack pin 1                 # Pin entry #1
  clipstack stats                 # Show statistics
  clipstack export -o backup.json # Export history

For more information: https://github.com/DonkRonk17/ClipStack
        """
    )
    
    parser.add_argument('--version', '-V', action='store_true',
                       help='Show version information')
    parser.add_argument('--db', type=str, default=None,
                       help='Custom database path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # list command
    p_list = subparsers.add_parser('list', aliases=['ls'],
                                   help='List recent clipboard entries')
    p_list.add_argument('--last', '-n', type=int, default=10,
                       help='Number of entries to show (default: 10)')
    
    # get command
    p_get = subparsers.add_parser('get', aliases=['g'],
                                  help='Get a specific entry')
    p_get.add_argument('position', type=int, nargs='?', default=1,
                      help='Entry position (1 = most recent)')
    p_get.add_argument('--quiet', '-q', action='store_true',
                      help='Output content only (no metadata)')
    
    # copy command
    p_copy = subparsers.add_parser('copy', aliases=['c'],
                                   help='Copy entry back to clipboard')
    p_copy.add_argument('position', type=int, nargs='?', default=1,
                       help='Entry position to copy')
    
    # search command
    p_search = subparsers.add_parser('search', aliases=['s', 'find'],
                                     help='Search clipboard history')
    p_search.add_argument('query', type=str,
                         help='Search term (supports regex)')
    p_search.add_argument('--limit', '-n', type=int, default=20,
                         help='Maximum results (default: 20)')
    
    # add command
    p_add = subparsers.add_parser('add', aliases=['a'],
                                  help='Manually add text to history')
    p_add.add_argument('text', nargs='+',
                      help='Text to add')
    
    # capture command
    p_capture = subparsers.add_parser('capture', aliases=['cap'],
                                      help='Capture current clipboard')
    
    # clear command
    p_clear = subparsers.add_parser('clear',
                                    help='Clear clipboard history')
    p_clear.add_argument('--force', '-f', action='store_true',
                        help='Force clear without confirmation')
    p_clear.add_argument('--keep-pinned', '-k', action='store_true', default=True,
                        help='Keep pinned entries (default: True)')
    p_clear.add_argument('--all', action='store_true',
                        help='Clear all entries including pinned')
    
    # pin command
    p_pin = subparsers.add_parser('pin',
                                  help='Pin an entry')
    p_pin.add_argument('position', type=int,
                      help='Entry position to pin')
    
    # unpin command
    p_unpin = subparsers.add_parser('unpin',
                                    help='Unpin an entry')
    p_unpin.add_argument('position', type=int,
                        help='Entry position to unpin')
    
    # delete command
    p_delete = subparsers.add_parser('delete', aliases=['del', 'rm'],
                                     help='Delete a specific entry')
    p_delete.add_argument('position', type=int,
                         help='Entry position to delete')
    
    # stats command
    p_stats = subparsers.add_parser('stats',
                                    help='Show clipboard statistics')
    
    # export command
    p_export = subparsers.add_parser('export',
                                     help='Export clipboard history')
    p_export.add_argument('--output', '-o', type=str,
                         help='Output file path')
    p_export.add_argument('--format', '-f', choices=['json', 'txt'],
                         default='json', help='Export format (default: json)')
    
    # import command
    p_import = subparsers.add_parser('import',
                                     help='Import clipboard history')
    p_import.add_argument('file', type=str,
                         help='JSON file to import')
    
    # watch command
    p_watch = subparsers.add_parser('watch',
                                    help='Watch clipboard and capture changes')
    
    args = parser.parse_args()
    
    # Handle --version flag
    if args.version:
        print(f"ClipStack v{__version__}")
        return 0
    
    # Default to list if no command
    if not args.command:
        args.command = 'list'
        args.last = 10
    
    # Initialize ClipStack
    db_path = Path(args.db) if args.db else None
    cs = ClipStack(db_path)
    
    try:
        # Command dispatch
        commands = {
            'list': cmd_list, 'ls': cmd_list,
            'get': cmd_get, 'g': cmd_get,
            'copy': cmd_copy, 'c': cmd_copy,
            'search': cmd_search, 's': cmd_search, 'find': cmd_search,
            'add': cmd_add, 'a': cmd_add,
            'capture': cmd_capture, 'cap': cmd_capture,
            'clear': cmd_clear,
            'pin': cmd_pin,
            'unpin': cmd_unpin,
            'delete': cmd_delete, 'del': cmd_delete, 'rm': cmd_delete,
            'stats': cmd_stats,
            'export': cmd_export,
            'import': cmd_import,
            'watch': cmd_watch,
        }
        
        if args.command == 'clear' and hasattr(args, 'all') and args.all:
            args.keep_pinned = False
        
        if args.command in commands:
            result = commands[args.command](args, cs)
            return result if result else 0
        else:
            parser.print_help()
            return 1
    
    finally:
        cs.close()


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    sys.exit(main())
