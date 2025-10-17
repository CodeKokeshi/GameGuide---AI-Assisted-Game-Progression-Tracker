# NextStep - AI-Assisted Game Progress Tracker

A modern, Windows 11-styled desktop application that helps you track your progress in games and get AI-powered guidance when you're stuck or returning after a break. Perfect for games with complex quest systems or when you haven't played in months and need to remember what you were doing.

## 🎯 Current Features

### 📚 Game Library Management
- Add unlimited games to your personal library
- Visual status indicators (✅ for completed games)
- Track completion status: **In Progress** or **Completed**
- Clean, organized list view with search capabilities
- Delete games with confirmation

### 🎮 Comprehensive Game Tracking
For each game, track:
- **Game Status**: Mark as "In Progress" or "Completed"
- **Current Situation**: Document where you are and what you last did
- **Next Objective** (Optional): Plan what you want to accomplish
- **AI Output Style**: Choose how the AI should respond to you

### 🤖 AI-Powered Guide Hints (Gemini)
- **5 Output Styles** to match your needs:
  - **Walkthrough Style**: Step-by-step next actions
  - **Strategic Planning**: Comprehensive preparation and approach
  - **Contextual Analysis**: Understand your current situation
  - **Tips & Tricks**: Exploits, secrets, and optimization
  - **Custom Instructions**: Define your own AI behavior
- Powered by **Google Gemini** with Search Grounding for accurate, up-to-date information
- Generates multiple guide options and selects the best one
- Beautiful **Markdown rendering** with formatting, lists, links, and more

### 🎨 Modern User Interface
- **Dark/Light Theme** toggle with persistence
- **View Mode**: Clean, readable display with markdown rendering
- **Edit Mode**: Easy editing with syntax highlighting
- **Seamless transitions** between modes
- Windows 11-inspired design with rounded corners and modern styling

### 💾 Smart Data Management
- **Auto-save**: All changes saved instantly
- **Local storage**: Privacy-first with JSON files
- **Encrypted API keys**: Secure storage with Fernet encryption
- **Backward compatible**: Old data automatically migrates to new format

### 🔒 Secure Settings
- API key encryption for safe credential storage
- Settings persist across sessions
- Theme preferences saved

---

## 📦 Installation

### Prerequisites
- **Python 3.9+** (Python 3.13.2 recommended)
- **Windows 10/11** (works on other platforms too)
- **Google Gemini API Key** ([Get one free here](https://aistudio.google.com/app/apikey))

### Step-by-Step Setup

1. **Clone the repository**
   ```powershell
   git clone https://github.com/CodeKokeshi/NextStep-An-AI-Assisted-Game-Progress-Tracker.git
   cd NextStep-An-AI-Assisted-Game-Progress-Tracker
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install pyqt6 requests cryptography markdown
   ```

4. **Run the application**
   ```powershell
   python main.py
   ```

5. **Configure API Key** (First Launch)
   - Click **⚙️ Settings** in the toolbar
   - Enter your **Gemini API Key**
   - Click **Save Settings**

---

## 🚀 Usage Guide

### Adding Your First Game
1. Click **➕ Add New Game** in the left sidebar
2. Enter the game title (e.g., "The Legend of Zelda: Tears of the Kingdom")
3. Click **Add Game**

### Tracking Your Progress
1. **Select a game** from your library
2. Click **✏️ Edit** to enter edit mode
3. Set **Game Status** (In Progress by default)
4. Fill in **Current Situation** (e.g., "Just defeated Goron City boss, need to find the next sage")
5. Add **Next Objective** if you have one (e.g., "Find the Water Temple")
6. Choose your preferred **Output Style** (try Walkthrough Style first)
7. Click **🔍 See Next Step** to get AI guidance

### Reading AI Guidance
- The guide appears in beautiful **markdown format**
- **View Mode**: Rendered with formatting, lists, bold text, and clickable links
- **Edit Mode**: See raw markdown if you want to copy/edit

### Switching Themes
- Click the **🌙 Dark** / **☀️ Light** button in the toolbar
- Your preference is saved automatically

### Marking Games as Completed
1. Select a game and click **✏️ Edit**
2. Change **Game Status** dropdown to **Completed**
3. The game will show a **✅** checkmark in your library

---

## 🗺️ Future Plans

### 🔥 High Priority
- **More Themes**: Cyberpunk, Retro, Gaming-inspired themes, Custom theme creator

### 📋 Medium Priority
- **Search/Filter Games**: Search bar, filter by status, sort options, quick tags
- **Backup/Restore**: Auto-backup, restore from file, version history
- **Export Progress Report**: Export to PDF/HTML/Markdown with formatted layout
- **Smart Objectives Suggestion**: AI suggests next objectives based on game progression
- **Game Recommendations**: AI analyzes your library and suggests similar games
- **Quest Chain Tracker**: Visual dependency tree and progression timeline

### 🎯 Low Priority
- **Screenshot Analysis**: Upload screenshots, AI analyzes and fills situation (requires vision API)
- **Conversation Mode**: Chat-based interaction with persistent context per game
- **Improved Library Display**: Cover art, custom icons, grid view, metadata badges

### ✅ Recently Completed
- ✅ **Game Status Tracking** (In Progress/Completed with visual indicators)
- ✅ **Output Style Dropdown** (5 preset styles + custom)
- ✅ **Markdown Rendering** (Beautiful formatting in view mode)
- ✅ **Dark/Light Theme Toggle**

---

## 🛠️ Helpful Information

### Project Structure
```
NextStep-An-AI-Assisted-Game-Progress-Tracker/
├── .venv/                      # Virtual environment
├── src/                        # Source code
│   ├── __init__.py
│   ├── app.py                 # Main application UI
│   ├── ai.py                  # AI integration (Gemini)
│   ├── data.py                # Data management & encryption
│   ├── dialogs.py             # UI dialogs (Add Game, Settings)
│   └── workers.py             # Background threads for AI calls
├── main.py                    # Application entry point
├── game_progress.json         # Your saved games (auto-created)
├── settings.json              # App settings (auto-created)
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

### Data Storage
- **game_progress.json**: Stores all your games and progress (not committed to git)
- **settings.json**: Stores API keys (encrypted), theme, and preferences (not committed to git)
- Both files are created automatically on first run

### AI Output Styles Explained

1. **Walkthrough Style (Next Step)**
   - Quick, actionable next steps
   - "Go to X, talk to Y, do Z"
   - Best for: Getting unstuck quickly

2. **Strategic Planning Style**
   - Comprehensive breakdown of approach
   - Preparation, strategy, tactics
   - Best for: Boss fights, difficult sections

3. **Contextual Analysis Style**
   - Explains your current situation
   - Story context, significance, connections
   - Best for: Understanding what's happening

4. **Tips & Tricks Style**
   - Exploits, secrets, optimizations
   - Hidden mechanics, shortcuts
   - Best for: Completionists, speedrunners

5. **Custom Instructions**
   - Define your own AI behavior
   - Examples: "Be concise", "No spoilers", "Focus on side quests"
   - Best for: Specific needs

### Keyboard Shortcuts
- **Ctrl+N**: Add new game (when focused on app)
- **Ctrl+E**: Enter edit mode (when game selected)
- **Ctrl+S**: Save and exit edit mode (when in edit mode)
- **Delete**: Delete selected game (with confirmation)

### Troubleshooting

**"No Response Returned" Error**
- Check your Gemini API key in Settings
- Verify you have internet connection
- Ensure you have API quota remaining (free tier has limits)

**App won't start**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install pyqt6 requests cryptography markdown`
- Check Python version: `python --version` (should be 3.9+)

**Themes not switching**
- Try restarting the app
- Check if settings.json exists and is writable

**Games not saving**
- Ensure game_progress.json is not read-only
- Check you have write permissions in the app directory

### Contributing
Contributions are welcome! If you'd like to add features or fix bugs:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Technologies Used
- **PyQt6**: Modern Qt6 bindings for Python GUI
- **Google Gemini API**: AI-powered guide generation with Search Grounding
- **Python 3.13**: Core programming language
- **Cryptography**: Fernet encryption for API keys
- **Markdown**: Beautiful text formatting
- **JSON**: Local data storage

### Design Philosophy
- **Privacy-First**: All data stored locally, no telemetry
- **User-Friendly**: Intuitive workflow, minimal clicks
- **Modern**: Windows 11-inspired design
- **Lightweight**: Fast startup, low resource usage
- **Extensible**: Modular code, easy to add features

### License
This project is open source. Feel free to use, modify, and distribute.

### Support
- **Issues**: Report bugs or request features on GitHub Issues
- **Discussions**: Join conversations on GitHub Discussions

---

**Made with ❤️ for gamers who forget what they were doing**

*Last Updated: 2025-10-17 | Version: 2.0*
