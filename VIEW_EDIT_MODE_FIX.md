# View vs Edit Mode Styling Fix

## Problem Summary

### Issue 1: View Mode Had Visible Border/Container
The QTextBrowser in view mode looked like a text box with borders and background, unlike the clean label-style display for "Current Situation" and "Next Objective".

### Issue 2: Edit Mode Couldn't Edit Markdown
Using QTextBrowser in edit mode prevented users from seeing and editing the raw markdown (asterisks, hashtags, etc.), making manual edits impossible.

---

## Solution

### Implemented Two Separate Widgets

#### 1. **View Mode** - `view_guide_text` (QTextBrowser)
- **Purpose:** Display beautifully rendered markdown
- **Styling:** Seamless, no borders, transparent background
- **Behavior:** Read-only, clickable links
- **CSS:** `border: none; background-color: transparent; padding: 0px;`

#### 2. **Edit Mode** - Two widgets:
   
   **a) `guide_output_edit` (QTextEdit)**
   - Shows raw markdown text with all formatting characters
   - Fully editable
   - Has border and background (like other input fields)
   - Visible during edit mode
   
   **b) `guide_output_view` (QTextBrowser)**
   - Shows rendered markdown preview
   - Hidden during edit mode (kept for potential future use)

---

## Technical Changes

### Widget Creation
```python
# View mode in details panel - seamless display
self.view_guide_text = QTextBrowser()
self.view_guide_text.setObjectName("viewGuideText")  # For CSS targeting
self.view_guide_text.setFrameShape(QFrame.Shape.NoFrame)
# CSS: border: none; background: transparent;

# Edit mode - raw markdown editor
self.guide_output_edit = QTextEdit()
self.guide_output_edit.textChanged.connect(self._on_guide_output_changed)
# CSS: normal text edit styling with borders

# Edit mode - rendered preview (currently hidden)
self.guide_output_view = QTextBrowser()
self.guide_output_view.setObjectName("guideOutputView")
# CSS: normal text browser styling with borders
```

### CSS Styling
```python
# View mode: Seamless like a label
QTextBrowser#viewGuideText {{ 
    border: none; 
    background-color: transparent; 
    padding: 0px; 
}}

# Edit mode view (if shown): Normal box
QTextBrowser#guideOutputView {{ 
    border: 2px solid {border_color}; 
    border-radius: 6px; 
    padding: 10px; 
    background-color: {bg_input}; 
}}
```

### Visibility Logic
```python
def _set_edit_elements_visible(self, visible):
    # ... other edit elements ...
    
    # In edit mode: show editable text, hide rendered view
    self.guide_output_edit.setVisible(visible)
    self.guide_output_view.setVisible(False)  # Always hidden for now
```

### Text Setting Logic
```python
def _set_guide_output_text(self, text):
    """Update guide output - raw markdown in edit mode, rendered HTML in view mode."""
    # Set raw markdown in edit mode widget
    self.guide_output_edit.setPlainText(text)
    
    # Convert markdown to HTML for view mode widget
    html_content = markdown.markdown(
        text,
        extensions=['extra', 'nl2br', 'sane_lists']
    )
    self.guide_output_view.setHtml(html_content)
    
    # Store raw markdown
    if self.current_game and self.current_game in self.games:
        self.games[self.current_game]["guide"] = text
        self.data_manager.save_games(self.games)
```

### Save Handler
```python
def _on_guide_output_changed(self):
    """Save changes when user edits the raw markdown in edit mode."""
    if not self.current_game or self.current_game not in self.games:
        return
    
    text = self.guide_output_edit.toPlainText()
    self.games[self.current_game]["guide"] = text
    self.data_manager.save_games(self.games)
```

---

## User Experience

### View Mode (Reading) 👁️
```
Current Situation
Just completed the Deku Tree dungeon.

Next Objective  
Head to Hyrule Castle to meet Princess Zelda.

Guide Hint
[Beautiful rendered markdown - seamless, no box]
**Essential Progression: Getting the Goron's Bracelet**

The primary reason you can't pick up Bomb Flowers is...
```
✅ Clean, professional look
✅ No visual separation from other labels
✅ Links are clickable
✅ Markdown renders beautifully

### Edit Mode (Editing) ✏️
```
[Input fields with borders]

Guide Hint:
┌─────────────────────────────────────┐
│ **Essential Progression: Getting   │
│ the Goron's Bracelet**             │
│                                     │
│ The primary reason you can't pick  │
│ up Bomb Flowers is...              │
└─────────────────────────────────────┘
```
✅ Can see and edit asterisks, hashtags
✅ Clear text box indicates it's editable
✅ Auto-saves changes
✅ Consistent with other input fields

---

## Benefits

### 1. **Seamless View Mode**
- Looks exactly like the "Current Situation" and "Next Objective" sections
- No visual clutter
- Professional appearance
- Markdown renders beautifully

### 2. **Functional Edit Mode**
- Users can see raw markdown
- Can manually edit formatting
- Can fix AI mistakes
- Can adjust styling as needed

### 3. **Best of Both Worlds**
- Beautiful rendering when viewing
- Full control when editing
- Automatic saving
- No confusion about which mode you're in

---

## Files Modified

### `src/app.py`
1. Added `guide_output_edit` (QTextEdit) for editing
2. Added `guide_output_view` (QTextBrowser) for preview (hidden)
3. Kept `view_guide_text` (QTextBrowser) seamless in view mode
4. Updated `_set_guide_output_text()` to update both widgets
5. Added `_on_guide_output_changed()` to save edits
6. Updated `_set_edit_elements_visible()` to show correct widget
7. Updated CSS for `#viewGuideText` to be transparent/borderless
8. Updated CSS for `#guideOutputView` to have normal styling

---

## Testing

### View Mode Test:
1. Select a game
2. Click "Edit" then "Done" (to exit edit mode)
3. **Expected:** Guide hint looks seamless, no border/box
4. **Expected:** Text flows naturally like labels above it
5. **Expected:** Links are clickable if present

### Edit Mode Test:
1. Select a game
2. Click "Edit"
3. **Expected:** Guide hint shows in editable text box with border
4. **Expected:** Can see raw markdown (`**bold**`, `# headers`, etc.)
5. **Expected:** Can edit the text
6. **Expected:** Changes save automatically
7. Generate new guide → raw markdown appears in edit box

---

## Future Enhancements

### Possible additions:
1. **Split View** - Show edit and preview side-by-side
2. **Preview Button** - Toggle between raw and rendered in edit mode
3. **Markdown Toolbar** - Buttons for bold, italic, headers, etc.
4. **Syntax Highlighting** - Color markdown syntax in edit mode
5. **Template Insertion** - Quick insert markdown structures

---

## Comparison

### Before Fix:
```
View Mode: [Bordered box with markdown asterisks]
Edit Mode: [Can't edit, QTextBrowser renders everything]
```

### After Fix:
```
View Mode: Seamless rendered markdown (no border)
Edit Mode: Editable raw markdown with asterisks (with border)
```

Perfect balance between beauty and functionality! 🎨✏️
