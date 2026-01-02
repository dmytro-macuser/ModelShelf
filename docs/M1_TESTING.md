# M1 Testing Guide

## Milestone 1: Hub Browsing

This guide helps you test the Discover functionality implemented in M1.

## Prerequisites

- Python 3.11 or higher installed
- Internet connection (for Hugging Face API)
- Windows 10/11 (or Linux/Mac for development testing)

## Setup

```bash
# Clone and install
git clone https://github.com/dmytro-macuser/ModelShelf.git
cd ModelShelf
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
# source .venv/bin/activate

pip install -r requirements.txt
```

## Launch

```bash
python main.py
```

The application should:
1. Open a window with sidebar navigation
2. Show "Discover" tab by default
3. Start loading popular models automatically

## Test Cases

### Test 1: Basic Search
**Objective**: Verify search functionality works

1. Type "llama" in the search box
2. Click "Search" or press Enter
3. **Expected**: Search indicator appears, then results load
4. **Expected**: Models with "llama" in name/description appear
5. **Expected**: Results show download/like counts and size

**✅ Pass criteria**: Results appear within 5 seconds

---

### Test 2: GGUF Filter
**Objective**: Verify GGUF filtering works

1. Search for "mistral"
2. Enable "GGUF files only" checkbox
3. **Expected**: Only models with GGUF files appear
4. **Expected**: Green "GGUF" badge visible on filtered models
5. Disable checkbox
6. **Expected**: More models appear (including non-GGUF)

**✅ Pass criteria**: GGUF filter narrows results appropriately

---

### Test 3: Sort Options
**Objective**: Verify sorting works

1. Search for "python"
2. Note the order of results
3. Change sort to "Likes"
4. **Expected**: Results reorder with most-liked first
5. Try "Recent" and "Trending"
6. **Expected**: Results change each time

**✅ Pass criteria**: Different sorts show different orderings

---

### Test 4: Model Details
**Objective**: Verify details panel loads correctly

1. Search for "TheBloke/Llama-2-7B-GGUF"
2. Click on the model in the list
3. **Expected**: Details panel slides in from right
4. **Expected**: See description, licence, download count
5. **Expected**: File list appears
6. **Expected**: GGUF files highlighted in green background
7. **Expected**: Quantisation shown (e.g., "Q4_K_M", "Q8_0")

**✅ Pass criteria**: All metadata displays correctly

---

### Test 5: File List - GGUF Priority
**Objective**: Verify GGUF files are prioritised

1. Open any model with multiple file types
2. Look at file list in details panel
3. **Expected**: GGUF files appear at top
4. **Expected**: GGUF files have green background
5. **Expected**: Non-GGUF files (config.json, etc.) at bottom

**✅ Pass criteria**: GGUF files clearly distinguished and prioritised

---

### Test 6: Pagination
**Objective**: Verify pagination works

1. Search for "llm" (broad query)
2. **Expected**: "Next" button enabled if more results exist
3. Click "Next"
4. **Expected**: Page 2 loads
5. **Expected**: "Previous" button now enabled
6. Click "Previous"
7. **Expected**: Back to page 1

**✅ Pass criteria**: Can navigate through multiple pages

---

### Test 7: Cache Performance
**Objective**: Verify caching speeds up repeat searches

1. Search for "gpt2"
2. Note the load time (should be ~2-5 seconds first time)
3. Search for something else (e.g., "bert")
4. Search for "gpt2" again
5. **Expected**: Results appear almost instantly (<500ms)
6. **Expected**: Same results as before

**✅ Pass criteria**: Cached search is noticeably faster

---

### Test 8: UI Responsiveness
**Objective**: Ensure UI doesn't freeze during operations

1. Start a search for "transformer"
2. While loading, try:
   - Moving the window
   - Clicking sidebar buttons
   - Scrolling (if any results loaded)
3. **Expected**: UI remains responsive
4. **Expected**: Can switch tabs during search
5. **Expected**: No "Not Responding" in title bar

**✅ Pass criteria**: UI never freezes

---

### Test 9: Error Handling
**Objective**: Verify graceful error handling

1. Disconnect internet
2. Try searching
3. **Expected**: Error message appears (not crash)
4. **Expected**: Previous results still visible
5. Reconnect internet
6. Search again
7. **Expected**: Works normally

**✅ Pass criteria**: No crashes, clear error messages

---

### Test 10: Empty Results
**Objective**: Handle no-result searches gracefully

1. Search for "xyzabc123notamodel"
2. **Expected**: "No results" message
3. **Expected**: No crash or blank screen
4. Search for something valid
5. **Expected**: Results load normally

**✅ Pass criteria**: Handles empty results without issues

---

## Performance Benchmarks

### Expected Performance
- **First search**: 2-5 seconds (network dependent)
- **Cached search**: <500ms
- **Model details**: 1-3 seconds first time
- **Pagination**: <1 second
- **UI interactions**: <100ms response time

### Memory Usage
- **Idle**: ~100-150 MB
- **After 10 searches**: ~200-300 MB
- **Database size**: <10 MB after moderate use

## Common Issues

### Issue: "Module not found" errors
**Solution**: 
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Search hangs indefinitely
**Solution**: 
- Check internet connection
- Check firewall settings
- Try restarting the app

### Issue: No GGUF models found
**Solution**: 
- Some models don't have GGUF files
- Try popular GGUF providers like "TheBloke"
- Search: "TheBloke GGUF"

### Issue: Details panel won't open
**Solution**: 
- Check console for errors
- Try different model
- Restart application

## Reporting Bugs

When reporting issues, include:
1. Steps to reproduce
2. Expected behaviour
3. Actual behaviour
4. Console output (if available)
5. Operating system and Python version

Open issues at: [github.com/dmytro-macuser/ModelShelf/issues](https://github.com/dmytro-macuser/ModelShelf/issues)

## M1 Acceptance Criteria

- [x] Search results show quickly
- [x] Scrolling doesn't freeze UI
- [x] GGUF files are clearly prioritised
- [x] Cached results load instantly
- [x] Model details load with file listings
- [x] Pagination works correctly
- [x] Filters affect results appropriately

## Next Steps

Once M1 testing is complete, the next milestone (M2) will add:
- Download queue
- Progress tracking
- Pause/resume functionality
- File verification

See [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) for details.
