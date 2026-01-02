# M2 Testing Guide

## Milestone 2: Download Manager

This guide helps you test the Download Manager functionality implemented in M2.

## Prerequisites

- Python 3.11 or higher installed
- Internet connection
- Windows 10/11 (or Linux/Mac for development testing)

## Setup

```bash
# Clone and install
git clone https://github.com/dmytro-macuser/ModelShelf.git
cd ModelShelf
git checkout feature/m2-download-manager
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

## Test Cases

### Test 1: Add to Queue
**Objective**: Verify adding files to queue works

1. Go to "Discover" tab
2. Search for a small model (e.g. "tinyllama")
3. Open model details
4. Find a small file (e.g. `config.json` or a small GGUF)
5. Click "Download"
6. **Expected**: Button text changes to "Queued" or "Downloading"
7. Go to "Downloads" tab
8. **Expected**: File appears in the list

**✅ Pass criteria**: File appears in Downloads list with correct name

---

### Test 2: Progress Tracking
**Objective**: Verify progress bars update

1. Start downloading a larger file (e.g. >100MB)
2. Watch the "Downloads" tab
3. **Expected**: Progress bar moves
4. **Expected**: Percentage increases
5. **Expected**: Speed (e.g., "5.2 MB/s") updates
6. **Expected**: ETA (e.g., "2m 30s") updates

**✅ Pass criteria**: Real-time updates visible

---

### Test 3: Pause and Resume
**Objective**: Verify pause/resume functionality

1. Start a download
2. Click "Pause"
3. **Expected**: Status changes to "Paused", speed becomes 0
4. Wait 5 seconds
5. Click "Resume"
6. **Expected**: Status changes to "Downloading", speed increases
7. **Expected**: Download continues from where it left off (not 0%)

**✅ Pass criteria**: Can pause and resume without restarting

---

### Test 4: Cancellation
**Objective**: Verify cancellation works

1. Start a download
2. Click "Cancel"
3. **Expected**: Status changes to "Cancelled"
4. **Expected**: File removed from active queue
5. Click "Retry"
6. **Expected**: Download restarts

**✅ Pass criteria**: Cancel stops download immediately

---

### Test 5: Concurrent Downloads
**Objective**: Verify multiple downloads run in parallel

1. Find a model with multiple files
2. Queue 3-4 files
3. **Expected**: Up to 3 start downloading immediately (default concurrency)
4. **Expected**: The 4th stays "Queued" until one finishes
5. **Expected**: Total bandwidth shared between active downloads

**✅ Pass criteria**: Max concurrency (default 3) respected

---

### Test 6: Persistence (Resume on Restart)
**Objective**: Verify downloads resume after app restart

1. Start a large download
2. Let it reach ~20%
3. Close the application window
4. Relaunch `python main.py`
5. Go to "Downloads" tab
6. **Expected**: Item is still there
7. Click "Resume" (or it might auto-resume if implemented)
8. **Expected**: Continues from ~20%, not 0%

**✅ Pass criteria**: Partial downloads are preserved

---

### Test 7: File Integrity (Manual)
**Objective**: Verify file is actually saved

1. Download a small file completely
2. Navigate to `~/ModelShelf/models/` (default folder)
3. **Expected**: Folder exists for the model
4. **Expected**: File exists with correct size

**✅ Pass criteria**: File exists on disk

## Common Issues

### Issue: "HTTP Error 403/401"
**Solution**: Some models are gated. M2 doesn't support auth tokens yet (coming in M4). Test with public models like `TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF`.

### Issue: "Disk Full"
**Solution**: Check available space. M2 doesn't pre-check disk space yet (planned for M3).

### Issue: Download fails immediately
**Solution**: Check internet connection. Retry.

## Reporting Bugs

Open issues at: [github.com/dmytro-macuser/ModelShelf/issues](https://github.com/dmytro-macuser/ModelShelf/issues)
