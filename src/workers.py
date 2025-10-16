# -*- coding: utf-8 -*-
"""
Worker Threads Module

Contains background worker classes for non-blocking operations.
"""

from PyQt6.QtCore import QObject, QThread, pyqtSignal


class GuideGenerationWorker(QObject):
    """Worker thread for generating guide hints without freezing UI"""

    finished = pyqtSignal(dict)
    status_update = pyqtSignal(str)

    def __init__(self, game_title, situation, objective, behavior, api_key, provider, ai_manager, parent=None):
        super().__init__(parent)
        self.game_title = game_title
        self.situation = situation
        self.objective = objective
        self.behavior = behavior
        self.api_key = api_key
        self.provider = provider
        self.ai_manager = ai_manager

    def run(self):
        """Execute the AI guide generation"""
        try:
            result = self.ai_manager.call_ai_api(
                game_title=self.game_title,
                situation=self.situation,
                objective=self.objective,
                behavior=self.behavior,
                api_key=self.api_key,
                provider=self.provider,
                status_callback=self.status_update.emit
            )
            self.finished.emit(result)
        except Exception as exc:
            self.finished.emit({"error": str(exc)})