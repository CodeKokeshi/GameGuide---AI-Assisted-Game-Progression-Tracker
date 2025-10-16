"""
Game Progress Tracker - Application Module

Implements the main application window using the original layout and styling
from the monolithic version while delegating persistence and AI calls to
modular helpers.
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QTextEdit,
    QPlainTextEdit,
    QLineEdit,
    QFrame,
    QSplitter,
    QMessageBox,
    QComboBox,
    QScrollArea,
    QDialog,
)
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QFont, QIcon

from .data import DataManager
from .ai import AIManager
from .workers import GuideGenerationWorker
from .dialogs import AddGameDialog


class GameTrackerApp(QMainWindow):
    """Main application window coordinating UI, storage, and AI calls"""

    def __init__(self, app_icon_path=None):
        super().__init__()

        # Managers
        self.data_manager = DataManager()
        self.ai_manager = AIManager()

        # State
        self.games = self.data_manager.load_games()
        self.settings = self.data_manager.load_settings()
        self.current_game = None
        self.is_dark_mode = self.settings.get("dark_mode", True)
        self.is_edit_mode = False
        self._status_messages = []
        self._guide_output_updating = False
        self.current_worker_thread = None
        self.current_worker = None
        self.app_icon_path = app_icon_path

        # Window setup
        self.setWindowTitle("NextStep")
        self.setMinimumSize(1000, 600)
        if self.app_icon_path:
            self.setWindowIcon(QIcon(self.app_icon_path))

        self._build_ui()
        self._apply_styles()
        self._update_theme_button()
        self._load_api_settings()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        theme_bar = self._create_theme_bar()
        main_layout.addWidget(theme_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._create_library_panel())
        splitter.addWidget(self._create_details_panel())
        splitter.setSizes([350, 850])

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)

    def _create_theme_bar(self):
        bar = QWidget()
        bar.setFixedHeight(60)

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        ai_label = QLabel("AI Provider:")
        ai_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(ai_label)

        self.ai_provider_combo = QComboBox()
        self.ai_provider_combo.addItems(["Gemini", "ChatGPT", "Claude", "Other"])
        self.ai_provider_combo.setFont(QFont("Segoe UI", 10))
        self.ai_provider_combo.setFixedWidth(120)
        self.ai_provider_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ai_provider_combo.currentTextChanged.connect(self._on_ai_provider_changed)
        layout.addWidget(self.ai_provider_combo)

        api_label = QLabel("API Key:")
        api_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(api_label)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key...")
        self.api_key_input.setFont(QFont("Segoe UI", 10))
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setFixedWidth(250)
        self.api_key_input.textChanged.connect(self._on_api_key_changed)
        layout.addWidget(self.api_key_input)

        layout.addStretch()

        self.theme_button = QPushButton()
        self.theme_button.setFont(QFont("Segoe UI", 10))
        self.theme_button.setFixedSize(100, 35)
        self.theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_button.setObjectName("themeButton")
        self.theme_button.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_button)

        bar.setLayout(layout)
        return bar

    def _create_library_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(250)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        header_label = QLabel("📚 Game Library")
        header_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        self.game_list = QListWidget()
        self.game_list.setFont(QFont("Segoe UI", 10))
        self.game_list.itemClicked.connect(self._on_game_selected)
        self.game_list.itemDoubleClicked.connect(self._rename_game)
        self._populate_game_list()
        layout.addWidget(self.game_list, stretch=1)

        add_button = QPushButton("➕ Add New Game")
        add_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.setMinimumHeight(40)
        add_button.clicked.connect(self._add_new_game)
        layout.addWidget(add_button)

        panel.setLayout(layout)
        return panel

    def _create_details_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(400)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.game_title_label = QLabel("")
        self.game_title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.game_title_label.setWordWrap(True)
        layout.addWidget(self.game_title_label)

        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.Shape.HLine)
        self.divider.setMaximumHeight(2)
        layout.addWidget(self.divider)

        self.view_situation_label = QLabel("📝 Current Situation")
        self.view_situation_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.view_situation_label.setWordWrap(True)
        self.view_situation_label.setContentsMargins(0, 10, 0, 5)
        layout.addWidget(self.view_situation_label)

        self.view_situation_text = QLabel("")
        self.view_situation_text.setFont(QFont("Segoe UI", 10))
        self.view_situation_text.setWordWrap(True)
        self.view_situation_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.view_situation_text.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(self.view_situation_text)

        self.view_objective_label = QLabel("🎯 Next Objective")
        self.view_objective_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.view_objective_label.setWordWrap(True)
        self.view_objective_label.setContentsMargins(0, 10, 0, 5)
        layout.addWidget(self.view_objective_label)

        self.view_objective_text = QLabel("")
        self.view_objective_text.setFont(QFont("Segoe UI", 10))
        self.view_objective_text.setWordWrap(True)
        self.view_objective_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.view_objective_text.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(self.view_objective_text)

        self.view_guide_label = QLabel("💡 Guide Hint")
        self.view_guide_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.view_guide_label.setWordWrap(True)
        self.view_guide_label.setContentsMargins(0, 10, 0, 5)
        layout.addWidget(self.view_guide_label)

        self.view_guide_text = QLabel("")
        self.view_guide_text.setFont(QFont("Segoe UI", 10))
        self.view_guide_text.setWordWrap(True)
        self.view_guide_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.view_guide_text.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(self.view_guide_text)

        layout.addStretch()

        self.edit_button = QPushButton("✏️ Edit")
        self.edit_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_button.setMinimumHeight(40)
        self.edit_button.clicked.connect(self._enter_edit_mode)
        layout.addWidget(self.edit_button)

        self.edit_situation_label = QLabel("📝 Current Situation / What I Last Did:")
        self.edit_situation_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_situation_label.setWordWrap(True)
        layout.addWidget(self.edit_situation_label)

        self.situation_input = QTextEdit()
        self.situation_input.setPlaceholderText("Describe where you are in the game and what you last remember doing...")
        self.situation_input.setFont(QFont("Segoe UI", 10))
        self.situation_input.setMinimumHeight(80)
        self.situation_input.setMaximumHeight(120)
        self.situation_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.situation_input)

        self.edit_objective_label = QLabel("🎯 Next Objective (Optional):")
        self.edit_objective_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_objective_label.setWordWrap(True)
        layout.addWidget(self.edit_objective_label)

        self.objective_input = QTextEdit()
        self.objective_input.setPlaceholderText("What do you want to accomplish next? (Optional)")
        self.objective_input.setFont(QFont("Segoe UI", 10))
        self.objective_input.setMinimumHeight(60)
        self.objective_input.setMaximumHeight(80)
        self.objective_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.objective_input)

        self.edit_behavior_label = QLabel("⚙️ Output Behavior (Optional):")
        self.edit_behavior_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_behavior_label.setWordWrap(True)
        layout.addWidget(self.edit_behavior_label)

        self.behavior_input = QTextEdit()
        self.behavior_input.setPlaceholderText("How should the guide respond? e.g., 'Tell me how to prepare'")
        self.behavior_input.setFont(QFont("Segoe UI", 10))
        self.behavior_input.setMinimumHeight(60)
        self.behavior_input.setMaximumHeight(80)
        self.behavior_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.behavior_input)

        self.guide_button = QPushButton("🔍 See Next Step")
        self.guide_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.guide_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.guide_button.setMinimumHeight(40)
        self.guide_button.clicked.connect(self._generate_guide)
        layout.addWidget(self.guide_button)

        self.status_panel = QFrame()
        self.status_panel.setObjectName("statusPanel")
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(10, 8, 10, 8)
        status_layout.setSpacing(6)

        status_title = QLabel("Processing Status")
        status_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        status_layout.addWidget(status_title)

        self.status_display = QPlainTextEdit()
        self.status_display.setObjectName("statusDisplay")
        self.status_display.setReadOnly(True)
        self.status_display.setFont(QFont("Segoe UI", 9))
        self.status_display.setFixedHeight(120)
        self.status_display.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.status_display.setCursor(Qt.CursorShape.ArrowCursor)
        status_layout.addWidget(self.status_display)

        self.status_panel.setLayout(status_layout)
        self.status_panel.setVisible(False)
        layout.addWidget(self.status_panel)

        self.edit_guide_output_label = QLabel("💡 Guide Hint:")
        self.edit_guide_output_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_guide_output_label.setWordWrap(True)
        layout.addWidget(self.edit_guide_output_label)

        self.guide_output = QTextEdit()
        self.guide_output.setReadOnly(False)
        self.guide_output.setFont(QFont("Segoe UI", 10))
        self.guide_output.setPlaceholderText("Your guide hint will appear here after clicking 'See Next Step'...")
        self.guide_output.setMinimumHeight(120)
        self.guide_output.textChanged.connect(self._on_guide_output_changed)
        layout.addWidget(self.guide_output, stretch=1)

        button_row = QHBoxLayout()

        self.done_button = QPushButton("✓ Done")
        self.done_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.done_button.setMinimumHeight(35)
        self.done_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.done_button.clicked.connect(self._exit_edit_mode)
        button_row.addWidget(self.done_button)

        button_row.addStretch()

        self.delete_button = QPushButton("🗑️ Delete Game")
        self.delete_button.setFont(QFont("Segoe UI", 10))
        self.delete_button.setMinimumHeight(35)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.clicked.connect(self._delete_current_game)
        self.delete_button.setObjectName("deleteButton")
        button_row.addWidget(self.delete_button)

        layout.addLayout(button_row)

        self._set_details_enabled(False)

        content_widget.setLayout(layout)
        scroll_area.setWidget(content_widget)

        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)
        panel.setLayout(panel_layout)

        return panel

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------
    def _populate_game_list(self):
        self.game_list.clear()
        for title in sorted(self.games.keys()):
            self.game_list.addItem(QListWidgetItem(title))

    def _add_new_game(self):
        dialog = AddGameDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        title = dialog.get_title()
        if not title:
            QMessageBox.warning(self, "Invalid Input", "Please enter a game title!")
            return

        if title in self.games:
            QMessageBox.warning(self, "Game Exists", f"'{title}' is already in your library!")
            return

        self.games[title] = {"situation": "", "objective": "", "behavior": "", "guide": ""}
        self.data_manager.save_games(self.games)
        self._populate_game_list()

        items = self.game_list.findItems(title, Qt.MatchFlag.MatchExactly)
        if items:
            self.game_list.setCurrentItem(items[0])
            self._on_game_selected(items[0])

    def _rename_game(self, item):
        if not item:
            return

        old_title = item.text()
        dialog = AddGameDialog(self)
        dialog.setWindowTitle("Rename Game")
        dialog.set_primary_button_text("Rename")
        dialog.title_input.setText(old_title)
        dialog.title_input.selectAll()

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        new_title = dialog.get_title()
        if not new_title:
            QMessageBox.warning(self, "Invalid Input", "Please enter a game title!")
            return

        if new_title == old_title:
            return

        if new_title in self.games:
            QMessageBox.warning(self, "Game Exists", f"'{new_title}' is already in your library!")
            return

        self.games[new_title] = self.games.pop(old_title)
        if self.current_game == old_title:
            self.current_game = new_title

        self.data_manager.save_games(self.games)
        self._populate_game_list()

        items = self.game_list.findItems(new_title, Qt.MatchFlag.MatchExactly)
        if items:
            self.game_list.setCurrentItem(items[0])
            self._on_game_selected(items[0])

    # ------------------------------------------------------------------
    # Game selection and display
    # ------------------------------------------------------------------
    def _on_game_selected(self, item):
        if not item:
            return

        title = item.text()
        self.current_game = title
        self.is_edit_mode = False
        self._load_game_details(title)
        self._set_details_enabled(True)

    def _load_game_details(self, title):
        data = self.games.get(title, {})
        self.game_title_label.setText(title)

        self.situation_input.blockSignals(True)
        self.objective_input.blockSignals(True)
        self.behavior_input.blockSignals(True)
        self.guide_output.blockSignals(True)

        self.situation_input.setPlainText(data.get("situation", ""))
        self.objective_input.setPlainText(data.get("objective", ""))
        self.behavior_input.setPlainText(data.get("behavior", ""))
        self._set_guide_output_text(data.get("guide", ""))

        self.situation_input.blockSignals(False)
        self.objective_input.blockSignals(False)
        self.behavior_input.blockSignals(False)
        self.guide_output.blockSignals(False)

        self._update_view_mode()

    def _enter_edit_mode(self):
        self.is_edit_mode = True
        self.guide_output.setReadOnly(False)
        self._update_view_mode()

    def _exit_edit_mode(self):
        self.is_edit_mode = False
        self._update_view_mode()

    def _update_view_mode(self):
        if not self.current_game:
            return

        game_data = self.games.get(self.current_game, {})
        situation = game_data.get("situation", "")
        objective = game_data.get("objective", "")
        guide = game_data.get("guide", "")

        if self.is_edit_mode:
            self._set_view_elements_visible(False)
            self._set_edit_elements_visible(True)
            self.status_panel.setVisible(bool(self._status_messages))
        else:
            self._set_edit_elements_visible(False)
            self.status_panel.setVisible(False)
            self.view_situation_text.setText(situation)
            self.view_objective_text.setText(objective)
            self.view_guide_text.setText(guide)

            self.view_situation_label.setVisible(bool(situation))
            self.view_situation_text.setVisible(bool(situation))
            self.view_objective_label.setVisible(bool(objective))
            self.view_objective_text.setVisible(bool(objective))
            self.view_guide_label.setVisible(bool(guide))
            self.view_guide_text.setVisible(bool(guide))
            self.edit_button.setVisible(True)

    def _set_view_elements_visible(self, visible):
        self.view_situation_label.setVisible(visible)
        self.view_situation_text.setVisible(visible)
        self.view_objective_label.setVisible(visible)
        self.view_objective_text.setVisible(visible)
        self.view_guide_label.setVisible(visible)
        self.view_guide_text.setVisible(visible)
        self.edit_button.setVisible(visible)

    def _set_edit_elements_visible(self, visible):
        self.edit_situation_label.setVisible(visible)
        self.situation_input.setVisible(visible)
        self.edit_objective_label.setVisible(visible)
        self.objective_input.setVisible(visible)
        self.edit_behavior_label.setVisible(visible)
        self.behavior_input.setVisible(visible)
        self.guide_button.setVisible(visible)
        self.edit_guide_output_label.setVisible(visible)
        self.guide_output.setVisible(visible)
        self.done_button.setVisible(visible)
        self.delete_button.setVisible(visible)

    def _set_details_enabled(self, enabled):
        self._hide_status_panel()
        self.game_title_label.setVisible(enabled)
        self.divider.setVisible(enabled)

        if not enabled:
            self._set_view_elements_visible(False)
            self._set_edit_elements_visible(False)
            self.game_title_label.setText("")
            self.situation_input.clear()
            self.objective_input.clear()
            self.behavior_input.clear()
            self._set_guide_output_text("")
            self.guide_output.setReadOnly(False)
            self.is_edit_mode = False
        else:
            self.is_edit_mode = False
            self._update_view_mode()

    def _set_guide_output_text(self, text):
        """Update the guide output editor without triggering save hooks."""
        self._guide_output_updating = True
        try:
            self.guide_output.setPlainText(text)
        finally:
            self._guide_output_updating = False

    def _on_guide_output_changed(self):
        if self._guide_output_updating:
            return
        if not self.current_game or self.current_game not in self.games:
            return

        updated_text = self.guide_output.toPlainText()
        self.games[self.current_game]["guide"] = updated_text
        self.data_manager.save_games(self.games)

        if not self.is_edit_mode:
            self.view_guide_text.setText(updated_text)

    def _on_text_changed(self):
        if not self.current_game or self.current_game not in self.games:
            return

        self.games[self.current_game]["situation"] = self.situation_input.toPlainText()
        self.games[self.current_game]["objective"] = self.objective_input.toPlainText()
        self.games[self.current_game]["behavior"] = self.behavior_input.toPlainText()
        self.data_manager.save_games(self.games)

    # ------------------------------------------------------------------
    # AI guidance workflow
    # ------------------------------------------------------------------
    def _generate_guide(self):
        if not self.current_game:
            return

        situation = self.situation_input.toPlainText().strip()
        if not situation:
            QMessageBox.warning(self, "Missing Information", "Please fill in the 'Current Situation' field first!")
            return

        provider = self.settings.get("ai_provider", "Gemini")
        api_key = self.data_manager.load_api_key(provider)

        if not api_key:
            QMessageBox.warning(self, "API Key Missing", "Please enter your API key in the top bar!")
            return

        self.guide_button.setEnabled(False)
        self.guide_button.setText("⏳ Generating...")
        self._clear_status_log()
        self._status_messages.append("Starting guide generation...")
        self._show_status_panel()
        self.guide_output.setReadOnly(True)
        self._set_guide_output_text("Searching game guides for your next move...")

        params = {
            "game_title": self.current_game,
            "situation": situation,
            "objective": self.objective_input.toPlainText().strip(),
            "behavior": self.behavior_input.toPlainText().strip(),
            "api_key": api_key,
            "provider": provider,
        }

        self.current_worker_thread = QThread()
        self.current_worker = GuideGenerationWorker(
            params["game_title"],
            params["situation"],
            params["objective"],
            params["behavior"],
            params["api_key"],
            params["provider"],
            self.ai_manager,
        )

        self.current_worker.moveToThread(self.current_worker_thread)
        self.current_worker_thread.started.connect(self.current_worker.run)
        self.current_worker.status_update.connect(self._on_status_update)
        self.current_worker.finished.connect(self._on_worker_finished)
        self.current_worker.finished.connect(self.current_worker_thread.quit)
        self.current_worker.finished.connect(self.current_worker.deleteLater)
        self.current_worker_thread.finished.connect(self.current_worker_thread.deleteLater)

        self.current_worker_thread.start()

    def _on_worker_finished(self, result):
        self._reset_guide_button()

        if result.get("error"):
            message = result["error"]
            QMessageBox.critical(self, "API Error", f"Error generating guide:\n\n{message}")
            self._set_guide_output_text(f"Failed to generate hint.\n\nError: {message}")
            self.guide_output.setReadOnly(False)
            self._hide_status_panel()
            return

        guides = result.get("guides", [])
        provider = result.get("provider", "Unknown")
        evaluation = result.get("evaluation")
        model_name = result.get("model_used")
        refined_context = result.get("refined_context")

        if not guides:
            self._set_guide_output_text("No guide suggestions were returned. Please try again with more context.")
            self.guide_output.setReadOnly(False)
            self._hide_status_panel()
            return

        display_text = self._format_guide_output(
            guides,
            provider,
            evaluation=evaluation,
            model_name=model_name,
            refined_context=refined_context,
        )
        self._set_guide_output_text(display_text)

        if self.current_game:
            self.games[self.current_game]["guide"] = display_text
            self.data_manager.save_games(self.games)

        if not self.is_edit_mode:
            self._update_view_mode()

        self._hide_status_panel()
        self.guide_output.setReadOnly(False)

    def _on_status_update(self, message):
        if not message:
            return
        self._status_messages.append(message)
        self._show_status_panel()

    def _reset_guide_button(self):
        self.guide_button.setEnabled(True)
        self.guide_button.setText("🔍 See Next Step")

    def _clear_status_log(self):
        self._status_messages = []
        self.status_display.clear()

    def _show_status_panel(self):
        if not self.status_panel.isVisible():
            self.status_panel.setVisible(True)
        if not self._status_messages:
            self.status_display.clear()
            return
        self.status_display.setPlainText("\n".join(self._status_messages))
        scrollbar = self.status_display.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def _hide_status_panel(self):
        self.status_panel.setVisible(False)
        self.status_display.clear()
        self._status_messages = []

    # ------------------------------------------------------------------
    # Guide formatting (matching original behaviour)
    # ------------------------------------------------------------------
    def _format_guide_output(self, guides, provider, evaluation=None, model_name=None, refined_context=None):
        if not guides:
            return "No guide suggestions available."

        aggregation = {}
        order = []
        total = 0

        for idx, guide in enumerate(guides, start=1):
            text = (guide.get("text", "") or "").strip()
            if not text:
                continue

            normalized = " ".join(text.lower().split())
            if normalized not in aggregation:
                aggregation[normalized] = {"text": text, "sources": set(), "count": 0, "indices": []}
                order.append(normalized)

            entry = aggregation[normalized]
            entry["count"] += 1
            entry["indices"].append(idx)
            total += 1

            for src in guide.get("sources", []):
                if src:
                    entry["sources"].add(src)

        recommended_original_index = 0
        evaluation_confidence = ""
        evaluation_reasoning = ""

        if evaluation:
            try:
                recommended_original_index = int(evaluation.get("recommended_index", 0) or 0)
            except (ValueError, TypeError):
                recommended_original_index = 0

            confidence_value = evaluation.get("confidence")
            if confidence_value not in (None, ""):
                try:
                    evaluation_confidence = f"{float(confidence_value):.0f}%"
                except (ValueError, TypeError):
                    evaluation_confidence = str(confidence_value)

            evaluation_reasoning = str(evaluation.get("reasoning", "")).strip()

        aggregated_guides = []
        recommended_agg_index = 0

        for display_idx, key in enumerate(order, start=1):
            data = aggregation[key]
            trust_value = 100.0 if total == 0 else (data["count"] / total) * 100.0
            trust_display = f"{trust_value:.1f}%" if trust_value % 1 else f"{int(trust_value)}%"

            if recommended_original_index and recommended_original_index in data["indices"]:
                recommended_agg_index = display_idx

            aggregated_guides.append(
                {
                    "display_index": display_idx,
                    "text": data["text"],
                    "sources": sorted(data["sources"]),
                    "trust": trust_display,
                    "count": data["count"],
                    "original_indices": data["indices"],
                }
            )

        provider_line = f"Provider: {provider}"
        if model_name:
            provider_line += f" (model: {model_name})"

        lines = ["Guide Hint Suggestions", provider_line]

        context_block = (refined_context or "").strip()
        if context_block:
            lines.append("")
            lines.append("Context Clarification")
            lines.append(context_block)
        lines.append("")

        if aggregated_guides and len(aggregated_guides) > 1 and recommended_agg_index:
            trust_display = evaluation_confidence or aggregated_guides[recommended_agg_index - 1]["trust"]
            lines.append(f"Recommended Guide: #{recommended_agg_index} — Trust Score: {trust_display}")
            if evaluation_reasoning:
                lines.append(f"Why: {evaluation_reasoning}")
            lines.append("")

        for entry in aggregated_guides:
            is_recommended = entry["display_index"] == recommended_agg_index and recommended_agg_index > 0
            marker = "★" if is_recommended else " "
            trust_value_display = entry["trust"]
            if is_recommended and evaluation_confidence:
                trust_value_display = evaluation_confidence
            trust_suffix = f" [Trust Score: {trust_value_display}]" if trust_value_display else ""
            lines.append(f"{entry['display_index']}. {marker} {entry['text']}{trust_suffix}")

            if entry["sources"]:
                lines.append("   Sources:")
                for src in entry["sources"]:
                    lines.append(f"     • {src}")
            lines.append("")

        return "\n".join(lines).strip()

    # ------------------------------------------------------------------
    # Theme & settings persistence
    # ------------------------------------------------------------------
    def _toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.settings["dark_mode"] = self.is_dark_mode
        self.data_manager.save_settings(self.settings)
        self._apply_styles()
        self._update_theme_button()

    def _update_theme_button(self):
        self.theme_button.setText("🌙 Dark" if self.is_dark_mode else "☀️ Light")

    def _apply_styles(self):
        if self.is_dark_mode:
            bg_main = "#1e1e1e"
            bg_panel = "#252526"
            bg_input = "#2d2d30"
            bg_list = "#2d2d30"
            text_primary = "#e0e0e0"
            text_secondary = "#ffffff"
            border_color = "#3e3e42"
            hover_bg = "#3e3e42"
            selected_bg = "#094771"
            selected_text = "#60cdff"
            scrollbar_bg = "#3e3e42"
            scrollbar_handle = "#686868"
            scrollbar_hover = "#9e9e9e"
        else:
            bg_main = "#f9f9f9"
            bg_panel = "#ffffff"
            bg_input = "#ffffff"
            bg_list = "#fafafa"
            text_primary = "#202020"
            text_secondary = "#202020"
            border_color = "#e0e0e0"
            hover_bg = "#f0f0f0"
            selected_bg = "#e3f2fd"
            selected_text = "#0078d4"
            scrollbar_bg = "#f0f0f0"
            scrollbar_handle = "#c0c0c0"
            scrollbar_hover = "#a0a0a0"

        self.setStyleSheet(
            f"""
            QMainWindow {{ background-color: {bg_main}; }}
            QWidget {{ background-color: {bg_main}; color: {text_primary}; }}
            QFrame {{ background-color: {bg_panel}; border: 1px solid {border_color}; }}
            QFrame#statusPanel {{ border: 1px dashed {border_color}; background-color: {bg_panel}; }}
            QLabel {{ color: {text_primary}; background-color: transparent; border: none; }}
            QListWidget {{ background-color: {bg_list}; border: 1px solid {border_color}; border-radius: 6px; padding: 5px; outline: none; color: {text_primary}; }}
            QListWidget::item {{ padding: 12px; border-radius: 4px; margin: 2px; color: {text_primary}; }}
            QListWidget::item:selected {{ background-color: {selected_bg}; color: {selected_text}; }}
            QListWidget::item:hover {{ background-color: {hover_bg}; color: {text_primary}; }}
            QTextEdit {{ border: 2px solid {border_color}; border-radius: 6px; padding: 10px; background-color: {bg_input}; color: {text_primary}; }}
            QTextEdit:focus {{ border: 2px solid #0078d4; }}
            QPlainTextEdit#statusDisplay {{ border: 1px solid {border_color}; border-radius: 6px; padding: 8px; background-color: {bg_panel}; color: {text_primary}; }}
            QPlainTextEdit#statusDisplay:focus {{ border: 1px solid {border_color}; }}
            QScrollArea {{ border: none; background-color: {bg_panel}; }}
            QScrollArea > QWidget > QWidget {{ background-color: {bg_panel}; }}
            QScrollBar:vertical {{ border: none; background: {scrollbar_bg}; width: 10px; border-radius: 5px; }}
            QScrollBar::handle:vertical {{ background: {scrollbar_handle}; border-radius: 5px; min-height: 20px; }}
            QScrollBar::handle:vertical:hover {{ background: {scrollbar_hover}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            QPushButton {{ background-color: #0078d4; color: white; border: none; border-radius: 6px; padding: 10px 20px; }}
            QPushButton:hover {{ background-color: #006cbd; }}
            QPushButton:pressed {{ background-color: #005a9e; }}
            QPushButton:disabled {{ background-color: #cccccc; color: #666666; }}
            QPushButton#deleteButton {{ background-color: #d32f2f; }}
            QPushButton#deleteButton:hover {{ background-color: #b71c1c; }}
            QPushButton#themeButton {{ background-color: {bg_input}; color: {text_primary}; border: 1px solid {border_color}; }}
            QPushButton#themeButton:hover {{ background-color: {hover_bg}; }}
            QComboBox {{ background-color: {bg_input}; color: {text_primary}; border: 2px solid {border_color}; border-radius: 4px; padding: 5px; }}
            QComboBox:hover {{ border: 2px solid #0078d4; }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox::down-arrow {{ image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid {text_primary}; margin-right: 5px; }}
            QComboBox QAbstractItemView {{ background-color: {bg_input}; color: {text_primary}; selection-background-color: {selected_bg}; selection-color: {selected_text}; border: 1px solid {border_color}; }}
            QLineEdit {{ background-color: {bg_input}; color: {text_primary}; border: 2px solid {border_color}; border-radius: 4px; padding: 5px; }}
            QLineEdit:focus {{ border: 2px solid #0078d4; }}
        """
        )

    # ------------------------------------------------------------------
    # Settings persistence helpers
    # ------------------------------------------------------------------
    def _load_api_settings(self):
        provider = self.settings.get("ai_provider", "Gemini")
        index = self.ai_provider_combo.findText(provider)
        if index >= 0:
            self.ai_provider_combo.setCurrentIndex(index)

        api_key = self.data_manager.load_api_key(provider)
        if api_key:
            self.api_key_input.setText(api_key)

    def _on_ai_provider_changed(self, provider):
        self.settings["ai_provider"] = provider
        self.data_manager.save_settings(self.settings)

    def _on_api_key_changed(self):
        provider = self.settings.get("ai_provider", "Gemini")
        api_key = self.api_key_input.text().strip()
        if api_key:
            self.data_manager.save_api_key(provider, api_key)

    def _delete_current_game(self):
        if not self.current_game:
            return

        reply = QMessageBox.question(
            self,
            "Delete Game",
            f"Are you sure you want to delete '{self.current_game}' from your library?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.games.pop(self.current_game, None)
        self.current_game = None
        self.data_manager.save_games(self.games)
        self._populate_game_list()
        self._set_details_enabled(False)