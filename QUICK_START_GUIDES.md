# ClipStack - Quick Start Guides

## 📖 ABOUT THESE GUIDES

Each Team Brain agent has a **5-minute quick-start guide** tailored to their role and workflows.

**Choose your guide:**
- [Forge (Orchestrator)](#-forge-quick-start)
- [Atlas (Executor)](#-atlas-quick-start)
- [Clio (Linux Agent)](#-clio-quick-start)
- [Nexus (Multi-Platform)](#-nexus-quick-start)
- [Bolt (Free Executor)](#-bolt-quick-start)

---

## 🔥 FORGE QUICK START

**Role:** Orchestrator / Reviewer  
**Time:** 5 minutes  
**Goal:** Use ClipStack to access clipboard history during reviews and coordination

### Step 1: Installation Check

```bash
# Verify ClipStack is available
cd C:\Users\logan\OneDrive\Documents\AutoProjects\ClipStack
python clipstack.py --version

# Expected: ClipStack v1.0.0
```

### Step 2: First Use - View Clipboard History

```python
# In your Forge session
from clipstack import ClipStack

cs = ClipStack()

# Check if there's any history
entries = cs.list(limit=10)
print(f"Found {len(entries)} clipboard entries")

# View most recent
if entries:
    print(f"Most recent: {entries[0]['content'][:100]}...")

cs.close()
```

### Step 3: Integration with Forge Workflows

**Use Case 1: Review code from session history**
```python
from clipstack import ClipStack

cs = ClipStack()

# Search for code snippets
code = cs.search("def ")
print(f"Found {len(code)} Python functions in history:")
for c in code[:5]:
    print(f"  - {c['content'][:60]}...")

cs.close()
```

**Use Case 2: Find previous context**
```python
from clipstack import ClipStack

cs = ClipStack()

# Search for specific content
results = cs.search("API")
if results:
    print("Found API-related content:")
    for r in results:
        print(f"  [{r['timestamp'][:10]}] {r['content'][:50]}...")

cs.close()
```

### Step 4: Common Forge Commands

```bash
# CLI usage (if preferred)
python clipstack.py list --last 20
python clipstack.py search "config"
python clipstack.py stats
```

### Next Steps for Forge

1. Read [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) - Forge section
2. Try [EXAMPLES.md](EXAMPLES.md) - Example 3 (Research Session)
3. Use during code reviews to find previous snippets

---

## ⚡ ATLAS QUICK START

**Role:** Executor / Builder  
**Time:** 5 minutes  
**Goal:** Use ClipStack to store and recall code snippets during tool development

### Step 1: Installation Check

```bash
cd C:\Users\logan\OneDrive\Documents\AutoProjects\ClipStack
python -c "from clipstack import ClipStack; print('OK')"
```

### Step 2: First Use - Store Build Snippets

```python
# During tool development
from clipstack import ClipStack

cs = ClipStack()

# Store reusable code pattern
cs.add("""
def run_tests():
    print("=" * 70)
    print("TESTING: ToolName v1.0")
    print("=" * 70)
    # Run tests...
""", source="atlas_build")

# Verify it's stored
content = cs.get(1)
print(f"Stored: {content[:50]}...")

cs.close()
```

### Step 3: Integration with Build Workflows

**During Tool Creation:**
```python
from clipstack import ClipStack

cs = ClipStack()

# Store important patterns during builds
patterns = [
    ("error_handler", "try:\n    result = func()\nexcept Exception as e:\n    print(f'Error: {e}')"),
    ("argparse_template", "parser = argparse.ArgumentParser(description='Tool')"),
    ("test_class", "class TestTool(unittest.TestCase):\n    def setUp(self):\n        pass"),
]

for name, code in patterns:
    cs.add(code, source=f"atlas_{name}")

# Pin the important ones
cs.pin(1)  # Most recent

cs.close()
```

**Recall Patterns:**
```python
from clipstack import ClipStack

cs = ClipStack()

# Find specific pattern
patterns = cs.search("argparse")
if patterns:
    print("Found argparse template:")
    print(patterns[0]['content'])

cs.close()
```

### Step 4: Common Atlas Commands

```bash
# Capture current clipboard during work
python clipstack.py capture

# List what you've copied today
python clipstack.py list -n 20

# Search for patterns
python clipstack.py search "def "

# Pin important code
python clipstack.py pin 1
```

### Next Steps for Atlas

1. Integrate into Holy Grail automation
2. Use during every tool build to track snippets
3. Export useful patterns: `python clipstack.py export -o patterns.json`

---

## 🐧 CLIO QUICK START

**Role:** Linux / Ubuntu Agent  
**Time:** 5 minutes  
**Goal:** Use ClipStack for CLI-first clipboard management on Linux

### Step 1: Linux Installation

```bash
# Clone from GitHub (if not already present)
cd ~/projects
git clone https://github.com/DonkRonk17/ClipStack.git
cd ClipStack

# Verify Python 3
python3 --version

# Install xclip for clipboard access
sudo apt install xclip

# Test it works
echo "test" | xclip -selection clipboard
xclip -selection clipboard -o  # Should print "test"

# Verify ClipStack
python3 clipstack.py --version
```

### Step 2: First Use - CLI Workflow

```bash
# Copy something to clipboard, then capture
echo "Hello from Clio" | xclip -selection clipboard
python3 clipstack.py capture

# List entries
python3 clipstack.py list

# Search
python3 clipstack.py search "Clio"

# Get content only (great for piping)
python3 clipstack.py get 1 --quiet
```

### Step 3: Integration with Clio Workflows

**Set up aliases (add to ~/.bashrc):**
```bash
# ClipStack aliases for Clio
alias cs='python3 ~/projects/ClipStack/clipstack.py'
alias cl='cs list'
alias cg='cs get'
alias cc='cs capture'
alias csearch='cs search'

# Reload
source ~/.bashrc
```

**Now use easily:**
```bash
cl          # List entries
cg 1        # Get most recent
cg 2 -q     # Get content only
csearch "sudo"
cc          # Capture current clipboard
```

**Watch mode for sessions:**
```bash
# Start watching in background
cs watch &

# Work normally, everything is captured
# When done:
kill %1  # Stop background watch
```

### Step 4: Common Clio Commands

```bash
# Quick operations
cs list -n 5                    # Last 5 entries
cs get 1 -q | xclip -sel clip   # Copy entry back to clipboard
cs search "error" -n 10         # Find errors
cs add "remember this"          # Add manually
cs stats                        # Check database status
```

### Next Steps for Clio

1. Add aliases to ~/.bashrc
2. Use during terminal sessions
3. Export backups periodically: `cs export -o ~/backups/clipboard_$(date +%Y%m%d).json`

---

## 🌐 NEXUS QUICK START

**Role:** Multi-Platform Agent  
**Time:** 5 minutes  
**Goal:** Use ClipStack consistently across Windows, Linux, and macOS

### Step 1: Platform Detection

```python
import platform
from clipstack import ClipStack

cs = ClipStack()

print(f"Platform: {platform.system()}")
print(f"Database: {cs.stats()['database_path']}")

# ClipStack works identically on all platforms!
cs.close()
```

### Step 2: First Use - Cross-Platform Testing

```python
from clipstack import ClipStack
import platform

cs = ClipStack()

# Platform-agnostic operations
cs.add(f"Test from {platform.system()}")

# Capture clipboard (works on all platforms)
result = cs.capture()
if result:
    print(f"Captured clipboard on {platform.system()}")

# List works everywhere
entries = cs.list(limit=5)
for e in entries:
    print(f"  {e['timestamp']}: {e['content'][:40]}...")

cs.close()
```

### Step 3: Platform-Specific Considerations

**Windows:**
```bash
# Works out of the box
python clipstack.py list
```

**Linux:**
```bash
# Requires xclip
sudo apt install xclip
python3 clipstack.py list
```

**macOS:**
```bash
# Works out of the box (uses pbcopy/pbpaste)
python3 clipstack.py list
```

**Cross-Platform Export/Import:**
```python
from clipstack import ClipStack
from pathlib import Path
import platform

cs = ClipStack()

# Export from current platform
backup = cs.export(format='json')
backup_file = Path(f"clipboard_{platform.system().lower()}.json")
backup_file.write_text(backup)
print(f"Exported to {backup_file}")

# Can import on any platform!
# other_backup = Path("clipboard_linux.json").read_text()
# cs.import_history(other_backup)

cs.close()
```

### Step 4: Common Nexus Commands

```bash
# Same commands work everywhere
clipstack list
clipstack search "function"
clipstack stats
clipstack export -o backup.json
```

### Next Steps for Nexus

1. Test on all 3 platforms
2. Use for cross-platform development projects
3. Export/import to share context between platforms

---

## 🆓 BOLT QUICK START

**Role:** Free Executor (Cline + Grok)  
**Time:** 5 minutes  
**Goal:** Use ClipStack to save time and reduce repeated work (FREE!)

### Step 1: Verify Free Access

```bash
# No API key required! ClipStack is 100% free
python clipstack.py --version

# Check it works
python clipstack.py stats
```

### Step 2: First Use - Save Time

```bash
# Scenario: You copied something important, then lost it

# Capture what's currently in clipboard
python clipstack.py capture

# Or manually add something important
python clipstack.py add "Remember: API endpoint is /api/v2/users"

# List to verify
python clipstack.py list
```

### Step 3: Integration with Bolt Workflows

**Use Case: Avoid Re-Finding Information**
```bash
# During task execution, you need something you copied earlier

# Search for it
python clipstack.py search "config"
python clipstack.py search "API"
python clipstack.py search "password"

# Found it! Copy back to clipboard
python clipstack.py copy 1
```

**Use Case: Track Task Results**
```bash
# After completing a task, save the result
python clipstack.py add "Task 123 completed: 57 tests passing, all checks green"

# Pin important results
python clipstack.py pin 1
```

### Step 4: Common Bolt Commands

```bash
# Quick operations (no cost!)
python clipstack.py capture          # Save current clipboard
python clipstack.py list -n 5        # Quick look at recent
python clipstack.py search "error"   # Find something specific
python clipstack.py copy 2           # Get it back
python clipstack.py add "note"       # Save a note
```

### Cost Savings

ClipStack helps Bolt save API tokens by:
- **Avoiding re-prompts**: Find context from clipboard instead of asking again
- **Reducing repeated work**: Recall code/config instead of regenerating
- **Quick lookups**: Search history instead of web searches

### Next Steps for Bolt

1. Use `clipstack capture` frequently during tasks
2. Search history before asking for information again
3. Add task results to history for future reference

---

## 📚 ADDITIONAL RESOURCES

**For All Agents:**
- Full Documentation: [README.md](README.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Integration Plan: [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)

**Support:**
- GitHub Issues: https://github.com/DonkRonk17/ClipStack/issues
- Synapse: Post in THE_SYNAPSE/active/
- Direct: Message ATLAS

---

**Last Updated:** January 22, 2026  
**Maintained By:** ATLAS (Team Brain)
