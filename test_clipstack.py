#!/usr/bin/env python3
"""
Comprehensive test suite for ClipStack - Clipboard History Manager.

Tests cover:
- Database operations (CRUD)
- Clipboard access
- Search functionality
- Pin/unpin operations
- Export/Import
- Statistics
- Edge cases
- Error handling

Run: python test_clipstack.py
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from clipstack import ClipStack, ClipStackDB, ClipboardAccess, truncate_text, format_timestamp


class TestClipStackDB(unittest.TestCase):
    """Test database operations."""
    
    def setUp(self):
        """Create temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_clipstack.db"
        self.db = ClipStackDB(self.db_path)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db.close()
        if self.db_path.exists():
            self.db_path.unlink()
        if Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_initialization(self):
        """Test database is created and initialized correctly."""
        self.assertTrue(self.db_path.exists())
        
        # Check tables exist
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        self.assertIn('clipboard_history', tables)
        self.assertIn('settings', tables)
    
    def test_add_entry(self):
        """Test adding clipboard entries."""
        entry_id = self.db.add_entry("Hello, World!")
        self.assertGreater(entry_id, 0)
        
        entry = self.db.get_entry(1)
        self.assertIsNotNone(entry)
        self.assertEqual(entry['content'], "Hello, World!")
        self.assertEqual(entry['source'], 'clipboard')
    
    def test_add_entry_with_source(self):
        """Test adding entry with custom source."""
        entry_id = self.db.add_entry("Manual entry", source="manual")
        entry = self.db.get_entry(1)
        
        self.assertEqual(entry['source'], 'manual')
    
    def test_add_empty_entry(self):
        """Test that empty entries are rejected."""
        result = self.db.add_entry("")
        self.assertEqual(result, -1)
        
        result = self.db.add_entry("   ")
        self.assertEqual(result, -1)
    
    def test_duplicate_detection(self):
        """Test that duplicate entries update timestamp instead of creating new."""
        self.db.add_entry("Same content")
        self.db.add_entry("Same content")
        
        # Should only have one entry
        entries = self.db.get_recent(limit=10)
        same_content_entries = [e for e in entries if e['content'] == "Same content"]
        self.assertEqual(len(same_content_entries), 1)
    
    def test_get_entry_by_position(self):
        """Test getting entries by position."""
        self.db.add_entry("First")
        self.db.add_entry("Second")
        self.db.add_entry("Third")
        
        # Position 1 = most recent
        entry = self.db.get_entry(1)
        self.assertEqual(entry['content'], "Third")
        
        # Position 3 = oldest
        entry = self.db.get_entry(3)
        self.assertEqual(entry['content'], "First")
    
    def test_get_nonexistent_position(self):
        """Test getting entry at invalid position."""
        self.db.add_entry("Only one")
        
        entry = self.db.get_entry(99)
        self.assertIsNone(entry)
        
        entry = self.db.get_entry(0)
        self.assertIsNone(entry)
        
        entry = self.db.get_entry(-1)
        self.assertIsNone(entry)
    
    def test_get_recent(self):
        """Test getting recent entries."""
        for i in range(5):
            self.db.add_entry(f"Entry {i}")
        
        entries = self.db.get_recent(limit=3)
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0]['content'], "Entry 4")  # Most recent
        self.assertEqual(entries[2]['content'], "Entry 2")
    
    def test_search_basic(self):
        """Test basic search functionality."""
        self.db.add_entry("Python programming")
        self.db.add_entry("JavaScript coding")
        self.db.add_entry("Python scripts")
        
        results = self.db.search("Python")
        self.assertEqual(len(results), 2)
    
    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        self.db.add_entry("UPPERCASE")
        self.db.add_entry("lowercase")
        self.db.add_entry("MixedCase")
        
        results = self.db.search("case")
        self.assertEqual(len(results), 3)
    
    def test_search_no_results(self):
        """Test search with no matches."""
        self.db.add_entry("Hello world")
        
        results = self.db.search("foobar")
        self.assertEqual(len(results), 0)
    
    def test_search_regex(self):
        """Test search with regex pattern."""
        self.db.add_entry("function hello()")
        self.db.add_entry("const hello = 1")
        self.db.add_entry("print hello")
        
        # Search for function calls
        results = self.db.search(r"hello\(\)")
        self.assertEqual(len(results), 1)
        self.assertIn("function", results[0]['content'])
    
    def test_delete_entry(self):
        """Test deleting entries."""
        self.db.add_entry("To be deleted")
        entry = self.db.get_entry(1)
        entry_id = entry['id']
        
        result = self.db.delete_entry(entry_id)
        self.assertTrue(result)
        
        # Should be gone
        entries = self.db.get_recent(limit=10)
        self.assertEqual(len(entries), 0)
    
    def test_clear_history(self):
        """Test clearing all history."""
        for i in range(10):
            self.db.add_entry(f"Entry {i}")
        
        count = self.db.clear_history(keep_pinned=False)
        self.assertEqual(count, 10)
        
        entries = self.db.get_recent(limit=100)
        self.assertEqual(len(entries), 0)
    
    def test_clear_history_keep_pinned(self):
        """Test clearing history but keeping pinned entries."""
        self.db.add_entry("Regular entry 1")
        self.db.add_entry("Pinned entry")
        self.db.add_entry("Regular entry 2")
        
        # Pin the middle entry
        self.db.pin_entry(2)
        
        count = self.db.clear_history(keep_pinned=True)
        self.assertEqual(count, 2)  # Should delete 2 unpinned
        
        entries = self.db.get_recent(limit=10)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['content'], "Pinned entry")
    
    def test_pin_entry(self):
        """Test pinning an entry."""
        self.db.add_entry("Important note")
        
        result = self.db.pin_entry(1)
        self.assertTrue(result)
        
        entry = self.db.get_entry(1)
        self.assertEqual(entry['pinned'], 1)
    
    def test_unpin_entry(self):
        """Test unpinning an entry."""
        self.db.add_entry("Was important")
        self.db.pin_entry(1)
        
        result = self.db.unpin_entry(1)
        self.assertTrue(result)
        
        entry = self.db.get_entry(1)
        self.assertEqual(entry['pinned'], 0)
    
    def test_get_stats(self):
        """Test statistics generation."""
        self.db.add_entry("Hello world")  # 11 chars, 2 words
        self.db.add_entry("Test")  # 4 chars, 1 word
        
        stats = self.db.get_stats()
        
        self.assertEqual(stats['total_entries'], 2)
        self.assertEqual(stats['pinned_entries'], 0)
        self.assertEqual(stats['total_characters'], 15)
        self.assertEqual(stats['total_words'], 3)
        self.assertIn('database_path', stats)
    
    def test_export_json(self):
        """Test JSON export."""
        self.db.add_entry("Export test 1")
        self.db.add_entry("Export test 2")
        
        exported = self.db.export_history(format='json')
        data = json.loads(exported)
        
        self.assertEqual(len(data), 2)
        self.assertTrue(any('Export test 1' in e['content'] for e in data))
    
    def test_export_txt(self):
        """Test plain text export."""
        self.db.add_entry("Plain text export")
        
        exported = self.db.export_history(format='txt')
        
        self.assertIn("Plain text export", exported)
        self.assertIn("Entry 1", exported)
    
    def test_import_json(self):
        """Test JSON import."""
        import_data = json.dumps([
            {'content': 'Imported entry 1'},
            {'content': 'Imported entry 2'},
            {'content': 'Imported entry 3'}
        ])
        
        count = self.db.import_history(import_data, format='json')
        self.assertEqual(count, 3)
        
        entries = self.db.get_recent(limit=10)
        self.assertEqual(len(entries), 3)
    
    def test_history_pruning(self):
        """Test that old entries are pruned."""
        # Add more than default limit
        for i in range(150):
            # Direct insert to bypass duplicate detection
            cursor = self.db.conn.cursor()
            cursor.execute("""
                INSERT INTO clipboard_history 
                (content, content_hash, timestamp, source, char_count, word_count)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (f"Entry {i}", str(hash(f"Entry {i}")), 
                  datetime.now().isoformat(), "test", len(f"Entry {i}"), 2))
        self.db.conn.commit()
        self.db._prune_history(max_entries=100)
        
        entries = self.db.get_recent(limit=200)
        self.assertLessEqual(len(entries), 100)
    
    def test_char_and_word_count(self):
        """Test character and word counting."""
        self.db.add_entry("One two three four five")  # 5 words, 23 chars
        
        entry = self.db.get_entry(1)
        self.assertEqual(entry['word_count'], 5)
        self.assertEqual(entry['char_count'], 23)


class TestClipboardAccess(unittest.TestCase):
    """Test clipboard access functionality."""
    
    def setUp(self):
        """Initialize clipboard access."""
        self.clipboard = ClipboardAccess()
    
    def test_clipboard_initialization(self):
        """Test clipboard access initializes correctly."""
        self.assertIsNotNone(self.clipboard)
        self.assertIn(self.clipboard.system, ['Windows', 'Linux', 'Darwin'])
    
    def test_get_clipboard_returns_string_or_none(self):
        """Test that get_clipboard returns string or None."""
        result = self.clipboard.get_clipboard()
        self.assertTrue(result is None or isinstance(result, str))
    
    def test_set_clipboard_returns_bool(self):
        """Test that set_clipboard returns boolean."""
        result = self.clipboard.set_clipboard("Test content")
        self.assertIsInstance(result, bool)
    
    def test_clipboard_roundtrip(self):
        """Test setting and getting clipboard content."""
        test_content = f"ClipStack test content {datetime.now().isoformat()}"
        
        # Set clipboard
        set_result = self.clipboard.set_clipboard(test_content)
        
        if set_result:
            # Get clipboard
            get_result = self.clipboard.get_clipboard()
            # Content should match (allowing for potential trailing whitespace)
            self.assertTrue(
                get_result is not None and test_content in get_result,
                f"Clipboard roundtrip failed. Expected '{test_content}', got '{get_result}'"
            )


class TestClipStack(unittest.TestCase):
    """Test main ClipStack class."""
    
    def setUp(self):
        """Create ClipStack instance with temp database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_clipstack.db"
        self.cs = ClipStack(self.db_path)
    
    def tearDown(self):
        """Clean up."""
        self.cs.close()
        if self.db_path.exists():
            self.db_path.unlink()
        if Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test ClipStack initializes correctly."""
        self.assertIsNotNone(self.cs)
        self.assertIsNotNone(self.cs.db)
        self.assertIsNotNone(self.cs.clipboard)
    
    def test_add_and_get(self):
        """Test adding and getting content."""
        self.cs.add("Test content")
        
        content = self.cs.get(1)
        self.assertEqual(content, "Test content")
    
    def test_add_returns_id(self):
        """Test that add returns entry ID."""
        entry_id = self.cs.add("New entry")
        self.assertIsInstance(entry_id, int)
        self.assertGreater(entry_id, 0)
    
    def test_get_entry_with_metadata(self):
        """Test getting entry with full metadata."""
        self.cs.add("With metadata")
        
        entry = self.cs.get_entry(1)
        
        self.assertIn('content', entry)
        self.assertIn('timestamp', entry)
        self.assertIn('char_count', entry)
        self.assertIn('word_count', entry)
        self.assertIn('pinned', entry)
    
    def test_list(self):
        """Test listing entries."""
        self.cs.add("Entry 1")
        self.cs.add("Entry 2")
        self.cs.add("Entry 3")
        
        entries = self.cs.list(limit=10)
        self.assertEqual(len(entries), 3)
    
    def test_search(self):
        """Test searching entries."""
        self.cs.add("Python code")
        self.cs.add("JavaScript code")
        self.cs.add("Python script")
        
        results = self.cs.search("Python")
        self.assertEqual(len(results), 2)
    
    def test_delete(self):
        """Test deleting entries."""
        self.cs.add("To delete")
        
        result = self.cs.delete(1)
        self.assertTrue(result)
        
        content = self.cs.get(1)
        self.assertIsNone(content)
    
    def test_clear(self):
        """Test clearing history."""
        self.cs.add("Entry 1")
        self.cs.add("Entry 2")
        
        count = self.cs.clear(keep_pinned=False)
        self.assertEqual(count, 2)
        
        entries = self.cs.list(limit=10)
        self.assertEqual(len(entries), 0)
    
    def test_pin_and_unpin(self):
        """Test pinning and unpinning."""
        self.cs.add("Pin me")
        
        result = self.cs.pin(1)
        self.assertTrue(result)
        
        entry = self.cs.get_entry(1)
        self.assertEqual(entry['pinned'], 1)
        
        result = self.cs.unpin(1)
        self.assertTrue(result)
        
        entry = self.cs.get_entry(1)
        self.assertEqual(entry['pinned'], 0)
    
    def test_stats(self):
        """Test statistics."""
        self.cs.add("Hello world")
        self.cs.add("Test")
        
        stats = self.cs.stats()
        
        self.assertEqual(stats['total_entries'], 2)
        self.assertIn('database_path', stats)
    
    def test_export_and_import(self):
        """Test export and import roundtrip."""
        self.cs.add("Export 1")
        self.cs.add("Export 2")
        
        # Export
        exported = self.cs.export(format='json')
        
        # Clear
        self.cs.clear(keep_pinned=False)
        
        # Import
        count = self.cs.import_history(exported, format='json')
        self.assertEqual(count, 2)
        
        # Verify
        entries = self.cs.list(limit=10)
        self.assertEqual(len(entries), 2)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_truncate_text_short(self):
        """Test truncation with short text."""
        result = truncate_text("Short text", max_length=80)
        self.assertEqual(result, "Short text")
    
    def test_truncate_text_long(self):
        """Test truncation with long text."""
        long_text = "A" * 100
        result = truncate_text(long_text, max_length=20)
        
        self.assertEqual(len(result), 20)
        self.assertTrue(result.endswith("..."))
    
    def test_truncate_text_newlines(self):
        """Test that newlines are replaced."""
        text = "Line 1\nLine 2\nLine 3"
        result = truncate_text(text, max_length=80)
        
        self.assertNotIn("\n", result)
        self.assertIn("[NL]", result)
    
    def test_format_timestamp_today(self):
        """Test formatting today's timestamp."""
        now = datetime.now()
        result = format_timestamp(now.isoformat())
        
        self.assertIn("Today", result)
    
    def test_format_timestamp_yesterday(self):
        """Test formatting yesterday's timestamp."""
        yesterday = datetime.now() - timedelta(days=1)
        result = format_timestamp(yesterday.isoformat())
        
        self.assertIn("Yesterday", result)
    
    def test_format_timestamp_old(self):
        """Test formatting old timestamp."""
        old_date = datetime(2020, 6, 15, 12, 30, 0)
        result = format_timestamp(old_date.isoformat())
        
        self.assertIn("2020", result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Create ClipStack instance with temp database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_clipstack.db"
        self.cs = ClipStack(self.db_path)
    
    def tearDown(self):
        """Clean up."""
        self.cs.close()
        if self.db_path.exists():
            self.db_path.unlink()
        if Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_database_operations(self):
        """Test operations on empty database."""
        # Get from empty
        content = self.cs.get(1)
        self.assertIsNone(content)
        
        # List from empty
        entries = self.cs.list(limit=10)
        self.assertEqual(len(entries), 0)
        
        # Search from empty
        results = self.cs.search("anything")
        self.assertEqual(len(results), 0)
        
        # Stats from empty
        stats = self.cs.stats()
        self.assertEqual(stats['total_entries'], 0)
    
    def test_special_characters(self):
        """Test handling special characters."""
        special = "Special chars: @#$%^&*()[]{}|\\;':\"<>,./?"
        self.cs.add(special)
        
        content = self.cs.get(1)
        self.assertEqual(content, special)
    
    def test_unicode_content(self):
        """Test handling unicode content."""
        unicode_content = "Unicode: \u2603 \u2764 \u263A \u00e9\u00e8\u00ea"
        self.cs.add(unicode_content)
        
        content = self.cs.get(1)
        self.assertEqual(content, unicode_content)
    
    def test_multiline_content(self):
        """Test handling multiline content."""
        multiline = "Line 1\nLine 2\nLine 3\n\nLine 5"
        self.cs.add(multiline)
        
        content = self.cs.get(1)
        self.assertEqual(content, multiline)
    
    def test_very_long_content(self):
        """Test handling very long content."""
        long_content = "X" * 100000  # 100KB
        self.cs.add(long_content)
        
        content = self.cs.get(1)
        self.assertEqual(content, long_content)
        self.assertEqual(len(content), 100000)
    
    def test_whitespace_only(self):
        """Test handling whitespace-only content."""
        # Should be rejected
        entry_id = self.cs.add("   ")
        self.assertEqual(entry_id, -1)
        
        entry_id = self.cs.add("\n\n\n")
        self.assertEqual(entry_id, -1)
    
    def test_delete_nonexistent(self):
        """Test deleting nonexistent entry."""
        result = self.cs.delete(999)
        self.assertFalse(result)
    
    def test_pin_nonexistent(self):
        """Test pinning nonexistent entry."""
        result = self.cs.pin(999)
        self.assertFalse(result)
    
    def test_copy_nonexistent(self):
        """Test copying nonexistent entry."""
        result = self.cs.copy(999)
        self.assertFalse(result)


class TestCLISimulation(unittest.TestCase):
    """Test CLI command simulation."""
    
    def setUp(self):
        """Create ClipStack instance with temp database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_clipstack.db"
        self.cs = ClipStack(self.db_path)
    
    def tearDown(self):
        """Clean up."""
        self.cs.close()
        if self.db_path.exists():
            self.db_path.unlink()
        if Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_workflow_add_list_get(self):
        """Test typical workflow: add, list, get."""
        # Add several entries
        self.cs.add("First copy")
        self.cs.add("Second copy")
        self.cs.add("Third copy")
        
        # List should show all 3
        entries = self.cs.list(limit=10)
        self.assertEqual(len(entries), 3)
        
        # Get most recent
        content = self.cs.get(1)
        self.assertEqual(content, "Third copy")
        
        # Get oldest
        content = self.cs.get(3)
        self.assertEqual(content, "First copy")
    
    def test_workflow_search_copy(self):
        """Test search and copy workflow."""
        self.cs.add("def hello_world():")
        self.cs.add("console.log('hi')")
        self.cs.add("def goodbye_world():")
        
        # Search for python functions
        results = self.cs.search("def")
        self.assertEqual(len(results), 2)
        
        # Verify they're the python entries
        contents = [r['content'] for r in results]
        self.assertTrue(all('def' in c for c in contents))
    
    def test_workflow_pin_clear_preserve(self):
        """Test pinning to preserve during clear."""
        self.cs.add("Temporary 1")
        self.cs.add("IMPORTANT - Keep this!")
        self.cs.add("Temporary 2")
        
        # Pin the important entry (position 2)
        self.cs.pin(2)
        
        # Clear (keeping pinned)
        self.cs.clear(keep_pinned=True)
        
        # Only pinned entry should remain
        entries = self.cs.list(limit=10)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['content'], "IMPORTANT - Keep this!")
    
    def test_workflow_export_import_backup(self):
        """Test backup workflow with export/import."""
        # Create some history
        self.cs.add("Important data 1")
        self.cs.add("Important data 2")
        
        # Export as backup
        backup = self.cs.export(format='json')
        
        # Clear everything
        self.cs.clear(keep_pinned=False)
        
        # Verify empty
        entries = self.cs.list(limit=10)
        self.assertEqual(len(entries), 0)
        
        # Restore from backup
        count = self.cs.import_history(backup, format='json')
        self.assertEqual(count, 2)
        
        # Verify restored
        entries = self.cs.list(limit=10)
        self.assertEqual(len(entries), 2)


# ==============================================================================
# TEST RUNNER
# ==============================================================================

def run_tests():
    """Run all tests with nice output."""
    print("=" * 70)
    print("TESTING: ClipStack v1.0")
    print("Clipboard History Manager for Power Users")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestClipStackDB))
    suite.addTests(loader.loadTestsFromTestCase(TestClipboardAccess))
    suite.addTests(loader.loadTestsFromTestCase(TestClipStack))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestCLISimulation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"RESULTS: {result.testsRun} tests")
    print(f"[OK] Passed: {passed}")
    if result.failures:
        print(f"[X] Failed: {len(result.failures)}")
    if result.errors:
        print(f"[X] Errors: {len(result.errors)}")
    
    pass_rate = (passed / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Pass Rate: {pass_rate:.1f}%")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
