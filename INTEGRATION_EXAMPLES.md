# ClipStack - Integration Examples

## 🎯 INTEGRATION PHILOSOPHY

ClipStack is designed to work seamlessly with other Team Brain tools. This document provides **copy-paste-ready code examples** for common integration patterns.

---

## 📚 TABLE OF CONTENTS

1. [Pattern 1: ClipStack + SynapseLink](#pattern-1-clipstack--synapselink)
2. [Pattern 2: ClipStack + AgentHealth](#pattern-2-clipstack--agenthealth)
3. [Pattern 3: ClipStack + TaskQueuePro](#pattern-3-clipstack--taskqueuepro)
4. [Pattern 4: ClipStack + SessionReplay](#pattern-4-clipstack--sessionreplay)
5. [Pattern 5: ClipStack + TokenTracker](#pattern-5-clipstack--tokentracker)
6. [Pattern 6: ClipStack + ContextCompressor](#pattern-6-clipstack--contextcompressor)
7. [Pattern 7: ClipStack + MemoryBridge](#pattern-7-clipstack--memorybridge)
8. [Pattern 8: ClipStack + ConfigManager](#pattern-8-clipstack--configmanager)
9. [Pattern 9: Multi-Tool Workflow](#pattern-9-multi-tool-workflow)
10. [Pattern 10: Full Team Brain Stack](#pattern-10-full-team-brain-stack)

---

## Pattern 1: ClipStack + SynapseLink

**Use Case:** Share important clipboard entries with team members

**Why:** Quickly distribute code snippets, URLs, or notes to other agents

**Code:**

```python
from synapselink import quick_send
from clipstack import ClipStack

cs = ClipStack()

# Capture current clipboard
cs.capture()

# Get the most recent entry
entry = cs.get_entry(1)

if entry:
    # Share with team
    quick_send(
        "FORGE,ATLAS,CLIO",
        f"Shared Clipboard: {entry['content'][:50]}...",
        f"""Clipboard Entry Shared:
        
Content:
{entry['content']}

Metadata:
- Characters: {entry['char_count']}
- Words: {entry['word_count']}
- Captured: {entry['timestamp']}
- Source: {entry['source']}

Use ClipStack to access more of your history!
""",
        priority="NORMAL"
    )
    print("[OK] Shared clipboard entry with team")

cs.close()
```

**Result:** Team members receive the clipboard content via Synapse notification

---

## Pattern 2: ClipStack + AgentHealth

**Use Case:** Track clipboard activity as part of agent health monitoring

**Why:** Understand clipboard usage patterns alongside other health metrics

**Code:**

```python
from agenthealth import AgentHealth
from clipstack import ClipStack

# Initialize tools
health = AgentHealth()
cs = ClipStack()

# Start health session
session_id = "atlas_session_001"
health.start_session("ATLAS", session_id=session_id)

try:
    # Do work that involves clipboard...
    cs.capture()
    results = cs.search("function")
    
    # Log clipboard activity to health
    stats = cs.stats()
    health.log_custom_metric("ATLAS", {
        "clipboard_entries": stats['total_entries'],
        "clipboard_chars": stats['total_characters'],
        "search_results": len(results)
    })
    
    # Heartbeat with clipboard info
    health.heartbeat("ATLAS", status="active", metadata={
        "clipboard_active": True,
        "recent_entries": len(cs.list(limit=10))
    })
    
finally:
    health.end_session("ATLAS", session_id=session_id)
    cs.close()
```

**Result:** Clipboard activity is correlated with agent health data

---

## Pattern 3: ClipStack + TaskQueuePro

**Use Case:** Create tasks from clipboard content (TODOs, bugs, notes)

**Why:** Turn copied notes into trackable tasks automatically

**Code:**

```python
from taskqueuepro import TaskQueuePro
from clipstack import ClipStack

queue = TaskQueuePro()
cs = ClipStack()

# Find all TODOs in clipboard history
todos = cs.search("TODO")

print(f"Found {len(todos)} TODO items in clipboard history")

for todo in todos:
    # Extract task title (first line or first 50 chars)
    content = todo['content']
    title = content.split('\n')[0][:50] if '\n' in content else content[:50]
    
    # Create task in queue
    task_id = queue.create_task(
        title=f"From clipboard: {title}",
        agent="ATLAS",
        priority=2,
        metadata={
            "source": "clipstack",
            "clipboard_id": todo['id'],
            "full_content": content[:500],
            "captured_at": todo['timestamp']
        }
    )
    
    print(f"[OK] Created task {task_id}: {title}")

# Mark processed TODOs in clipboard
for todo in todos:
    cs.pin(1)  # Pin so they're not lost

cs.close()
```

**Result:** TODO items from clipboard become tracked tasks

---

## Pattern 4: ClipStack + SessionReplay

**Use Case:** Include clipboard history in session recordings for debugging

**Why:** When replaying a session, see what was in the clipboard at each point

**Code:**

```python
from sessionreplay import SessionReplay
from clipstack import ClipStack

replay = SessionReplay()
cs = ClipStack()

# Start session recording
session_id = replay.start_session("ATLAS", task="Debug issue #456")

# Log initial clipboard state
replay.log_input(session_id, "=== Initial Clipboard State ===")
for i, entry in enumerate(cs.list(limit=5), 1):
    preview = entry['content'][:60].replace('\n', ' ')
    replay.log_input(session_id, f"  [{i}] {preview}...")

# During debugging, capture relevant clipboard content
replay.log_action(session_id, "Copying error message from console")
cs.capture()
error = cs.get(1)
if error:
    replay.log_input(session_id, f"Captured: {error[:200]}")

# Search for related content
replay.log_action(session_id, "Searching clipboard for related errors")
related = cs.search("error")
replay.log_output(session_id, f"Found {len(related)} related clipboard entries")

# End session with clipboard summary
replay.log_output(session_id, f"Session clipboard stats: {cs.stats()}")
replay.end_session(session_id, status="COMPLETED")

cs.close()
```

**Result:** Session replay includes complete clipboard context

---

## Pattern 5: ClipStack + TokenTracker

**Use Case:** Track clipboard-related token usage

**Why:** Monitor how much context comes from clipboard vs new prompts

**Code:**

```python
from tokentracker import TokenTracker
from clipstack import ClipStack

tracker = TokenTracker()
cs = ClipStack()

# Get clipboard stats
stats = cs.stats()

# Estimate tokens in clipboard history
estimated_tokens = stats['total_characters'] // 4  # Rough estimate

# Log to token tracker
tracker.log_usage(
    agent="ATLAS",
    operation="clipboard_context",
    details={
        "tool": "ClipStack",
        "entries": stats['total_entries'],
        "characters": stats['total_characters'],
        "estimated_tokens": estimated_tokens,
        "action": "clipboard_history_check"
    },
    tokens_saved=estimated_tokens  # Tokens we didn't need to re-generate
)

# Report savings
print(f"[TOKENTRACKER] ClipStack history contains ~{estimated_tokens} tokens of reusable context")

# When using clipboard content instead of re-prompting
entry = cs.get(1)
if entry:
    entry_tokens = len(entry) // 4
    tracker.log_usage(
        agent="ATLAS",
        operation="clipboard_recall",
        details={
            "action": "recalled_from_clipboard",
            "chars": len(entry),
            "estimated_tokens": entry_tokens
        },
        tokens_saved=entry_tokens
    )
    print(f"[TOKENTRACKER] Saved ~{entry_tokens} tokens by using clipboard")

cs.close()
```

**Result:** Token usage includes clipboard-related savings

---

## Pattern 6: ClipStack + ContextCompressor

**Use Case:** Compress large clipboard entries before sharing or storing

**Why:** Reduce token usage when clipboard contains verbose content

**Code:**

```python
from contextcompressor import ContextCompressor
from clipstack import ClipStack

compressor = ContextCompressor()
cs = ClipStack()

# Get entries larger than 500 characters
entries = cs.list(limit=20)
large_entries = [e for e in entries if e['char_count'] > 500]

print(f"Found {len(large_entries)} large clipboard entries")

for entry in large_entries:
    # Compress the entry
    compressed = compressor.compress_text(
        entry['content'],
        query="key information and code",
        method="summary",
        target_ratio=0.3  # 30% of original size
    )
    
    print(f"\n[ENTRY {entry['id']}]")
    print(f"  Original: {entry['char_count']} chars (~{entry['char_count']//4} tokens)")
    print(f"  Compressed: {len(compressed.compressed_text)} chars (~{len(compressed.compressed_text)//4} tokens)")
    print(f"  Savings: {compressed.estimated_token_savings} tokens")
    print(f"  Summary: {compressed.compressed_text[:100]}...")

cs.close()
```

**Result:** Large clipboard entries are compressed for efficient sharing

---

## Pattern 7: ClipStack + MemoryBridge

**Use Case:** Sync important (pinned) clipboard entries to Memory Core

**Why:** Preserve critical clipboard content in long-term memory

**Code:**

```python
from memorybridge import MemoryBridge
from clipstack import ClipStack
from datetime import datetime

memory = MemoryBridge()
cs = ClipStack()

# Get all pinned entries (important content)
entries = cs.list(limit=100)
pinned = [e for e in entries if e['pinned']]

print(f"Found {len(pinned)} pinned clipboard entries to sync")

for entry in pinned:
    # Create memory key
    key = f"clipboard_important_{entry['id']}"
    
    # Store in Memory Bridge
    memory.set(key, {
        "content": entry['content'],
        "timestamp": entry['timestamp'],
        "source": "clipstack_pinned",
        "synced_at": datetime.now().isoformat(),
        "char_count": entry['char_count'],
        "word_count": entry['word_count']
    })
    
    print(f"[OK] Synced pinned entry {entry['id']} to Memory Core")

# Also save clipboard stats as a snapshot
memory.set("clipboard_stats_snapshot", {
    "snapshot_time": datetime.now().isoformat(),
    **cs.stats()
})

memory.sync()
print(f"[OK] Synced {len(pinned)} entries to Memory Core")

cs.close()
```

**Result:** Important clipboard content persisted to Memory Core

---

## Pattern 8: ClipStack + ConfigManager

**Use Case:** Centralize ClipStack configuration

**Why:** Consistent settings across all agents

**Code:**

```python
from configmanager import ConfigManager
from clipstack import ClipStack
from pathlib import Path

config = ConfigManager()

# Get or create ClipStack config
clipstack_config = config.get("clipstack", {
    "history_limit": 100,
    "watch_interval": 0.5,
    "auto_backup": False,
    "backup_path": None,
    "custom_db_path": None
})

# Use custom database path if configured
db_path = None
if clipstack_config.get("custom_db_path"):
    db_path = Path(clipstack_config["custom_db_path"])

cs = ClipStack(db_path=db_path)

# Apply configuration
if clipstack_config.get("auto_backup"):
    backup_path = clipstack_config.get("backup_path", "clipboard_backup.json")
    backup = cs.export(format='json')
    Path(backup_path).write_text(backup)
    print(f"[OK] Auto-backup saved to {backup_path}")

# Update config with current stats
config.set("clipstack.last_stats", cs.stats())
config.save()

print(f"[OK] ClipStack configured with history_limit={clipstack_config['history_limit']}")

cs.close()
```

**Result:** ClipStack uses centralized configuration

---

## Pattern 9: Multi-Tool Workflow

**Use Case:** Complete workflow combining multiple tools

**Why:** Demonstrate real-world integration scenario

**Code:**

```python
"""
Multi-Tool Workflow: Code Review with Clipboard Tracking
Combines: ClipStack, SessionReplay, SynapseLink, TokenTracker
"""

from clipstack import ClipStack
from sessionreplay import SessionReplay
from synapselink import quick_send
from tokentracker import TokenTracker

# Initialize tools
cs = ClipStack()
replay = SessionReplay()
tracker = TokenTracker()

# Start tracked session
session_id = replay.start_session("FORGE", task="Code review")
replay.log_action(session_id, "Starting code review with clipboard tracking")

try:
    # Capture initial clipboard state
    cs.capture()
    initial_count = cs.stats()['total_entries']
    replay.log_input(session_id, f"Initial clipboard entries: {initial_count}")
    
    # During review, capture code snippets
    code_snippets = [
        "def validate_input(data): return data is not None",
        "async function fetchUser(id) { return await api.get(`/users/${id}`); }",
        "SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at",
    ]
    
    for snippet in code_snippets:
        cs.add(snippet, source="code_review")
        replay.log_input(session_id, f"Captured code: {snippet[:50]}...")
    
    # Search for issues
    issues = cs.search("SELECT \\*")  # Bad practice: SELECT *
    if issues:
        replay.log_output(session_id, f"[WARNING] Found {len(issues)} SELECT * queries")
    
    # Calculate token savings
    stats = cs.stats()
    tokens_tracked = (stats['total_characters'] - initial_count * 100) // 4
    tracker.log_usage(
        agent="FORGE",
        operation="code_review_clipboard",
        tokens_saved=tokens_tracked,
        details={"snippets_captured": len(code_snippets)}
    )
    
    # End session and notify team
    replay.end_session(session_id, status="COMPLETED")
    
    # Send summary
    quick_send(
        "ATLAS,CLIO",
        "Code Review Complete",
        f"""Code review session completed.

Clipboard Stats:
- Snippets captured: {len(code_snippets)}
- Total entries: {stats['total_entries']}
- Issues found: {len(issues)} SELECT * queries

Tokens saved by reusing clipboard: ~{tokens_tracked}
""",
        priority="NORMAL"
    )
    
    print("[OK] Multi-tool workflow completed successfully")

except Exception as e:
    replay.log_error(session_id, str(e))
    replay.end_session(session_id, status="FAILED")
    raise

finally:
    cs.close()
```

**Result:** Fully integrated code review workflow

---

## Pattern 10: Full Team Brain Stack

**Use Case:** Ultimate integration - all major tools working together

**Why:** Production-grade agent operation with complete tooling

**Code:**

```python
"""
Full Team Brain Stack Integration
A complete agent session with all tools working together
"""

import sys
from pathlib import Path
from datetime import datetime

# Import all Team Brain tools
from clipstack import ClipStack
from synapselink import quick_send
from agenthealth import AgentHealth
from sessionreplay import SessionReplay
from tokentracker import TokenTracker
from taskqueuepro import TaskQueuePro
from configmanager import ConfigManager

class TeamBrainSession:
    """Complete Team Brain session with all tools integrated."""
    
    def __init__(self, agent_name: str, task_description: str):
        self.agent = agent_name
        self.task = task_description
        
        # Initialize all tools
        self.config = ConfigManager()
        self.clipboard = ClipStack()
        self.health = AgentHealth()
        self.replay = SessionReplay()
        self.tracker = TokenTracker()
        self.queue = TaskQueuePro()
        
        # Start session
        self.session_id = f"{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._start_session()
    
    def _start_session(self):
        """Initialize all tracking."""
        # Health monitoring
        self.health.start_session(self.agent, session_id=self.session_id)
        
        # Session replay
        self.replay.start_session(self.agent, task=self.task)
        
        # Log initial clipboard state
        stats = self.clipboard.stats()
        self.replay.log_input(self.session_id, f"Clipboard: {stats['total_entries']} entries")
        
        # Notify team
        quick_send(
            "TEAM",
            f"{self.agent} Session Started",
            f"Task: {self.task}\nSession: {self.session_id}",
            priority="LOW"
        )
    
    def capture_clipboard(self, description: str = ""):
        """Capture and log clipboard content."""
        entry_id = self.clipboard.capture()
        if entry_id:
            entry = self.clipboard.get_entry(1)
            self.replay.log_input(self.session_id, f"Clipboard captured: {description}")
            self.health.heartbeat(self.agent, status="active")
            return entry
        return None
    
    def search_clipboard(self, query: str) -> list:
        """Search clipboard and log."""
        results = self.clipboard.search(query)
        self.replay.log_action(self.session_id, f"Clipboard search: '{query}' ({len(results)} results)")
        
        # Track tokens saved by using clipboard instead of re-prompting
        if results:
            tokens = sum(r['char_count'] for r in results) // 4
            self.tracker.log_usage(
                agent=self.agent,
                operation="clipboard_search",
                tokens_saved=tokens,
                details={"query": query, "results": len(results)}
            )
        
        return results
    
    def create_task_from_clipboard(self, position: int, priority: int = 2):
        """Create task from clipboard entry."""
        entry = self.clipboard.get_entry(position)
        if entry:
            task_id = self.queue.create_task(
                title=f"Review: {entry['content'][:40]}...",
                agent=self.agent,
                priority=priority,
                metadata={"source": "clipboard", "clipboard_id": entry['id']}
            )
            self.replay.log_action(self.session_id, f"Created task {task_id} from clipboard")
            return task_id
        return None
    
    def end_session(self, status: str = "COMPLETED"):
        """Clean up and finalize session."""
        # Final stats
        stats = self.clipboard.stats()
        
        # Log final state
        self.replay.log_output(self.session_id, f"Final clipboard: {stats['total_entries']} entries")
        self.replay.end_session(self.session_id, status=status)
        
        # Health monitoring
        self.health.end_session(self.agent, session_id=self.session_id)
        
        # Notify team
        quick_send(
            "TEAM",
            f"{self.agent} Session {status}",
            f"Task: {self.task}\nSession: {self.session_id}\nClipboard entries: {stats['total_entries']}",
            priority="LOW"
        )
        
        # Cleanup
        self.clipboard.close()
        
        print(f"[OK] Session {self.session_id} ended: {status}")


# Example usage
if __name__ == "__main__":
    # Create integrated session
    session = TeamBrainSession("ATLAS", "Tool development with full tracking")
    
    try:
        # Work with clipboard
        session.capture_clipboard("Initial capture")
        
        # Search for relevant content
        code = session.search_clipboard("def ")
        print(f"Found {len(code)} function definitions")
        
        # Create task from clipboard content
        if code:
            session.create_task_from_clipboard(1, priority=2)
        
        # Successful completion
        session.end_session("COMPLETED")
        
    except Exception as e:
        session.end_session("FAILED")
        raise
```

**Result:** Complete production-grade session with all tools integrated

---

## 📊 RECOMMENDED INTEGRATION PRIORITY

**Week 1 (Essential):**
1. ✅ SynapseLink - Team notifications
2. ✅ SessionReplay - Debugging support
3. ✅ TokenTracker - Cost awareness

**Week 2 (Productivity):**
4. ☐ TaskQueuePro - Task creation from clipboard
5. ☐ AgentHealth - Activity correlation
6. ☐ ConfigManager - Centralized settings

**Week 3 (Advanced):**
7. ☐ ContextCompressor - Token optimization
8. ☐ MemoryBridge - Long-term persistence
9. ☐ Full stack integration

---

## 🔧 TROUBLESHOOTING INTEGRATIONS

**Import Errors:**
```python
# Ensure all tools are in Python path
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "OneDrive/Documents/AutoProjects"))

# Then import
from clipstack import ClipStack
from synapselink import quick_send
```

**ClipStack Database Not Found:**
```python
# Check default location
from clipstack import ClipStack
cs = ClipStack()
print(f"Database: {cs.stats()['database_path']}")
cs.close()

# Use custom path if needed
from pathlib import Path
cs = ClipStack(db_path=Path("/custom/path/clipstack.db"))
```

**Clipboard Access Issues:**
```bash
# Linux: Install xclip
sudo apt install xclip

# Test manually
echo "test" | xclip -selection clipboard
xclip -selection clipboard -o

# Python: Install pyperclip for better support
pip install pyperclip
```

**Version Conflicts:**
```bash
# Check versions
cd ~/OneDrive/Documents/AutoProjects/ClipStack
git pull origin main
python clipstack.py --version
```

---

**Last Updated:** January 22, 2026  
**Maintained By:** ATLAS (Team Brain)
