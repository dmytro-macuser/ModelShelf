# M3 Testing Guide

## Milestone 3: Shelf (Library Management)

This guide helps you test the Shelf functionality - the visual library management system.

## Prerequisites

- Completed M1 & M2 (have at least one downloaded model)
- Python 3.11+
- Windows 10/11 or Linux/Mac

## Setup

```bash
git checkout feature/m3-shelf
pip install -r requirements.txt
python main.py
```

## Test Cases

### Test 1: Empty Shelf Display
**Objective**: Verify empty state shows correctly

**Prerequisites**: Delete or move all models from `~/ModelShelf/models/`

1. Launch app
2. Click "📚 Shelf" tab
3. **Expected**: Empty bookshelf illustration with 3 wooden shelves
4. **Expected**: Message "📚 Your shelf is empty"
5. **Expected**: Hint to download from Discover

**✅ Pass criteria**: Empty state looks good and is informative

---

### Test 2: Library Scanning
**Objective**: Verify library scan finds downloaded models

**Prerequisites**: Have at least 1 completed download in `~/ModelShelf/models/`

1. Go to Shelf tab
2. **Expected**: "Scanning library..." briefly appears
3. **Expected**: Books appear on shelves
4. **Expected**: Stats show "X models" and total size
5. Click "⟳ Refresh"
6. **Expected**: Re-scans and updates

**✅ Pass criteria**: Models appear as colorful book spines

---

### Test 3: Book Spine Visual
**Objective**: Verify book appearance

1. Look at a book on the shelf
2. **Expected**: Vertical text showing model name
3. **Expected**: Each book has a different color
4. **Expected**: Small green badge at bottom showing GGUF count
5. Hover over a book
6. **Expected**: Book scales up slightly (1.05x)
7. **Expected**: Cursor changes to pointer

**✅ Pass criteria**: Books look attractive and responsive

---

### Test 4: Shelf Layout
**Objective**: Verify multiple shelves render correctly

**Prerequisites**: Have 6+ models downloaded

1. Go to Shelf tab
2. **Expected**: Books grouped into rows of 5
3. **Expected**: Wooden shelf board below each row
4. **Expected**: Shadow under each shelf
5. **Expected**: Can scroll if many models

**✅ Pass criteria**: Looks like a real bookshelf

---

### Test 5: Model Details Dialog
**Objective**: Verify clicking a book shows details

1. Click any book spine
2. **Expected**: Dialog opens with model name as title
3. **Expected**: Shows:
   - File count
   - GGUF file count
   - Total size
   - Path on disk
4. **Expected**: "Open Folder" and "Delete" buttons visible

**✅ Pass criteria**: Details accurate and dialog usable

---

### Test 6: Open Folder
**Objective**: Verify folder opening works

1. Click a book → Details dialog opens
2. Click "Open Folder"
3. **Expected**: File explorer opens to model folder
4. **Expected**: Folder contains downloaded files

**Platform notes**:
- Windows: Opens in Explorer
- Mac: Opens in Finder
- Linux: Opens in default file manager

**✅ Pass criteria**: Correct folder opens

---

### Test 7: Delete Model
**Objective**: Verify deletion works

**Warning**: This deletes real files. Use a test model.

1. Click a book → Details dialog
2. Click "Delete" button
3. **Expected**: Confirmation dialog appears
4. **Expected**: Warning message about permanent deletion
5. Click "Cancel"
6. **Expected**: Dialog closes, model still there
7. Click "Delete" again → "Delete" in confirmation
8. **Expected**: Both dialogs close
9. **Expected**: Book disappears from shelf
10. **Expected**: Stats update (model count decreases)
11. Check `~/ModelShelf/models/`
12. **Expected**: Model folder deleted from disk

**✅ Pass criteria**: Deletion works, confirmation prevents accidents

---

### Test 8: Persistence
**Objective**: Verify index persists across restarts

1. Note current model count on Shelf
2. Close app
3. Relaunch
4. Go to Shelf tab
5. **Expected**: Same models appear quickly (from cache)
6. **Expected**: Scan completes fast

**✅ Pass criteria**: No need to re-scan entire disk each time

---

### Test 9: Download Integration
**Objective**: Verify new downloads appear on Shelf

1. Go to Discover
2. Download a new model (small file)
3. Wait for download to complete
4. Go to Shelf
5. Click "⟳ Refresh"
6. **Expected**: New model appears as a book

**✅ Pass criteria**: Shelf updates with new content

---

### Test 10: Many Models (Stress Test)
**Objective**: Test performance with many models

**Prerequisites**: Have 20+ models (or manually create dummy folders)

1. Go to Shelf
2. **Expected**: All books render
3. **Expected**: Multiple shelves created
4. **Expected**: Scrolling is smooth
5. **Expected**: Hover effects still responsive

**✅ Pass criteria**: Performance acceptable with large libraries

---

## Visual Expectations

### Book Colors
- Each book gets a color from a palette based on model ID hash
- Colors: Blue, Red, Green, Orange, Purple, Teal, Dark Gray, etc.
- Same model = same color every time

### Shelf Styling
- Wooden brown shelf boards (#8b7355)
- Subtle shadows underneath
- Books have 3D-ish lighting (lighter left edge, darker right)

### GGUF Badge
- Small green circle at bottom of spine
- Shows count of GGUF files
- White border

## Common Issues

### Issue: "Shelf is empty but I have downloads"
**Solution**: Check if files are in `~/ModelShelf/models/`. M2 saves to this location. If folder name doesn't match pattern, indexer might skip it.

### Issue: "Books have no text"
**Solution**: Model name might be too short or font rendering issue. Check console logs.

### Issue: "Shelf doesn't refresh"
**Solution**: Force refresh with ⟳ button. Check logs for scan errors.

### Issue: "Delete doesn't work"
**Solution**: File permission issue. Check if you have write access to library folder.

## Reporting Bugs

Open issues at: [github.com/dmytro-macuser/ModelShelf/issues](https://github.com/dmytro-macuser/ModelShelf/issues)

Include:
- Test case number
- Expected vs actual behavior
- Screenshots (especially for visual issues)
- Log file (`~/.modelshelf/app.log`)
