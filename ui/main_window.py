import os
import sys
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QProgressBar, QHeaderView, QMessageBox, QComboBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from algorithms.sorting import ALL_SORTS


# Locate books.db relative to this file (works from anywhere)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "books.db")


# Column headers and their indices in the SQL result
COLUMNS = ["Title", "Author", "Year", "Publisher",
           "ISBN", "Pages", "Language", "Subject", "Editions"]


# ------------------------------------------------------------------
# STYLESHEET — modern dark theme
# ------------------------------------------------------------------
STYLESHEET = """
QMainWindow { background-color: #1e1e2e; }
QWidget {
    background-color: #1e1e2e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}
QLabel { color: #e0e0e0; }
QLabel#title_label {
    color: #00d4aa; font-size: 22px; font-weight: bold; padding: 8px;
}
QLabel#count_label {
    color: #a0a0b0; font-size: 14px; padding: 8px;
}
QLabel#metrics_label {
    color: #e0e0e0; font-size: 13px; padding: 6px 12px;
    background-color: #252535; border-radius: 6px;
}
QLabel#algo_info {
    color: #00d4aa; font-size: 12px; font-style: italic; padding: 4px 12px;
}
QFrame#sort_panel {
    background-color: #252535; border-radius: 8px; padding: 10px;
}
QComboBox {
    background-color: #2d2d44; color: #e0e0e0;
    border: 1px solid #33334d; border-radius: 6px;
    padding: 8px 12px; font-size: 13px; min-width: 150px;
}
QComboBox:hover { border: 1px solid #00d4aa; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #2d2d44; color: #e0e0e0;
    selection-background-color: #00d4aa;
    selection-color: #1e1e2e;
    border: 1px solid #33334d;
}
QPushButton {
    background-color: #00d4aa; color: #1e1e2e;
    border: none; padding: 10px 20px;
    border-radius: 6px; font-size: 13px; font-weight: bold;
}
QPushButton:hover { background-color: #00e8bb; }
QPushButton:pressed { background-color: #00b894; }
QPushButton:disabled { background-color: #444455; color: #888899; }
QTableWidget {
    background-color: #252535;
    alternate-background-color: #2a2a3d;
    gridline-color: #33334d;
    color: #e0e0e0; font-size: 13px;
    border: 1px solid #33334d; border-radius: 6px;
    selection-background-color: #00d4aa;
    selection-color: #1e1e2e;
}
QTableWidget::item { padding: 6px; border: none; }
QTableWidget::item:selected {
    background-color: #00d4aa; color: #1e1e2e;
}
QHeaderView::section {
    background-color: #2d2d44; color: #00d4aa;
    padding: 10px; border: none;
    border-right: 1px solid #1e1e2e;
    border-bottom: 2px solid #00d4aa;
    font-weight: bold; font-size: 13px;
}
QHeaderView::section:hover { background-color: #3a3a55; }
QProgressBar {
    background-color: #252535;
    border: 1px solid #33334d; border-radius: 6px;
    text-align: center; color: #e0e0e0;
    font-weight: bold; height: 22px;
}
QProgressBar::chunk { background-color: #00d4aa; border-radius: 5px; }
QScrollBar:vertical {
    background: #1e1e2e; width: 12px; margin: 0;
}
QScrollBar::handle:vertical {
    background: #3a3a55; border-radius: 6px; min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #00d4aa; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #1e1e2e; height: 12px; margin: 0;
}
QScrollBar::handle:horizontal {
    background: #3a3a55; border-radius: 6px; min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background: #00d4aa; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSA Project - Books Database")
        self.resize(1500, 850)
        self.setStyleSheet(STYLESHEET)

        # Holds the current data as list of tuples (unsorted copy)
        self.raw_data = []

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

        # --- Sort panel ---
        sort_panel = QFrame()
        sort_panel.setObjectName("sort_panel")
        sort_layout = QHBoxLayout(sort_panel)
        sort_layout.setSpacing(10)

        sort_layout.addWidget(QLabel("Sort by:"))
        self.column_combo = QComboBox()
        self.column_combo.addItems(COLUMNS)
        sort_layout.addWidget(self.column_combo)

        sort_layout.addWidget(QLabel("Algorithm:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(list(ALL_SORTS.keys()))
        self.algo_combo.currentTextChanged.connect(self.update_algo_info)
        sort_layout.addWidget(self.algo_combo)

        self.sort_btn = QPushButton("🔀  Sort")
        self.sort_btn.clicked.connect(self.run_sort)
        sort_layout.addWidget(self.sort_btn)

        sort_layout.addStretch()
        layout.addWidget(sort_panel)

        # --- Metrics panel ---
        metrics_layout = QHBoxLayout()
        self.time_label = QLabel("⏱ Time: —")
        self.time_label.setObjectName("metrics_label")
        self.comparisons_label = QLabel("🔍 Comparisons: —")
        self.comparisons_label.setObjectName("metrics_label")
        self.swaps_label = QLabel("🔄 Swaps: —")
        self.swaps_label.setObjectName("metrics_label")
        metrics_layout.addWidget(self.time_label)
        metrics_layout.addWidget(self.comparisons_label)
        metrics_layout.addWidget(self.swaps_label)
        metrics_layout.addStretch()
        layout.addLayout(metrics_layout)

        self.algo_info = QLabel("")
        self.algo_info.setObjectName("algo_info")
        layout.addWidget(self.algo_info)

        # --- Progress bar (for future scraping controls) ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(15000)
        self.progress_bar.setVisible(False)   # hide until needed
        layout.addWidget(self.progress_bar)

        # --- The table ---
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setSortingEnabled(False)   # we handle sorting ourselves
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        # --- Initial load ---
        self.load_books()
        self.update_algo_info(self.algo_combo.currentText())

    # ----------------------------------------------------------------
    # DATA LOADING
    # ----------------------------------------------------------------
    def load_books(self):
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
            self.raw_data = cur.fetchall()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            return

        self.populate_table(self.raw_data)
        self.count_label.setText(f"Total: {len(self.raw_data):,} books")

    def populate_table(self, rows):
        """Fill the table with the given rows."""
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

        widths = [320, 220, 80, 180, 140, 80, 100, 260, 80]
        for i, w in enumerate(widths):
            self.table.setColumnWidth(i, w)

    # ----------------------------------------------------------------
    # SORTING
    # ----------------------------------------------------------------
    def update_algo_info(self, algo_name):
        """Update the complexity/stability info label below the combo."""
        from algorithms.sorting import ALL_SORTS
        if algo_name not in ALL_SORTS:
            return
        # Run once on an empty list to get metadata
        sample = ALL_SORTS[algo_name]([], 0)
        stable_str = "Stable ✅" if sample.stable else "Not stable ❌"
        self.algo_info.setText(
            f"ℹ️  {sample.algorithm}  •  Time complexity: {sample.complexity}  •  {stable_str}"
        )

    def run_sort(self):
        """Sort the raw data by the selected column with the selected algorithm."""
        col_index = self.column_combo.currentIndex()
        algo_name = self.algo_combo.currentText()
        algo_func = ALL_SORTS[algo_name]

        # Disable button to prevent double-click
        self.sort_btn.setEnabled(False)
        self.sort_btn.setText("Sorting…")
        QApplication.processEvents()

        try:
            result = algo_func(self.raw_data, col_index)
        except Exception as e:
            QMessageBox.critical(self, "Sort Error", str(e))
            self.sort_btn.setEnabled(True)
            self.sort_btn.setText("🔀  Sort")
            return

        # Update table with sorted rows
        self.populate_table(result.sorted_data)

        # Update metrics
        self.time_label.setText(f"⏱ Time: {result.time_ms:.2f} ms")
        self.comparisons_label.setText(
            f"🔍 Comparisons: {result.comparisons:,}"
        )
        self.swaps_label.setText(f"🔄 Swaps: {result.swaps:,}")

        # Restore button
        self.sort_btn.setEnabled(True)
        self.sort_btn.setText("🔀  Sort")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()