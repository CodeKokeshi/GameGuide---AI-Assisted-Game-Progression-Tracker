# -*- coding: utf-8 -*-
"""
Dialog Components Module

Contains dialog classes extracted from the original monolithic
implementation to keep the UI composition intact.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt6.QtGui import QFont


class AddGameDialog(QDialog):
    """Dialog for adding or renaming a game"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Game")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        title_label = QLabel("Enter Game Title:")
        title_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(title_label)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., The Legend of Zelda: Ocarina of Time")
        self.title_input.setFont(QFont("Segoe UI", 10))
        self.title_input.setStyleSheet(
            """
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
                color: #202020;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
            """
        )
        layout.addWidget(self.title_input)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Segoe UI", 10))
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                padding: 8px 20px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
                color: #202020;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            """
        )
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setAutoDefault(False)

        self.primary_button = QPushButton("Add Game")
        self.primary_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.primary_button.setStyleSheet(
            """
            QPushButton {
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                background-color: #0078d4;
                color: white;
            }
            QPushButton:hover {
                background-color: #006cbd;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            """
        )
        self.primary_button.clicked.connect(self.accept)
        self.primary_button.setDefault(True)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.primary_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.setStyleSheet(
            """
            QDialog {
                background-color: #f3f3f3;
            }
            QLabel {
                color: #202020;
            }
            """
        )

    def get_title(self):
        """Return the entered game title"""
        return self.title_input.text().strip()

    def set_primary_button_text(self, text):
        """Update the action button label"""
        self.primary_button.setText(text)