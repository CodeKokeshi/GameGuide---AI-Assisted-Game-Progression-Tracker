# Output Behavior Styles

This document describes the different output styles available in NextStep.

## Available Styles

### 1. Walkthrough Style (Next Step) - DEFAULT
The original behavior that provides the immediate, actionable next step.

**Best for:** Quick guidance when you know what you're doing but forgot the next step.

**Output format:**
- Single, concise next action
- Specific locations, items, or actions
- 2-3 sentences max

---

### 2. Strategic Planning Style
Provides comprehensive breakdown of goals and action plans.

**Best for:** Returning to a game after a long break and need to understand the big picture.

**Output format:**
```
Understanding Your Situation/Quest:
* Final Goal: [Ultimate objective]
* Immediate Goal: [Current focus]

Your Recommended Action Plan:
Step 1: The Foundation
  - Initial tasks to reorient yourself
  
Step 2: Get Stronger
  - Ways to prepare and level up
  
Step 3: Tackle Your First Challenge
  - First major objective to complete
  
Step 4: Long-term Preparation
  - Materials, upgrades, etc. to gather

TL;DR - Your Simple To-Do List:
• [Immediate task 1]
• [Immediate task 2]
• [Immediate task 3]
```

---

### 3. Contextual Analysis Style
Analyzes WHERE you are in the game's progression rather than telling you what to do next.

**Best for:** Understanding context when you're confused about a quest or story element.

**Output format:**
- Identifies the current section/quest/chapter
- Explains what happened before
- Describes what comes after
- Clarifies story context and requirements

**Example:**
"According to online sources, giving the mask to the guard happens after you return from the Happy Mask Shop. The guard will give it to his kid. Now you'll be tasked to return the payment - you can do this now or later. If you return to Hyrule, a new mask is unlocked..."

---

### 4. Tips & Tricks Style
Provides exploits, shortcuts, secrets, and advantages.

**Best for:** Players who want to optimize their gameplay or find hidden content.

**Output format:**
- In-game cheats or shortcuts
- Exploits or mechanics to leverage
- Hidden items or secrets nearby
- Puzzle solutions or passwords
- Time-saving techniques

---

### 5. Custom Instructions
Allows you to specify exactly how you want the AI to respond.

**Best for:** Specific needs not covered by the preset styles.

**Usage:** Select this option and enter your custom instructions in the text field that appears.

---

## Data Storage

### New Game Data Structure
```json
{
  "game_title": {
    "situation": "Current situation text",
    "objective": "Next objective text",
    "behavior_style": "Walkthrough Style (Next Step)",
    "custom_behavior": "",
    "guide": "Generated guide text"
  }
}
```

### Backward Compatibility
Old games with the `"behavior"` field are automatically migrated:
- If `behavior` exists, it's treated as "Custom Instructions"
- The old `behavior` text becomes `custom_behavior`
- `behavior_style` is set to "Custom Instructions"

---

## Implementation Details

### UI Changes
1. **Replaced:** `QTextEdit` for behavior input
2. **Added:** `QComboBox` for style selection
3. **Added:** `QTextEdit` for custom instructions (shown only when "Custom Instructions" is selected)

### Files Modified
- `src/app.py`: Main UI and behavior logic
- Game data structure updated for new fields

### Key Methods
- `_get_behavior_instruction(behavior_style)`: Converts style selection to AI prompt
- `_on_behavior_style_changed(index)`: Handles dropdown changes
- `_update_custom_behavior_visibility()`: Shows/hides custom text field
- `_on_custom_behavior_changed()`: Saves custom instructions
