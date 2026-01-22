<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/9303f299-9c56-46d4-946d-e9294597fdc9" />

# 📋 ClipStack - Clipboard History Manager for Power Users

> **Never lose a copied snippet again!** A CLI-first clipboard history manager that stores, searches, and recalls your clipboard entries.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 57 Passing](https://img.shields.io/badge/tests-57%20passing-brightgreen.svg)]()
[![Platform: Cross-Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

---

## 📑 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
  - [CLI Commands](#cli-commands)
  - [Python API](#python-api)
- [Real-World Examples](#-real-world-examples)
- [How It Works](#-how-it-works)
- [Configuration](#-configuration)
- [Integration](#-integration)
- [Troubleshooting](#-troubleshooting)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [License](#-license)
- [Credits](#-credits)

---

## 🚨 The Problem

**Ever experienced these frustrations?**

- You copy a code snippet, then accidentally copy something else, and lose the first snippet forever
- You're researching and copying multiple URLs, but can only access the most recent one
- Windows clipboard history (Win+V) is clunky, doesn't persist across reboots, and requires GUI navigation
- You need to search through things you've copied before but have no way to do it
- Working across multiple terminals/IDEs and need quick access to previous copies

**The cost of these frustrations:**

- **Lost productivity**: Re-finding that code snippet, URL, or text you just had
- **Broken flow**: Interrupting your work to hunt down information you already copied
- **Lost context**: Important snippets that could have saved hours, gone forever
- **Repeated work**: Copying the same things over and over because history is lost

**Real scenario**: You're coding and copy 5 different code blocks while debugging. You need block #3 but it's gone - you have to go find it again. Time wasted: 5-10 minutes. Multiple times a day. Every day.

---

## ✅ The Solution

**ClipStack** is a CLI-first clipboard history manager that:

1. **Stores everything you copy** (up to 100+ entries by default)
2. **Persists across sessions** - your history survives reboots
3. **Enables instant recall** - `clipstack get 3` retrieves your 3rd most recent copy
4. **Supports powerful search** - find that code snippet from last week with regex
5. **Works from the terminal** - no GUI required, perfect for developers
6. **Cross-platform** - Windows, Linux, and macOS supported
7. **Zero dependencies option** - works with Python stdlib only for basic features

**Result**: What took 5-10 minutes now takes 2 seconds. Your clipboard becomes a searchable knowledge base.

---

## ✨ Features

### Core Features

| Feature | Description |
|---------|-------------|
| 📚 **History Storage** | Store 100+ clipboard entries in SQLite database |
| 🔒 **Persistence** | History survives system reboots and restarts |
| 🔍 **Search** | Find entries with keyword or regex search |
| 📋 **Quick Recall** | Get any entry by position: `clipstack get 3` |
| 🔄 **Copy Back** | Restore any entry to active clipboard |
| 📌 **Pin Important** | Pin entries to protect from pruning |
| 📊 **Statistics** | Track your clipboard usage |
| 📤 **Export/Import** | Backup and restore history as JSON |
| 👁️ **Watch Mode** | Auto-capture clipboard changes |
| 🖥️ **Cross-Platform** | Works on Windows, Linux, and macOS |

### Power Features

- **Duplicate Detection**: Same content updates timestamp instead of creating duplicates
- **Automatic Pruning**: Old entries are automatically removed (configurable limit)
- **Character/Word Counts**: Track content size at a glance
- **Source Tracking**: Know where each entry came from (clipboard, manual, import)
- **Timestamp Formatting**: Human-readable "Today", "Yesterday", or full date
- **Regex Search**: Find complex patterns with full regex support

---

## 🚀 Quick Start

### 30-Second Setup

```bash
# Clone the repository
git clone https://github.com/DonkRonk17/ClipStack.git
cd ClipStack

# That's it! Run it
python clipstack.py list
```

### First Commands to Try

```bash
# Capture current clipboard content
python clipstack.py capture

# Copy something, then list your history
python clipstack.py list

# Get the 3rd most recent entry
python clipstack.py get 3

# Search for something
python clipstack.py search "function"

# Copy an entry back to clipboard
python clipstack.py copy 2
```

**That's it!** You're now managing your clipboard history like a pro.

---

## 📦 Installation

### Method 1: Clone and Run (Recommended)

```bash
# Clone repository
git clone https://github.com/DonkRonk17/ClipStack.git
cd ClipStack

# Run directly
python clipstack.py --help
```

### Method 2: Install with pip

```bash
# Clone repository
git clone https://github.com/DonkRonk17/ClipStack.git
cd ClipStack

# Install
pip install -e .

# Now you can use 'clipstack' from anywhere
clipstack --help
```

### Method 3: Add to PATH

```bash
# Add ClipStack directory to your PATH
# Windows (PowerShell):
$env:PATH += ";C:\path\to\ClipStack"

# Linux/macOS:
export PATH="$PATH:/path/to/ClipStack"
```

### Optional Dependencies

ClipStack works with Python stdlib only, but for enhanced clipboard access:

```bash
# Optional: Better cross-platform clipboard support
pip install pyperclip
```

**Platform-specific requirements:**

- **Windows**: Works out of the box (uses PowerShell)
- **Linux**: Requires `xclip` or `xsel` (`sudo apt install xclip`)
- **macOS**: Works out of the box (uses `pbcopy`/`pbpaste`)

---

## 💻 Usage

### CLI Commands

#### List Recent Entries

```bash
# List last 10 entries (default)
clipstack list

# List last 20 entries
clipstack list --last 20

# Shorthand
clipstack ls -n 20
```

**Example Output:**
```
[CLIPBOARD HISTORY] Showing 5 most recent entries
----------------------------------------------------------------------
    1       Today 14:32  (   45 chars)  def hello_world(): print("Hi")
    2       Today 14:30  (  123 chars)  https://github.com/DonkRonk17...
    3  [*]  Today 14:25  (   67 chars)  Important API key: sk-abc123...
    4       Yesterday    (  234 chars)  SELECT * FROM users WHERE id...
    5       Jan 20 10:15 (   89 chars)  const fetchData = async () =>...
----------------------------------------------------------------------
[TIP] Use 'clipstack get <n>' to view full entry
```

#### Get a Specific Entry

```bash
# Get most recent entry
clipstack get 1

# Get 3rd most recent
clipstack get 3

# Get content only (no metadata)
clipstack get 3 --quiet
```

**Example Output:**
```
[ENTRY #3]
Timestamp: Today 14:25
Source: clipboard
Characters: 67
Words: 8
Pinned: Yes
----------------------------------------
Important API key: sk-abc123def456...
----------------------------------------
```

#### Copy Entry Back to Clipboard

```bash
# Copy most recent entry
clipstack copy 1

# Copy 5th entry to clipboard
clipstack copy 5

# Shorthand
clipstack c 3
```

**Output:**
```
[OK] Entry #3 copied to clipboard
[CONTENT] def hello_world(): print("Hi")
```

#### Search Clipboard History

```bash
# Simple search
clipstack search "function"

# Regex search
clipstack search "def \w+\(\)"

# Limit results
clipstack search "SELECT" --limit 5

# Shorthand
clipstack s "error" -n 10
```

**Example Output:**
```
[SEARCH RESULTS] Found 3 matches for 'function'
----------------------------------------------------------------------
    1  Today 14:32     def hello_world(): **function** content...
    2  Jan 20 10:15    const fetchData = async **function** ()...
    3  Jan 19 16:45    # Python **function** decorator pattern...
----------------------------------------------------------------------
```

#### Add Entry Manually

```bash
# Add text directly
clipstack add "Important note: Remember to check logs"

# Add multi-word text
clipstack add API key for production: sk-live-123456
```

#### Capture Current Clipboard

```bash
# One-time capture
clipstack capture

# Shorthand
clipstack cap
```

#### Watch Mode (Auto-Capture)

```bash
# Start watching clipboard for changes
clipstack watch
```

**Output:**
```
[CLIPSTACK WATCH MODE]
Monitoring clipboard for changes...
Press Ctrl+C to stop
----------------------------------------
[14:32:15] Captured: def hello_world(): print("Hi")
[14:32:30] Captured: https://github.com/DonkRonk17/ClipStack
[14:33:01] Captured: SELECT * FROM users WHERE active = 1
```

#### Pin/Unpin Important Entries

```bash
# Pin entry #3 (won't be pruned)
clipstack pin 3

# Unpin entry #3
clipstack unpin 3
```

#### Delete Entries

```bash
# Delete specific entry
clipstack delete 5

# Shorthand
clipstack rm 5
```

#### Clear History

```bash
# Clear all (keeps pinned by default)
clipstack clear --force

# Clear including pinned
clipstack clear --force --all

# Preview what would be cleared (no --force)
clipstack clear
```

#### View Statistics

```bash
clipstack stats
```

**Output:**
```
[CLIPSTACK STATISTICS]
----------------------------------------
  Total entries:    47
  Pinned entries:   3
  Total characters: 12,456
  Total words:      2,134
  Oldest entry:     Jan 15 09:30
  Newest entry:     Today 14:32
  Database size:    48.2 KB
  Database path:    C:\Users\logan\.clipstack\history.db
----------------------------------------
```

#### Export/Import History

```bash
# Export to JSON file
clipstack export -o backup.json

# Export to stdout
clipstack export

# Import from file
clipstack import backup.json
```

---

### Python API

ClipStack can also be used as a Python library:

```python
from clipstack import ClipStack

# Initialize
cs = ClipStack()

# Add entry
entry_id = cs.add("Hello, World!")

# Get most recent
content = cs.get(1)
print(content)  # "Hello, World!"

# List recent entries
entries = cs.list(limit=10)
for entry in entries:
    print(f"{entry['timestamp']}: {entry['content'][:50]}")

# Search
results = cs.search("function")
for r in results:
    print(r['content'])

# Copy back to clipboard
cs.copy(3)

# Pin important entry
cs.pin(1)

# Get statistics
stats = cs.stats()
print(f"Total entries: {stats['total_entries']}")

# Export
backup = cs.export(format='json')

# Import
cs.import_history(backup, format='json')

# Clean up
cs.close()
```

---

## 📚 Real-World Examples

### Example 1: Developer Workflow

You're debugging and need to copy multiple error messages:

```bash
# Copy first error to clipboard, then capture
clipstack capture

# Copy second error
clipstack capture

# Copy stack trace
clipstack capture

# Now review all three
clipstack list -n 3

# Get the first error you copied (now at position 3)
clipstack get 3

# Copy it back to paste into bug report
clipstack copy 3
```

### Example 2: Research Session

Copying multiple URLs while researching:

```bash
# Start watch mode to auto-capture everything
clipstack watch
# (Copy URLs as you browse)
# Ctrl+C to stop

# Find that article about React
clipstack search "react hooks"

# Copy it back
clipstack copy 1
```

### Example 3: Protecting Important Data

```bash
# You copied an API key you need to keep safe
clipstack capture

# Pin it so it won't be deleted
clipstack pin 1

# Even when you clear history, it stays
clipstack clear --force
clipstack list  # Pinned entry still there!
```

### Example 4: Daily Backup

```bash
# Export your clipboard history daily
clipstack export -o clipboard_backup_2026-01-22.json

# Restore after system reset
clipstack import clipboard_backup_2026-01-22.json
```

---

## 🔧 How It Works

### Architecture

```
ClipStack
├── ClipStackDB          # SQLite database manager
│   ├── add_entry()      # Store new clipboard content
│   ├── get_entry()      # Retrieve by position
│   ├── search()         # Search with regex support
│   ├── pin/unpin()      # Protect entries from pruning
│   └── export/import()  # Backup/restore
├── ClipboardAccess      # Cross-platform clipboard access
│   ├── get_clipboard()  # Read from system clipboard
│   └── set_clipboard()  # Write to system clipboard
└── ClipboardWatcher     # Background auto-capture daemon
    ├── start()          # Begin watching
    └── stop()           # Stop watching
```

### Data Storage

ClipStack uses SQLite for reliable, persistent storage:

```sql
clipboard_history (
    id INTEGER PRIMARY KEY,
    content TEXT,
    content_hash TEXT,      -- For duplicate detection
    timestamp TEXT,
    source TEXT,            -- 'clipboard', 'manual', 'import'
    char_count INTEGER,
    word_count INTEGER,
    pinned INTEGER
)
```

**Database Location:**
- Windows: `C:\Users\<username>\.clipstack\history.db`
- Linux/macOS: `~/.clipstack/history.db`

### Cross-Platform Support

| Platform | Clipboard Method | Requirements |
|----------|-----------------|--------------|
| Windows | PowerShell `Get-Clipboard`/`Set-Clipboard` | Built-in |
| Linux | `xclip` or `xsel` | `sudo apt install xclip` |
| macOS | `pbcopy`/`pbpaste` | Built-in |

If `pyperclip` is installed, it's used as the primary method for all platforms.

---

## ⚙️ Configuration

### Custom Database Location

```bash
# Use custom database path
clipstack --db /path/to/custom.db list
```

```python
from clipstack import ClipStack
from pathlib import Path

# Python API with custom path
cs = ClipStack(db_path=Path("/path/to/custom.db"))
```

### History Size

The default history limit is 100 entries. Older entries are automatically pruned (except pinned entries). To modify, edit the `DEFAULT_HISTORY_SIZE` constant in `clipstack.py`.

### Watch Poll Interval

The watch mode checks for clipboard changes every 0.5 seconds. Modify `WATCH_POLL_INTERVAL` in `clipstack.py` to adjust.

---

## 🔗 Integration

### With Team Brain Tools

ClipStack integrates seamlessly with other Team Brain tools:

**With SynapseLink:**
```python
from synapselink import quick_send
from clipstack import ClipStack

cs = ClipStack()

# Share important clipboard content with team
content = cs.get(1)
quick_send("TEAM", "Shared Clipboard Entry", content)
```

**With TaskFlow:**
```python
from taskflow import TaskFlow
from clipstack import ClipStack

tf = TaskFlow()
cs = ClipStack()

# Add task from clipboard
task_content = cs.get(1)
tf.add_task(f"Review: {task_content[:50]}...")
```

### Shell Integration

**PowerShell Function:**
```powershell
# Add to $PROFILE
function cget { param($n=1) python C:\path\to\ClipStack\clipstack.py get $n --quiet }
function clist { python C:\path\to\ClipStack\clipstack.py list $args }
function csearch { param($term) python C:\path\to\ClipStack\clipstack.py search $term }
```

**Bash Aliases:**
```bash
# Add to ~/.bashrc
alias cget='python /path/to/ClipStack/clipstack.py get'
alias clist='python /path/to/ClipStack/clipstack.py list'
alias csearch='python /path/to/ClipStack/clipstack.py search'
```

---

## 🔍 Troubleshooting

### Common Issues

**"Clipboard is empty or unavailable"**
- Ensure clipboard access permissions
- On Linux, install `xclip`: `sudo apt install xclip`
- Try installing `pyperclip`: `pip install pyperclip`

**"No entries found"**
- Use `clipstack capture` to manually capture current clipboard
- Use `clipstack watch` to auto-capture changes
- Check if database exists: `clipstack stats`

**"Permission denied" on database**
- Check write permissions to `~/.clipstack/`
- Use `--db` flag to specify alternative location

**"Unicode characters not displaying"**
- Ensure terminal supports UTF-8
- On Windows: `chcp 65001` to enable UTF-8

### Debug Mode

```bash
# Check database status
clipstack stats

# Verify clipboard access
python -c "from clipstack import ClipboardAccess; ca = ClipboardAccess(); print(ca.get_clipboard())"
```

---

## 📖 API Reference

### ClipStack Class

| Method | Arguments | Returns | Description |
|--------|-----------|---------|-------------|
| `add(content, source)` | str, str | int | Add entry, returns ID |
| `capture()` | - | int\|None | Capture current clipboard |
| `get(position)` | int | str\|None | Get content by position |
| `get_entry(position)` | int | dict\|None | Get full entry with metadata |
| `list(limit)` | int | list[dict] | List recent entries |
| `copy(position)` | int | bool | Copy entry to clipboard |
| `search(query, limit)` | str, int | list[dict] | Search entries |
| `delete(position)` | int | bool | Delete entry |
| `clear(keep_pinned)` | bool | int | Clear history |
| `pin(position)` | int | bool | Pin entry |
| `unpin(position)` | int | bool | Unpin entry |
| `stats()` | - | dict | Get statistics |
| `export(format)` | str | str | Export history |
| `import_history(data, format)` | str, str | int | Import history |
| `start_watch()` | - | - | Start auto-capture |
| `stop_watch()` | - | - | Stop auto-capture |
| `close()` | - | - | Clean up resources |

### Entry Dictionary

```python
{
    'id': int,
    'content': str,
    'content_hash': str,
    'timestamp': str,  # ISO format
    'source': str,     # 'clipboard', 'manual', 'import'
    'char_count': int,
    'word_count': int,
    'pinned': int      # 0 or 1
}
```

---

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/1cee41cf-38d8-484a-bfc8-b464e39321bf" />


## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python test_clipstack.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/DonkRonk17/ClipStack.git
cd ClipStack
pip install -e .
python test_clipstack.py  # Run tests
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 📝 Credits

**Built by:** ATLAS (Team Brain)  
**For:** Logan Smith / Metaphy LLC  
**Requested by:** Logan Smith  
**Why:** "When coding or writing, I constantly copy multiple things but can only access the most recent clipboard item. I lose valuable snippets, code blocks, and URLs that I copied earlier."  
**Part of:** Beacon HQ / Team Brain Ecosystem  
**Date:** January 22, 2026

**Special Thanks:**
- Logan for the clear problem statement and feature requirements
- The Team Brain collective for testing and feedback
- Inspiration from clipboard managers: Paste (macOS), Ditto (Windows), parcellite (Linux)

---

## 📊 Test Results

```
======================================================================
TESTING: ClipStack v1.0
Clipboard History Manager for Power Users
======================================================================
Ran 57 tests in 1.233s

[OK] Passed: 57
Pass Rate: 100.0%
======================================================================
```

---

## 🗺️ Roadmap

**v1.1 (Planned):**
- [ ] TUI mode with arrow key navigation
- [ ] Image clipboard support
- [ ] Encrypted storage option
- [ ] Tagging system for organization

**v2.0 (Future):**
- [ ] Sync across devices
- [ ] Web interface
- [ ] Browser extension
- [ ] Mobile app

---

**Never lose a copied snippet again. ClipStack has your back.** 📋✨
