# ClipStack - Integration Plan

## 🎯 INTEGRATION GOALS

This document outlines how ClipStack integrates with:
1. Team Brain agents (Forge, Atlas, Clio, Nexus, Bolt)
2. Existing Team Brain tools
3. BCH (Beacon Command Hub)
4. Logan's workflows

---

## 📦 BCH INTEGRATION

### Overview

ClipStack can be integrated into BCH as a utility command, allowing Logan to manage clipboard history through the BCH interface on desktop or mobile.

### BCH Commands (Proposed)

```
@clipboard list              # List recent clipboard entries
@clipboard get <n>           # Get specific entry
@clipboard search <term>     # Search clipboard history
@clipboard copy <n>          # Copy entry to clipboard (desktop only)
@clipboard stats             # Show statistics
```

### Implementation Steps

1. **Add ClipStack to BCH imports:**
   ```python
   from clipstack import ClipStack
   ```

2. **Create BCH command handler:**
   ```python
   class ClipboardHandler:
       def __init__(self):
           self.cs = ClipStack()
       
       def handle_command(self, cmd, args):
           if cmd == "list":
               return self.format_list(self.cs.list(limit=10))
           elif cmd == "get":
               return self.cs.get(int(args[0]))
           elif cmd == "search":
               return self.format_results(self.cs.search(" ".join(args)))
           # ... etc
   ```

3. **Add to BCH command router:**
   ```python
   COMMAND_HANDLERS = {
       "clipboard": ClipboardHandler(),
       # ... other handlers
   }
   ```

4. **Desktop-specific features:**
   - `@clipboard copy` only available on desktop (requires clipboard access)
   - Mobile can view but not copy to device clipboard

### Integration Priority

**Priority: MEDIUM** - Nice to have for BCH but ClipStack works standalone.

---

## 🤖 AI AGENT INTEGRATION

### Integration Matrix

| Agent | Use Case | Integration Method | Priority |
|-------|----------|-------------------|----------|
| **Forge** | Review code snippets from sessions | Python API | HIGH |
| **Atlas** | Store build artifacts, track copied code | Python API + CLI | HIGH |
| **Clio** | Linux CLI workflows, quick recall | CLI | HIGH |
| **Nexus** | Cross-platform development | Python API | MEDIUM |
| **Bolt** | Task execution, code storage | CLI | MEDIUM |

### Agent-Specific Workflows

#### Forge (Orchestrator / Reviewer)

**Primary Use Case:** Access clipboard history when reviewing code or coordinating tasks.

**Integration Steps:**
1. Import ClipStack in Forge sessions
2. Use to recall context from previous operations
3. Search for specific code patterns across clipboard history

**Example Workflow:**
```python
# Forge session reviewing code
from clipstack import ClipStack

cs = ClipStack()

# Find all code snippets with a specific pattern
code_snippets = cs.search("def ")
print(f"Found {len(code_snippets)} Python functions in clipboard history")

for snippet in code_snippets[:5]:
    print(f"- {snippet['timestamp']}: {snippet['content'][:60]}...")

cs.close()
```

**When Forge Uses ClipStack:**
- Reviewing code that was previously copied
- Finding context from earlier in a session
- Searching for specific patterns or keywords
- Exporting relevant snippets for documentation

#### Atlas (Executor / Builder)

**Primary Use Case:** Store code snippets during tool development, recall previously built components.

**Integration Steps:**
1. Capture code snippets during development
2. Search for reusable patterns
3. Export/import code libraries

**Example Workflow:**
```python
# Atlas tool development session
from clipstack import ClipStack

cs = ClipStack()

# During development, capture important snippets
cs.add("""
def handle_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[ERROR] {e}")
            return None
    return wrapper
""", source="atlas_build")

# Pin important patterns
cs.pin(1)

# Later, recall the pattern
decorator_pattern = cs.get(1)
print(decorator_pattern)

cs.close()
```

**When Atlas Uses ClipStack:**
- Building tools and storing useful snippets
- Recalling patterns from previous builds
- Sharing code between sessions
- Tracking code evolution during development

#### Clio (Linux / Ubuntu Agent)

**Primary Use Case:** CLI-first clipboard management on Linux systems.

**Platform Considerations:**
- Requires `xclip` installed: `sudo apt install xclip`
- Works in headless environments with X11 forwarding
- Integrates with bash workflows

**Example:**
```bash
# Clio CLI usage
clipstack capture  # Capture from X clipboard

# Search for specific content
clipstack search "sudo"

# Get the command you need
clipstack get 1 --quiet | xclip -selection clipboard
```

**Integration with Clio Workflows:**
```bash
# Add to Clio's .bashrc
alias cl='clipstack list'
alias cg='clipstack get'
alias cs='clipstack search'

# Watch mode for session recording
clipstack watch &  # Background auto-capture
```

#### Nexus (Multi-Platform Agent)

**Primary Use Case:** Cross-platform clipboard management during multi-platform testing.

**Cross-Platform Notes:**
- Works identically on Windows, Linux, macOS
- SQLite database format is portable
- Can export from one platform, import on another

**Example:**
```python
# Nexus cross-platform session
from clipstack import ClipStack
import platform

cs = ClipStack()

# Log platform-specific clipboard content
content = cs.capture()
if content:
    print(f"[{platform.system()}] Captured: {content[:50]}...")

# Export for cross-platform sharing
backup = cs.export(format='json')
Path(f"clipboard_{platform.system().lower()}.json").write_text(backup)

cs.close()
```

#### Bolt (Cline / Free Executor)

**Primary Use Case:** Quick clipboard operations during task execution.

**Cost Considerations:**
- ClipStack is FREE (no API calls)
- Reduces need to re-find information
- Saves tokens by avoiding context re-gathering

**Example:**
```bash
# Bolt task execution
# Need the config from earlier? Search for it
clipstack search "config"

# Copy it back
clipstack copy 1

# Add result to history for later
clipstack add "Task completed: Build passed with 57 tests"
```

---

## 🔗 INTEGRATION WITH OTHER TEAM BRAIN TOOLS

### With SynapseLink

**Notification Use Case:** Share clipboard entries with team or notify about important captures.

**Integration Pattern:**
```python
from synapselink import quick_send
from clipstack import ClipStack

cs = ClipStack()

# Capture important content
cs.capture()
content = cs.get(1)

# Share with team
quick_send(
    "FORGE,ATLAS",
    "Shared Clipboard Entry",
    f"Content:\n{content[:500]}...",
    priority="NORMAL"
)

cs.close()
```

### With AgentHealth

**Correlation Use Case:** Track clipboard activity as part of agent health monitoring.

**Integration Pattern:**
```python
from agenthealth import AgentHealth
from clipstack import ClipStack

health = AgentHealth()
cs = ClipStack()

# Start session with shared tracking
session_id = "atlas_session_001"
health.start_session("ATLAS", session_id=session_id)

# Track clipboard activity
stats = cs.stats()
health.log_activity("ATLAS", {
    "clipboard_entries": stats['total_entries'],
    "session_id": session_id
})

health.end_session("ATLAS", session_id=session_id)
cs.close()
```

### With TaskQueuePro

**Task Management Use Case:** Create tasks from clipboard content.

**Integration Pattern:**
```python
from taskqueuepro import TaskQueuePro
from clipstack import ClipStack

queue = TaskQueuePro()
cs = ClipStack()

# Find all TODO items in clipboard history
todos = cs.search("TODO")

for todo in todos:
    # Create task from clipboard content
    task_id = queue.create_task(
        title=f"Review: {todo['content'][:50]}...",
        agent="ATLAS",
        priority=2,
        metadata={"source": "clipstack", "clipboard_id": todo['id']}
    )
    print(f"Created task {task_id} from clipboard entry")

cs.close()
```

### With SessionReplay

**Debugging Use Case:** Include clipboard history in session recordings.

**Integration Pattern:**
```python
from sessionreplay import SessionReplay
from clipstack import ClipStack

replay = SessionReplay()
cs = ClipStack()

# Start session recording
session_id = replay.start_session("ATLAS", task="Debugging issue #123")

# Log clipboard activity
replay.log_input(session_id, "Clipboard entries at session start:")
for entry in cs.list(limit=5):
    replay.log_input(session_id, f"  - {entry['content'][:50]}")

# ... do work ...

# End session with clipboard state
replay.log_output(session_id, f"Clipboard entries at end: {cs.stats()['total_entries']}")
replay.end_session(session_id, status="COMPLETED")

cs.close()
```

### With ContextCompressor

**Token Optimization Use Case:** Compress large clipboard entries before sharing.

**Integration Pattern:**
```python
from contextcompressor import ContextCompressor
from clipstack import ClipStack

compressor = ContextCompressor()
cs = ClipStack()

# Get large clipboard entry
entry = cs.get_entry(1)
if entry and entry['char_count'] > 1000:
    # Compress before sharing
    compressed = compressor.compress_text(
        entry['content'],
        query="key information",
        method="summary"
    )
    print(f"Original: {entry['char_count']} chars")
    print(f"Compressed: {len(compressed.compressed_text)} chars")
    print(f"Savings: {compressed.estimated_token_savings} tokens")

cs.close()
```

### With ConfigManager

**Configuration Use Case:** Store ClipStack settings in centralized config.

**Integration Pattern:**
```python
from configmanager import ConfigManager
from clipstack import ClipStack
from pathlib import Path

config = ConfigManager()

# Get ClipStack config
clipstack_config = config.get("clipstack", {
    "history_limit": 100,
    "watch_interval": 0.5,
    "auto_capture": False
})

# Use custom database path from config
db_path = config.get("clipstack.db_path", None)
cs = ClipStack(db_path=Path(db_path) if db_path else None)

cs.close()
```

### With TokenTracker

**Cost Monitoring Use Case:** Track token usage of clipboard operations.

**Integration Pattern:**
```python
from tokentracker import TokenTracker
from clipstack import ClipStack

tracker = TokenTracker()
cs = ClipStack()

# Log clipboard activity in token tracker
stats = cs.stats()
tracker.log_activity({
    "tool": "ClipStack",
    "operation": "stats_check",
    "entries_count": stats['total_entries'],
    "total_chars": stats['total_characters'],
    "estimated_tokens": stats['total_characters'] // 4  # Rough estimate
})

cs.close()
```

### With MemoryBridge

**Persistence Use Case:** Sync important clipboard entries to memory core.

**Integration Pattern:**
```python
from memorybridge import MemoryBridge
from clipstack import ClipStack

memory = MemoryBridge()
cs = ClipStack()

# Get pinned (important) entries
entries = cs.list(limit=100)
pinned = [e for e in entries if e['pinned']]

# Sync to memory core
for entry in pinned:
    memory.set(f"clipboard_pinned_{entry['id']}", {
        "content": entry['content'],
        "timestamp": entry['timestamp'],
        "source": "clipstack"
    })

memory.sync()
cs.close()
```

---

## 🚀 ADOPTION ROADMAP

### Phase 1: Core Adoption (Week 1)

**Goal:** All agents aware and can use basic features

**Steps:**
1. ✓ Tool deployed to GitHub
2. ☐ Quick-start guides sent via Synapse
3. ☐ Each agent tests basic workflow
4. ☐ Feedback collected

**Success Criteria:**
- All 5 agents have used ClipStack at least once
- No blocking issues reported

### Phase 2: Integration (Week 2-3)

**Goal:** Integrated into daily workflows

**Steps:**
1. ☐ Add to agent startup routines
2. ☐ Create integration examples with SynapseLink
3. ☐ Update agent-specific workflows
4. ☐ Monitor usage patterns

**Success Criteria:**
- Used daily by at least 3 agents
- Integration with SynapseLink working

### Phase 3: Optimization (Week 4+)

**Goal:** Optimized and fully adopted

**Steps:**
1. ☐ Collect efficiency metrics
2. ☐ Implement v1.1 improvements
3. ☐ Create advanced workflow examples
4. ☐ Full Team Brain ecosystem integration

**Success Criteria:**
- Measurable time savings
- Positive feedback from all agents
- v1.1 features identified

---

## 📊 SUCCESS METRICS

**Adoption Metrics:**
- Number of agents using tool: Target 5/5
- Daily usage count: Track via stats
- Integration with other tools: Count integrations

**Efficiency Metrics:**
- Time saved per clipboard recall: ~30 seconds
- Code snippets recovered: Track per session
- Search success rate: Track found vs not found

**Quality Metrics:**
- Bug reports: Track and resolve
- Feature requests: Collect for v1.1
- User satisfaction: Qualitative feedback

---

## 🛠️ TECHNICAL INTEGRATION DETAILS

### Import Paths

```python
# Standard import
from clipstack import ClipStack

# Specific imports
from clipstack import ClipStack, ClipStackDB, ClipboardAccess
```

### Default Database Location

```
Windows: C:\Users\<user>\.clipstack\history.db
Linux:   /home/<user>/.clipstack/history.db
macOS:   /Users/<user>/.clipstack/history.db
```

### Return Types

```python
# Entry dictionary format
{
    'id': int,
    'content': str,
    'content_hash': str,
    'timestamp': str,      # ISO format
    'source': str,         # 'clipboard', 'manual', 'import'
    'char_count': int,
    'word_count': int,
    'pinned': int          # 0 or 1
}

# Stats dictionary format
{
    'total_entries': int,
    'pinned_entries': int,
    'total_characters': int,
    'total_words': int,
    'oldest_entry': str,   # timestamp
    'newest_entry': str,   # timestamp
    'database_size_bytes': int,
    'database_path': str
}
```

### Error Handling

```python
from clipstack import ClipStack

cs = ClipStack()

try:
    # Operations that might fail
    content = cs.get(999)  # Returns None if not found
    if content is None:
        print("Entry not found")
    
    # Search always returns list (empty if no results)
    results = cs.search("xyz")  # Returns [] if no matches
    
except Exception as e:
    print(f"Error: {e}")

finally:
    cs.close()  # Always close
```

---

## 🔧 MAINTENANCE & SUPPORT

### Update Strategy

- Minor updates (v1.x): Monthly
- Major updates (v2.0+): Quarterly
- Bug fixes: Immediate

### Support Channels

- GitHub Issues: Bug reports
- Synapse: Team Brain discussions
- Direct to ATLAS: Complex issues

### Known Limitations

- Watch mode requires foreground process (no true daemon yet)
- Image clipboard not supported (text only)
- Shared database across processes not recommended

### Planned Improvements (v1.1)

- True daemon mode for watch
- TUI interface option
- Image clipboard support
- Encrypted storage option

---

## 📚 ADDITIONAL RESOURCES

- Main Documentation: [README.md](README.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Quick Start Guides: [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)
- GitHub: https://github.com/DonkRonk17/ClipStack

---

**Last Updated:** January 22, 2026  
**Maintained By:** ATLAS (Team Brain)
