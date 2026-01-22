# ClipStack - Usage Examples

Quick navigation:
- [Example 1: Basic First Use](#example-1-basic-first-use)
- [Example 2: Coding Workflow](#example-2-coding-workflow)
- [Example 3: Research Session](#example-3-research-session)
- [Example 4: Search Mastery](#example-4-search-mastery)
- [Example 5: Pin Important Data](#example-5-pin-important-data)
- [Example 6: Watch Mode Auto-Capture](#example-6-watch-mode-auto-capture)
- [Example 7: Export and Backup](#example-7-export-and-backup)
- [Example 8: Integration with Scripts](#example-8-integration-with-scripts)
- [Example 9: Error Recovery](#example-9-error-recovery)
- [Example 10: Full Daily Workflow](#example-10-full-daily-workflow)

---

## Example 1: Basic First Use

**Scenario:** First time using ClipStack, want to understand basic operations.

**Steps:**

```bash
# Step 1: Check version and help
clipstack --version
clipstack --help

# Step 2: See if there's any existing history
clipstack list

# Step 3: Copy something to your clipboard (any text)
# Then capture it
clipstack capture

# Step 4: See it in your history
clipstack list
```

**Expected Output:**
```
ClipStack v1.0.0

[CLIPBOARD HISTORY] Showing 1 most recent entries
----------------------------------------------------------------------
    1       Today 14:30  (   25 chars)  Your copied text here...
----------------------------------------------------------------------
[TIP] Use 'clipstack get <n>' to view full entry
```

**What You Learned:**
- How to check ClipStack status
- How to manually capture clipboard content
- How to view your clipboard history

---

## Example 2: Coding Workflow

**Scenario:** You're debugging code and need to copy multiple code snippets.

**Steps:**

```bash
# Copy this function to clipboard (simulated)
# def calculate_total(items):
#     return sum(item.price for item in items)

# Capture it
clipstack add "def calculate_total(items):
    return sum(item.price for item in items)"

# Copy another snippet
clipstack add "async function fetchUsers() {
    const response = await fetch('/api/users');
    return response.json();
}"

# Copy a SQL query
clipstack add "SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id"

# Now list all three
clipstack list -n 3
```

**Expected Output:**
```
[CLIPBOARD HISTORY] Showing 3 most recent entries
----------------------------------------------------------------------
    1       Today 14:35  (   97 chars)  SELECT u.name, COUNT(o.id) a...
    2       Today 14:34  (  106 chars)  async function fetchUsers() ...
    3       Today 14:33  (   71 chars)  def calculate_total(items): ...
----------------------------------------------------------------------
```

```bash
# Need the Python function? Get it by position
clipstack get 3

# Copy it back to your clipboard
clipstack copy 3
```

**Expected Output:**
```
[ENTRY #3]
Timestamp: Today 14:33
Source: manual
Characters: 71
Words: 9
Pinned: No
----------------------------------------
def calculate_total(items):
    return sum(item.price for item in items)
----------------------------------------

[OK] Entry #3 copied to clipboard
```

**What You Learned:**
- How to add multiple code snippets
- How to retrieve specific entries by position
- How to copy entries back to the active clipboard

---

## Example 3: Research Session

**Scenario:** You're researching a topic and copying URLs, quotes, and notes.

**Steps:**

```bash
# As you browse, capture URLs
clipstack add "https://docs.python.org/3/library/sqlite3.html"
clipstack add "https://github.com/python/cpython/blob/main/Lib/sqlite3/"
clipstack add "Note: SQLite transactions are auto-committed unless BEGIN is used"
clipstack add "https://www.sqlitetutorial.net/sqlite-python/"

# Search for your SQLite resources
clipstack search "sqlite"
```

**Expected Output:**
```
[SEARCH RESULTS] Found 4 matches for 'sqlite'
----------------------------------------------------------------------
    1  Today 14:40     https://www.**sqlite**tutorial.net/**sqlite**...
    2  Today 14:39     Note: **SQLite** transactions are auto-comm...
    3  Today 14:38     https://github.com/python/cpython/blob/main...
    4  Today 14:37     https://docs.python.org/3/library/**sqlite**3...
----------------------------------------------------------------------
```

```bash
# Get just the official docs URL
clipstack search "docs.python"
clipstack copy 1  # Copy the search result to clipboard
```

**What You Learned:**
- How to build a research archive
- How to search through your clipboard history
- How to quickly find and re-copy specific content

---

## Example 4: Search Mastery

**Scenario:** Advanced search techniques including regex.

**Steps:**

```bash
# Add some varied content first
clipstack add "function hello() { console.log('hi'); }"
clipstack add "def hello(): print('hi')"
clipstack add "public void Hello() { System.out.println('hi'); }"
clipstack add "Error: connection timeout after 30s"
clipstack add "WARNING: deprecated function used"
clipstack add "Error: null pointer exception at line 42"

# Simple keyword search
clipstack search "hello"
```

**Expected Output:**
```
[SEARCH RESULTS] Found 3 matches for 'hello'
----------------------------------------------------------------------
    1  Today 14:45     public void **Hello**() { System.out.print...
    2  Today 14:44     def **hello**(): print('hi')
    3  Today 14:43     function **hello**() { console.log('hi'); }
----------------------------------------------------------------------
```

```bash
# Search for errors only
clipstack search "Error:"
```

**Expected Output:**
```
[SEARCH RESULTS] Found 2 matches for 'Error:'
----------------------------------------------------------------------
    1  Today 14:47     **Error:** null pointer exception at line...
    2  Today 14:46     **Error:** connection timeout after 30s
----------------------------------------------------------------------
```

```bash
# Regex search: find function definitions in any language
clipstack search "def |function |void "
```

**Expected Output:**
```
[SEARCH RESULTS] Found 3 matches for 'def |function |void '
----------------------------------------------------------------------
    1  Today 14:45     public **void** Hello() { System.out.prin...
    2  Today 14:44     **def** hello(): print('hi')
    3  Today 14:43     **function** hello() { console.log('hi'); }
----------------------------------------------------------------------
```

```bash
# Regex: find all URLs
clipstack search "https?://"
```

**What You Learned:**
- Simple keyword searches are case-insensitive
- You can use regex for complex patterns
- Search highlights matching terms in results

---

## Example 5: Pin Important Data

**Scenario:** You have critical data that must never be lost.

**Steps:**

```bash
# Add some entries
clipstack add "Regular note - not important"
clipstack add "API_KEY=sk-prod-abc123def456ghi789"
clipstack add "Another regular note"

# Check your history
clipstack list
```

**Expected Output:**
```
[CLIPBOARD HISTORY] Showing 3 most recent entries
----------------------------------------------------------------------
    1       Today 15:00  (   22 chars)  Another regular note
    2       Today 14:59  (   38 chars)  API_KEY=sk-prod-abc123def456...
    3       Today 14:58  (   29 chars)  Regular note - not important
----------------------------------------------------------------------
```

```bash
# Pin the API key (position 2)
clipstack pin 2
clipstack list
```

**Expected Output:**
```
[CLIPBOARD HISTORY] Showing 3 most recent entries
----------------------------------------------------------------------
    1       Today 15:00  (   22 chars)  Another regular note
    2  [*]  Today 14:59  (   38 chars)  API_KEY=sk-prod-abc123def456...
    3       Today 14:58  (   29 chars)  Regular note - not important
----------------------------------------------------------------------
```

Note the `[*]` indicating pinned status.

```bash
# Clear history but keep pinned
clipstack clear --force

# The pinned entry survives!
clipstack list
```

**Expected Output:**
```
[OK] Cleared 2 unpinned entries (pinned entries preserved)

[CLIPBOARD HISTORY] Showing 1 most recent entries
----------------------------------------------------------------------
    1  [*]  Today 14:59  (   38 chars)  API_KEY=sk-prod-abc123def456...
----------------------------------------------------------------------
```

```bash
# Later, unpin when you no longer need it protected
clipstack unpin 1
```

**What You Learned:**
- How to pin important entries
- Pinned entries are protected from pruning and clearing
- How to unpin when protection is no longer needed

---

## Example 6: Watch Mode Auto-Capture

**Scenario:** Automatically capture everything you copy during a work session.

**Steps:**

```bash
# Start watch mode
clipstack watch
```

**Expected Output:**
```
[CLIPSTACK WATCH MODE]
Monitoring clipboard for changes...
Press Ctrl+C to stop
----------------------------------------
```

Now copy things normally (Ctrl+C in any application). Each copy is automatically captured:

```
[15:10:23] Captured: First thing you copied
[15:10:45] Captured: Second thing you copied
[15:11:12] Captured: https://example.com/page
[15:11:30] Captured: def my_function(): pass
```

Press `Ctrl+C` to stop watching:

```
[INFO] Stopped watching
```

```bash
# Check what was captured
clipstack list -n 10
```

**Expected Output:**
```
[CLIPBOARD HISTORY] Showing 4 most recent entries
----------------------------------------------------------------------
    1       Today 15:11  (   23 chars)  def my_function(): pass
    2       Today 15:11  (   27 chars)  https://example.com/page
    3       Today 15:10  (   27 chars)  Second thing you copied
    4       Today 15:10  (   26 chars)  First thing you copied
----------------------------------------------------------------------
```

**What You Learned:**
- Watch mode runs in the foreground
- All clipboard changes are automatically captured
- Press Ctrl+C to stop watching

---

## Example 7: Export and Backup

**Scenario:** Backup your clipboard history and restore it later.

**Steps:**

```bash
# Check current history
clipstack stats
```

**Expected Output:**
```
[CLIPSTACK STATISTICS]
----------------------------------------
  Total entries:    25
  Pinned entries:   2
  Total characters: 3,456
  Total words:      567
  Oldest entry:     Jan 20 09:15
  Newest entry:     Today 15:15
  Database size:    24.5 KB
  Database path:    /home/user/.clipstack/history.db
----------------------------------------
```

```bash
# Export to JSON file
clipstack export -o clipboard_backup.json

# View the export
head -20 clipboard_backup.json
```

**Expected Output (JSON):**
```json
[
  {
    "id": 25,
    "content": "Latest entry content...",
    "content_hash": "1234567890",
    "timestamp": "2026-01-22T15:15:00",
    "source": "clipboard",
    "char_count": 50,
    "word_count": 8,
    "pinned": 0
  },
  ...
]
```

```bash
# Clear everything (simulating system reset)
clipstack clear --force --all

# Verify it's empty
clipstack list
```

**Expected Output:**
```
[INFO] No clipboard entries found.
```

```bash
# Restore from backup
clipstack import clipboard_backup.json
clipstack list
```

**Expected Output:**
```
[OK] Imported 25 entries from clipboard_backup.json

[CLIPBOARD HISTORY] Showing 10 most recent entries
----------------------------------------------------------------------
    1       Today 15:15  (   50 chars)  Latest entry content...
...
----------------------------------------------------------------------
```

**What You Learned:**
- How to export clipboard history to JSON
- How to import/restore from backup
- Useful for system migrations or periodic backups

---

## Example 8: Integration with Scripts

**Scenario:** Use ClipStack in automation scripts.

**Python Script Example:**

```python
#!/usr/bin/env python3
"""Script that uses ClipStack to manage copied code snippets."""

import sys
sys.path.insert(0, '/path/to/ClipStack')

from clipstack import ClipStack

def main():
    cs = ClipStack()
    
    # Get all code snippets from today
    entries = cs.list(limit=50)
    code_snippets = [e for e in entries 
                     if 'def ' in e['content'] or 'function' in e['content']]
    
    print(f"Found {len(code_snippets)} code snippets in clipboard history:")
    for i, snippet in enumerate(code_snippets, 1):
        preview = snippet['content'][:60].replace('\n', ' ')
        print(f"  {i}. {preview}...")
    
    # Export today's code snippets
    if code_snippets:
        import json
        with open('code_snippets.json', 'w') as f:
            json.dump(code_snippets, f, indent=2, default=str)
        print(f"\nExported to code_snippets.json")
    
    cs.close()

if __name__ == "__main__":
    main()
```

**Bash Script Example:**

```bash
#!/bin/bash
# Daily clipboard backup script

BACKUP_DIR="$HOME/clipboard_backups"
DATE=$(date +%Y-%m-%d)

mkdir -p "$BACKUP_DIR"

# Export clipboard history
python /path/to/ClipStack/clipstack.py export -o "$BACKUP_DIR/clipboard_$DATE.json"

echo "Clipboard backed up to $BACKUP_DIR/clipboard_$DATE.json"

# Keep only last 7 days
find "$BACKUP_DIR" -name "clipboard_*.json" -mtime +7 -delete
```

**PowerShell Integration:**

```powershell
# Add to your $PROFILE
function Get-ClipHistory {
    param([int]$Count = 10)
    python C:\Tools\ClipStack\clipstack.py list --last $Count
}

function Search-ClipHistory {
    param([string]$Query)
    python C:\Tools\ClipStack\clipstack.py search $Query
}

function Copy-ClipEntry {
    param([int]$Position = 1)
    python C:\Tools\ClipStack\clipstack.py copy $Position
}

# Usage:
# Get-ClipHistory 20
# Search-ClipHistory "function"
# Copy-ClipEntry 3
```

**What You Learned:**
- ClipStack can be imported as a Python library
- Easy to integrate into shell scripts
- Can automate clipboard management tasks

---

## Example 9: Error Recovery

**Scenario:** Troubleshooting common issues.

**Issue 1: "Clipboard is empty"**

```bash
clipstack capture
# Output: [INFO] Clipboard is empty or unavailable
```

**Solution:**
```bash
# Copy something to clipboard first, then try again
# Or check if clipboard access is working:
python -c "from clipstack import ClipboardAccess; ca = ClipboardAccess(); print('Clipboard:', repr(ca.get_clipboard()))"
```

**Issue 2: "No entries found"**

```bash
clipstack list
# Output: [INFO] No clipboard entries found.
```

**Solution:**
```bash
# Check database status
clipstack stats

# If database is empty, start capturing:
clipstack capture  # One-time capture
# OR
clipstack watch   # Auto-capture mode
```

**Issue 3: Entry position not found**

```bash
clipstack get 100
# Output: [ERROR] No entry at position 100
```

**Solution:**
```bash
# Check how many entries exist
clipstack stats  # Shows total entries

# List to see available positions
clipstack list -n 20
```

**Issue 4: Linux clipboard not working**

```bash
clipstack capture
# Output: [INFO] Clipboard is empty or unavailable
```

**Solution:**
```bash
# Install xclip
sudo apt install xclip

# Test it works
echo "test" | xclip -selection clipboard
xclip -selection clipboard -o  # Should print "test"

# Now clipstack should work
clipstack capture
```

**What You Learned:**
- How to diagnose clipboard access issues
- Platform-specific requirements (xclip on Linux)
- How to verify ClipStack is working correctly

---

## Example 10: Full Daily Workflow

**Scenario:** Complete daily workflow demonstrating all features.

**Morning Setup:**

```bash
# Check stats from yesterday
clipstack stats

# See if there's anything important
clipstack list -n 5
```

**During Work:**

```bash
# Start auto-capture for your work session
clipstack watch &  # Run in background (or in separate terminal)

# Work normally, copying code, URLs, text...

# When you need to find something:
clipstack search "API"
clipstack search "function"
clipstack search "TODO"

# Found it! Copy it back
clipstack copy 3
```

**Protecting Important Data:**

```bash
# Found an important credential - pin it
clipstack pin 2

# List to confirm
clipstack list
# Entry shows [*] for pinned
```

**End of Day:**

```bash
# Stop watch mode (if running)
# Ctrl+C or kill the background process

# Check your day's work
clipstack stats

# Backup (optional)
clipstack export -o "clipboard_$(date +%Y%m%d).json"

# Clear non-essential entries (keeps pinned)
clipstack clear --force
```

**Expected Stats:**
```
[CLIPSTACK STATISTICS]
----------------------------------------
  Total entries:    47
  Pinned entries:   3
  Total characters: 12,456
  Total words:      2,134
  Oldest entry:     Today 09:00
  Newest entry:     Today 17:30
  Database size:    48.2 KB
  Database path:    /home/user/.clipstack/history.db
----------------------------------------
```

**What You Learned:**
- Complete daily workflow using ClipStack
- Watch mode for passive capture
- Search and retrieve when needed
- Pin to protect important data
- Backup and cleanup routines

---

## Quick Reference

| Task | Command |
|------|---------|
| List entries | `clipstack list` or `clipstack ls` |
| Get entry | `clipstack get 1` or `clipstack g 1` |
| Copy back | `clipstack copy 2` or `clipstack c 2` |
| Search | `clipstack search "term"` or `clipstack s "term"` |
| Add manual | `clipstack add "text"` |
| Capture current | `clipstack capture` |
| Watch mode | `clipstack watch` |
| Pin | `clipstack pin 1` |
| Unpin | `clipstack unpin 1` |
| Delete | `clipstack delete 3` or `clipstack rm 3` |
| Clear | `clipstack clear --force` |
| Stats | `clipstack stats` |
| Export | `clipstack export -o backup.json` |
| Import | `clipstack import backup.json` |

---

**More examples? Check the [README](README.md) or run `clipstack --help`!**
