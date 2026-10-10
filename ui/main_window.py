import os
import sys
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QProgressBar, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


# Locate books.db relative to this file (works from anywhere)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "books.db")


# ------------------------------------------------------------------
# STYLESHEET — modern dark theme
# ------------------------------------------------------------------
STYLESHEET = """
QMainWindow {
    background-color: #1e1e2e;
}

QWidget {
    background-color: #1e1e2e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

QLabel {
    color: #e0e0e0;
}

QLabel#title_label {
    color: #00d4aa;
    font-size: 22px;
    font-weight: bold;
    padding: 8px;
}

QLabel#count_label {
    color: #a0a0b0;
    font-size: 14px;
    padding: 8px;
}

QPushButton {
    background-color: #00d4aa;
    color: #1e1e2e;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #00e8bb;
}

QPushButton:pressed {
    background-color: #00b894;
}

QPushButton:disabled {
    background-color: #444455;
    color: #888899;
}

QTableWidget {
    background-color: #252535;
    alternate-background-color: #2a2a3d;
    gridline-color: #33334d;
    color: #e0e0e0;
    font-size: 13px;
    border: 1px solid #33334d;
    border-radius: 6px;
    selection-background-color: #00d4aa;
    selection-color: #1e1e2e;
}

QTableWidget::item {
    padding: 6px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #00d4aa;
    color: #1e1e2e;
}

QHeaderView::section {
    background-color: #2d2d44;
    color: #00d4aa;
    padding: 10px;
    border: none;
    border-right: 1px solid #1e1e2e;
    border-bottom: 2px solid #00d4aa;
    font-weight: bold;
    font-size: 13px;
}

QHeaderView::section:hover {
    background-color: #3a3a55;
}

QProgressBar {
    background-color: #252535;
    border: 1px solid #33334d;
    border-radius: 6px;
    text-align: center;
    color: #e0e0e0;
    font-weight: bold;
    height: 22px;
}

QProgressBar::chunk {
    background-color: #00d4aa;
    border-radius: 5px;
}

QScrollBar:vertical {
    background: #1e1e2e;
    width: 12px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #3a3a55;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #00d4aa;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #1e1e2e;
    height: 12px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #3a3a55;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background: #00d4aa;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSA Project - Books Database")
        self.resize(1400, 800)
        self.setStyleSheet(STYLESHEET)

        # Main container
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # --- Top bar: title + count ---
        top_bar = QHBoxLayout()
        self.title_label = QLabel("📚 Books Database")
        self.title_label.setObjectName("title_label")
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()

        self.count_label = QLabel("Total: 0")
        self.count_label.setObjectName("count_label")
        top_bar.addWidget(self.count_label)
        layout.addLayout(top_bar)

        # --- Progress bar (placeholder for scraping controls) ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(15000)
        layout.addWidget(self.progress_bar)

        # --- Controls bar ---
        controls = QHBoxLayout()
        controls.setSpacing(10)
        self.refresh_btn = QPushButton("🔄  Refresh")
        self.refresh_btn.clicked.connect(self.load_books)
        controls.addWidget(self.refresh_btn)
        controls.addStretch()
        layout.addLayout(controls)

        # --- The table ---
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Title", "Author", "Year", "Publisher",
            "ISBN", "Pages", "Language", "Subject", "Editions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        # --- Load data ---
        self.load_books()

    def load_books(self):
        """Load all books from SQLite into the table."""
        if not os.path.exists(DB_PATH):
            QMessageBox.critical(self, "Missing DB",
                                 f"books.db not found at:\n{DB_PATH}")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                SELECT title, author, year, publisher, isbn,
                       pages, language, subject, edition_count
                FROM books
            """)
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            return

        self.table.setSortingEnabled(False)

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                item = QTableWidgetItem()
                if value is None:
                    item.setText("")
                elif isinstance(value, int):
                    item.setData(Qt.DisplayRole, value)
                else:
                    item.setText(str(value))
                self.table.setItem(r, c, item)

        self.table.setSortingEnabled(True)
        self.count_label.setText(f"Total: {len(rows):,} books")

        # Reasonable column widths
        widths = [320, 220, 80, 180, 140, 80, 100, 260, 80]
        for i, w in enumerate(widths):
            self.table.setColumnWidth(i, w)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()