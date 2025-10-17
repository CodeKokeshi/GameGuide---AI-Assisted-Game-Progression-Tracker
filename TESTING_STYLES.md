# Testing Output Styles

## Test Case: Stuck in Goron City (Ocarina of Time)

**Situation:** "I'm stuck in Goron City and idk what to do, maybe I forgot something or I need to use some songs"

### Expected Outputs by Style:

#### 1. Walkthrough Style (Next Step) ✅ WORKING
**Expected:** Direct, concise next step
**Example:**
```
Play Zelda's Lullaby in front of Darunia's chamber to open the door. 
Then play Saria's Song inside to cheer him up and receive the Goron's Bracelet.
```

#### 2. Strategic Planning Style 🔄 UPDATED
**Expected:** Structured breakdown with goals and action plan
**Example:**
```
1. FINAL GOAL: Defeat Volvagia in the Fire Temple to free the Gorons

2. IMMEDIATE GOAL: Get the Goron's Bracelet from Darunia to access Dodongo's Cavern

3. ACTION PLAN:
   - Step 1: Play Zelda's Lullaby to open Darunia's chamber
   - Step 2: Play Saria's Song to cheer up Darunia
   - Step 3: Receive Goron's Bracelet and use it to pick up Bomb Flowers
   - Step 4: Clear Dodongo's Cavern to progress

4. QUICK TO-DO:
   • Stand in front of the blocked door
   • Play Zelda's Lullaby (C-Left, C-Up, C-Right)
   • Enter and play Saria's Song for Darunia
```

#### 3. Contextual Analysis Style
**Expected:** Explanation of WHERE in the game progression
**Example:**
```
[Before] → You completed the Deku Tree and met Princess Zelda, who taught you Zelda's Lullaby. 
You then climbed Death Mountain to reach Goron City.

[Current] → You're at the quest "Dodongo's Cavern" - the second dungeon. 
Darunia, the Goron leader, won't see you yet. The door to his chamber responds to the Royal Family's song.
Once you meet him and play Saria's Song, he'll give you the Goron's Bracelet.

[After] → The Goron's Bracelet lets you pick up Bomb Flowers. 
You'll use these to blow up the boulder blocking Dodongo's Cavern entrance on the Death Mountain Trail.
```

#### 4. Tips & Tricks Style
**Expected:** Exploits, secrets, shortcuts
**Example:**
```
TIPS & TRICKS:
• Skip talking to most Gorons - only Darunia matters here
• You can actually skip getting Bombs from the Bomb Bag Shop - Bomb Flowers work too
• Secret: Behind the Goron Shop is a passageway with a chest containing bombs
• Speedrun trick: You can use Bomb Flower clipping to access certain areas early
• The rolling Goron on the bottom floor will give you a free bomb bag upgrade later
```

#### 5. Custom Instructions
**Expected:** Whatever you specify
**Example Input:** "Tell me exactly which songs to play and where"
**Example Output:** Based on your custom instructions

---

## Changes Made to Fix Strategic Style

### Problem:
The Strategic Planning Style was returning fallback text: "No reliable hint could be confirmed"

### Root Causes:
1. **Over-complicated prompt** - Too many formatting requirements
2. **Conflicting instructions** - System prompt said "concise" but behavior asked for detailed breakdown
3. **No style-aware system prompts** - All styles used the same base prompt

### Solutions Applied:

#### 1. Simplified Behavior Instructions (`src/app.py`)
```python
"Strategic Planning Style":
"""Instead of just the next step, provide a strategic breakdown:

1. FINAL GOAL: What's the ultimate objective?
2. IMMEDIATE GOAL: What should they focus on now?
3. ACTION PLAN (numbered steps):
   - Foundation/orientation tasks
   - Preparation and strengthening
   - First major challenge
   - Long-term items to collect
4. QUICK TO-DO LIST: 3-5 immediate actionable bullet points.

Search game guides and provide specific advice."""
```

#### 2. Style-Aware System Prompts (`src/ai.py`)
Each style now gets an appropriate system prompt:

- **Strategic:** "Provide comprehensive strategic guidance..."
- **Contextual:** "Analyze the player's position... Focus on explaining WHERE..."
- **Tips & Tricks:** "Specializing in tips, tricks, and optimization..."
- **Default (Walkthrough):** "Provide the IMMEDIATE next step..."

#### 3. Removed Conflicting Instructions
- Strategic style no longer has "Keep response concise (2-3 sentences)"
- Behavior instructions are now the PRIMARY directive, not secondary
- System prompts now align with the chosen style

---

## How to Test:

1. **Start the application** (should already be running)
2. **Add a test game** (e.g., "The Legend of Zelda: Ocarina of Time")
3. **Enter edit mode** and fill in:
   - **Situation:** "I'm stuck in Goron City and idk what to do, maybe I forgot something or I need to use some songs"
   - **Objective:** (leave blank or "Progress to next dungeon")
4. **Select different Output Styles** from the dropdown
5. **Click "See Next Step"** for each style
6. **Compare results** with expected outputs above

### Expected Results:
- ✅ All styles should return actual guidance (not fallback text)
- ✅ Each style should have distinct formatting/focus
- ✅ Strategic should provide structured breakdown
- ✅ Contextual should explain game progression
- ✅ Tips should provide optimization advice

---

## Troubleshooting:

### If Strategic Style Still Returns Fallback:
1. Check your API key is valid
2. Try the prompt again (sometimes API has temporary issues)
3. Check the status panel for specific error messages
4. The refined context should show what the AI researched

### If Results Are Generic:
- The AI might not be searching effectively
- Try being more specific in the situation description
- Include the game's full name
- Mention specific locations or quest names
