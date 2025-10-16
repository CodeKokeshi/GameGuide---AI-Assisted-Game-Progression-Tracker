# Game Progress Tracker

A Windows 11-styled desktop application for tracking your progress in games with poor quest systems or games you haven't played in a while.

## Features

### 📚 Game Library
- Add new games to your personal library
- View all your tracked games in an organized list
- Click any game to view and edit its details

### 🎮 Game Details
For each game, you can track:
- **Current Situation**: Where you are and what you last did
- **Next Objective** (Optional): What you want to accomplish next
- **Output Behavior** (Optional): How you want the guide to respond (e.g., "Tell me how to prepare" or "Focus on earning money first")

### 🔍 Guide Hints
- Click "See Next Step" to generate a guide hint
- Guide hints appear in a dedicated output section
- Perfect for getting quick reminders without reading full walkthroughs

### 💾 Auto-Save
- All your progress is automatically saved locally
- Data persists between sessions
- Stored in `game_progress.json` (not committed to git)

## Setup

### Prerequisites
- Python 3.9 or higher
- Windows 10/11 (PyQt6 works on other platforms too)

### Installation

1. **Clone the repository**
   ```powershell
   git clone <your-repo-url>
   cd GameGuide
   ```

2. **Create and activate virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install pyqt6
   ```

## Usage

### Running the App
```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

### Adding a Game
1. Click "➕ Add New Game" in the left panel
2. Enter the game title
3. Click "Add Game"

### Tracking Progress
1. Select a game from the library
2. Fill in your current situation (required)
3. Optionally add your next objective
4. Optionally specify how the guide should behave
5. Click "🔍 See Next Step" to generate a guide hint

### Deleting a Game
1. Select the game you want to delete
2. Click "🗑️ Delete Game" at the bottom of the details panel
3. Confirm the deletion

## Project Structure

```
GameGuide/
├── .venv/                  # Virtual environment (not committed)
├── main.py                 # Main application file
├── game_progress.json      # Your saved game data (not committed)
├── Game Guide.html         # Original HTML prototype (not committed)
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## AI Integration (TODO)

The app has a placeholder for AI-powered guide hints. To integrate with your AI service:

1. Open `main.py`
2. Find the `generate_guide()` method
3. Replace the placeholder code with your AI API call
4. Use these variables:
   - `self.current_game` - The game title
   - `situation` - Current situation text
   - `self.objective_input.toPlainText()` - Next objective
   - `self.behavior_input.toPlainText()` - Output behavior preference

Example integration point:
```python
def generate_guide(self):
    # ... existing code ...
    
    # TODO: Replace with your AI API call
    # response = your_ai_api.get_guide_hint(
    #     game=self.current_game,
    #     situation=situation,
    #     objective=self.objective_input.toPlainText(),
    #     behavior=self.behavior_input.toPlainText()
    # )
    
    # guide_text = response.text
```

## Technologies Used

- **PyQt6**: Modern Qt6 bindings for Python
- **Python 3**: Core programming language
- **JSON**: Local data storage

## Design Philosophy

- **Windows 11 Inspired**: Clean, modern interface with rounded corners and soft shadows
- **User-Friendly**: Intuitive workflow with minimal clicks
- **Privacy-First**: All data stored locally, no cloud requirements
- **Lightweight**: Fast startup and minimal resource usage

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
