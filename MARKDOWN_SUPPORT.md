# Markdown Rendering Support

## Overview

NextStep now supports beautiful **Markdown rendering** for all guide hints! No more ugly asterisks and formatting characters - the AI's output is now displayed with proper formatting.

## What's Changed?

### Before (Plain Text) ❌
```
**Essential Progression: Getting the Goron's Bracelet**

The primary reason you can't pick up Bomb Flowers is that you don't have the **Goron's Bracelet**.

1.  **Enter Darunia's Chamber:** In Goron City...
2.  **Soothe Darunia:** Inside, you'll find...
```

### After (Rendered Markdown) ✅
**Essential Progression: Getting the Goron's Bracelet**

The primary reason you can't pick up Bomb Flowers is that you don't have the **Goron's Bracelet**.

1.  **Enter Darunia's Chamber:** In Goron City...
2.  **Soothe Darunia:** Inside, you'll find...

---

## Supported Markdown Features

Thanks to the `markdown` library with the `extra`, `nl2br`, and `sane_lists` extensions, we support:

### ✅ Text Formatting
- **Bold text** with `**text**` or `__text__`
- *Italic text* with `*text*` or `_text_`
- ***Bold and italic*** with `***text***`
- `Inline code` with backticks
- ~~Strikethrough~~ with `~~text~~`

### ✅ Headers
```markdown
# Header 1
## Header 2
### Header 3
#### Header 4
```

### ✅ Lists
**Ordered lists:**
```markdown
1. First item
2. Second item
3. Third item
```

**Unordered lists:**
```markdown
- Item one
- Item two
- Item three

* Alternative
* Bullet style
```

**Nested lists:**
```markdown
1. Main item
   - Sub item
   - Sub item
2. Another main item
```

### ✅ Links
```markdown
[Link text](https://example.com)
```
Links automatically open in your default browser!

### ✅ Code Blocks
Single line:
```markdown
Use `code` for inline code
```

Multi-line:
````markdown
```
function example() {
    return "formatted code";
}
```
````

### ✅ Blockquotes
```markdown
> This is a quote
> It can span multiple lines
```

### ✅ Horizontal Rules
```markdown
---
***
___
```

### ✅ Line Breaks
With the `nl2br` extension, single line breaks in the source become actual line breaks in the output!

### ✅ Tables
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
```

---

## Technical Implementation

### Components Changed

#### 1. **View Mode Display** (`view_guide_text`)
- **Before:** `QLabel` (plain text only)
- **After:** `QTextBrowser` (HTML/markdown rendering)
- **Features:**
  - Renders markdown as HTML
  - Clickable links that open in browser
  - Selectable text
  - Scrollable for long content

#### 2. **Edit Mode Display** (`guide_output`)
- **Before:** `QTextEdit` (editable plain text)
- **After:** `QTextBrowser` (read-only rendered markdown)
- **Rationale:** 
  - Users shouldn't edit AI-generated content directly
  - Better to regenerate if changes are needed
  - Prevents markdown formatting corruption

#### 3. **Data Storage**
- Stored as **raw markdown text** in `game_progress.json`
- Rendered to HTML on display
- Preserves formatting for future edits

### Code Changes

**Added Import:**
```python
import markdown
from PyQt6.QtWidgets import QTextBrowser
```

**Markdown Rendering Function:**
```python
def _set_guide_output_text(self, text):
    """Update the guide output with markdown rendering."""
    html_content = markdown.markdown(
        text,
        extensions=['extra', 'nl2br', 'sane_lists']
    )
    self.guide_output.setHtml(html_content)
    
    # Store the raw markdown text
    if self.current_game and self.current_game in self.games:
        self.games[self.current_game]["guide"] = text
        self.data_manager.save_games(self.games)
```

**View Mode Rendering:**
```python
# Render guide as markdown HTML
if guide:
    guide_html = markdown.markdown(
        guide,
        extensions=['extra', 'nl2br', 'sane_lists']
    )
    self.view_guide_text.setHtml(guide_html)
```

---

## Benefits

### 🎨 Better Readability
- Proper formatting makes long guides easier to read
- Headers create clear sections
- Lists are properly indented and bulleted
- Code and commands stand out

### 🔗 Clickable Links
- Source URLs from AI responses are clickable
- Opens in default browser
- Easy to verify information

### 📱 Professional Appearance
- No more asterisks everywhere
- Clean, modern look
- Consistent with other documentation tools

### 🎯 AI-Friendly
- AI naturally outputs markdown
- No need to strip formatting
- Works with all output styles

---

## How AI Generates Markdown

The AI (Gemini, ChatGPT, Claude) naturally uses markdown formatting when providing structured responses. Our different output styles leverage this:

### Walkthrough Style
Usually simple formatting:
```markdown
Go to **Kakariko Village** and talk to **Impa**.
```

### Strategic Planning Style
Heavy use of headers and lists:
```markdown
## Final Goal
Defeat Ganon

## Action Plan
1. **Step 1:** Foundation
   - Visit Kakariko Village
   - Complete 4 shrines
2. **Step 2:** Get Stronger
   - Upgrade weapons
```

### Contextual Analysis Style
Paragraphs with emphasis:
```markdown
You're currently in the **Goron City** section, which occurs after 
completing the Deku Tree. The *Goron's Bracelet* is required to 
progress to **Dodongo's Cavern**.
```

### Tips & Tricks Style
Often uses code blocks and lists:
```markdown
**Tricks:**
- Use `Bomb Flower clipping` to skip sections
- Behind the shop is a hidden chest with **5 bombs**
```

---

## Styling

The QTextBrowser inherits the theme colors from the application:

**Dark Mode:**
- Background: Dark gray (#2d2d30)
- Text: Light gray (#e0e0e0)
- Links: Blue (#60cdff)

**Light Mode:**
- Background: White (#ffffff)
- Text: Dark gray (#202020)
- Links: Blue (#0078d4)

Both modes have rounded corners and proper borders for a polished look.

---

## Dependencies

**New dependency added:**
```bash
pip install markdown
```

**Extensions used:**
- `extra`: Tables, fenced code blocks, definition lists
- `nl2br`: Converts newlines to `<br>` tags
- `sane_lists`: Better list handling

---

## Future Enhancements

Possible future improvements:

1. **Syntax Highlighting** - Add `pygments` for code syntax highlighting
2. **Custom CSS** - More control over markdown styling
3. **Image Support** - Render inline images if AI provides them
4. **Export to HTML** - Save guides as standalone HTML files
5. **Copy as Markdown** - Copy button to get raw markdown text

---

## Troubleshooting

### If markdown isn't rendering:
1. Check that `markdown` package is installed: `.venv/Scripts/pip list`
2. Restart the application if you just installed it
3. Check console for errors

### If links aren't clickable:
- Make sure `setOpenExternalLinks(True)` is set on QTextBrowser
- Links must be in proper markdown format: `[text](url)`

### If formatting looks wrong:
- Check that the AI is actually outputting markdown
- View the raw text in `game_progress.json`
- Try regenerating the guide

---

## Testing

To see markdown rendering in action:

1. **Add a test game** (e.g., "Zelda: Ocarina of Time")
2. **Enter a situation** (e.g., "Stuck in Goron City")
3. **Select Strategic Planning Style** (produces heavy markdown)
4. **Click "See Next Step"**
5. **Observe the beautifully formatted output!**

Compare the rendered output with the raw markdown stored in `game_progress.json` to see the difference.
