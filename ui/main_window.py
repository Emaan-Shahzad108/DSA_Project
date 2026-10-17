import os
import sys
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QProgressBar, QHeaderView, QMessageBox, QComboBox, QFrame,
    QLineEdit, QCheckBox, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from algorithms.sorting import ALL_SORTS
from algorithms.benchmark_worker import BenchmarkWorker


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "books.db")

COLUMNS = ["Title", "Author", "Year", "Publisher",
           "ISBN", "Pages", "Language", "Subject", "Editions"]

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
QComboBox, QLineEdit {
    background-color: #2d2d44; color: #e0e0e0;
    border: 1px solid #33334d; border-radius: 6px;
    padding: 8px 12px; font-size: 13px; min-width: 120px;
}
QComboBox:hover, QLineEdit:hover { border: 1px solid #00d4aa; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #2d2d44; color: #e0e0e0;
    selection-background-color: #00d4aa;
    selection-color: #1e1e2e;
    border: 1px solid #33334d;
}
QCheckBox { color: #e0e0e0; font-size: 13px; padding: 4px; }
QCheckBox::indicator { width: 18px; height: 18px; }
QPushButton {
    background-color: #00d4aa; color: #1e1e2e;
    border: none; padding: 10px 20px;
    border-radius: 6px; font-size: 13px; font-weight: bold;
}
QPushButton:hover { background-color: #00e8bb; }
QPushButton:pressed { background-color: #00b894; }
QPushButton:disabled { background-color: #444455; color: #888899; }
QPushButton#clear_btn { background-color: #e74c3c; }
QPushButton#clear_btn:hover { background-color: #c0392b; }
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
QSplitter::handle {
    background-color: #33334d;
    height: 6px;
}
QSplitter::handle:hover {
    background-color: #00d4aa;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSA Project - Books Database")
        self.resize(1500, 950)  # Made window slightly taller
        self.setStyleSheet(STYLESHEET)

        self.raw_data = []
        self.filtered_data = []
        self.benchmark_worker = None

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # ==========================================
        # TOP WIDGET (Controls)
        # ==========================================
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5) # Tight spacing

        # Top bar
        top_bar = QHBoxLayout()
        self.title_label = QLabel("📚 Books Database")
        self.title_label.setObjectName("title_label")
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        self.count_label = QLabel("Total: 0")
        self.count_label.setObjectName("count_label")
        top_bar.addWidget(self.count_label)
        top_layout.addLayout(top_bar)

        # Search Panel
        search_panel = QFrame()
        search_panel.setObjectName("sort_panel")
        search_layout = QHBoxLayout(search_panel)
        search_layout.setSpacing(10)

        search_layout.addWidget(QLabel("🔍 Search:"))
        self.search_col_combo = QComboBox()
        self.search_col_combo.addItems(COLUMNS)
        search_layout.addWidget(self.search_col_combo)

        self.search_cond_combo = QComboBox()
        self.search_cond_combo.addItems([
            "Contains", "Starts With", "Ends With", "Equals", 
            "Greater Than", "Less Than"
        ])
        search_layout.addWidget(self.search_cond_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type search query here…")
        self.search_input.returnPressed.connect(self.run_search)
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("Apply")
        self.search_btn.clicked.connect(self.run_search)
        search_layout.addWidget(self.search_btn)

        self.clear_btn = QPushButton("✖ Clear")
        self.clear_btn.setObjectName("clear_btn")
        self.clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_btn)

        search_layout.addStretch()
        top_layout.addWidget(search_panel)

        # Sort panel
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

        self.scope_checkbox = QCheckBox("Sort only filtered results")
        sort_layout.addWidget(self.scope_checkbox)

        sort_layout.addStretch()
        top_layout.addWidget(sort_panel)

        # Metrics panel & Algo Info (Side by side to save space)
        metrics_layout = QHBoxLayout()
        self.time_label = QLabel("⏱ Time: —")
        self.time_label.setObjectName("metrics_label")
        self.comparisons_label = QLabel("🔍 Comparisons: —")
        self.comparisons_label.setObjectName("metrics_label")
        self.swaps_label = QLabel("🔄 Swaps: —")
        self.swaps_label.setObjectName("metrics_label")
        
        self.algo_info = QLabel("")
        self.algo_info.setObjectName("algo_info")

        metrics_layout.addWidget(self.time_label)
        metrics_layout.addWidget(self.comparisons_label)
        metrics_layout.addWidget(self.swaps_label)
        metrics_layout.addStretch()
        metrics_layout.addWidget(self.algo_info)
        top_layout.addLayout(metrics_layout)

        # Benchmark panel
        bench_panel = QFrame()
        bench_panel.setObjectName("sort_panel")
        bench_layout = QHBoxLayout(bench_panel)
        bench_layout.setSpacing(10)

        bench_layout.addWidget(QLabel("📊 Benchmark — Column:"))
        self.benchmark_column_combo = QComboBox()
        self.benchmark_column_combo.addItems(COLUMNS)
        bench_layout.addWidget(self.benchmark_column_combo)

        self.benchmark_btn = QPushButton("▶  Run Benchmark")
        self.benchmark_btn.clicked.connect(self.run_benchmark)
        bench_layout.addWidget(self.benchmark_btn)

        self.benchmark_status = QLabel("")
        self.benchmark_status.setObjectName("algo_info")
        bench_layout.addWidget(self.benchmark_status)

        bench_layout.addStretch()
        top_layout.addWidget(bench_panel)

        # Benchmark Table (Hidden initially)
        self.benchmark_table = QTableWidget()
        self.benchmark_table.setColumnCount(5)
        self.benchmark_table.setHorizontalHeaderLabels(
            ["Algorithm", "Time (ms)", "Comparisons", "Swaps", "Complexity / Stable"]
        )
        self.benchmark_table.setAlternatingRowColors(True)
        self.benchmark_table.verticalHeader().setDefaultSectionSize(28)
        self.benchmark_table.setShowGrid(False)
        self.benchmark_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.benchmark_table.setVisible(False)
        top_layout.addWidget(self.benchmark_table)

        # ==========================================
        # BOTTOM WIDGET (Main Table)
        # ==========================================
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setSortingEnabled(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setShowGrid(False)

        # ==========================================
        # THE SPLITTER (The Fix)
        # ==========================================
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(top_widget)
        self.splitter.addWidget(self.table)
        
        # THIS IS THE MAGIC LINE: 200px for top, 800px for table (80% of space!)
        self.splitter.setSizes([200, 800])
        
        main_layout.addWidget(self.splitter)

        # --- Initial load ---
        self.load_books()
        self.update_algo_info(self.algo_combo.currentText())

    # ----------------------------------------------------------------
    # DATA LOADING
    # ----------------------------------------------------------------
    def load_books(self):
        if not os.path.exists(DB_PATH):
            QMessageBox.critical(self, "Missing DB", f"books.db not found at:\n{DB_PATH}")
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
            self.filtered_data = list(self.raw_data)
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            return

        self.populate_table(self.filtered_data)
        self.update_count_label()

    def update_count_label(self):
        total = len(self.raw_data)
        current = len(self.filtered_data)
        if current == total:
            self.count_label.setText(f"Total: {total:,} books")
        else:
            self.count_label.setText(f"Showing: {current:,} of {total:,} books")

    def populate_table(self, rows):
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
    # SEARCHING
    # ----------------------------------------------------------------
    def run_search(self):
        col_index = self.search_col_combo.currentIndex()
        condition = self.search_cond_combo.currentText()
        query = self.search_input.text().strip()

        if not query:
            self.clear_search()
            return

        results = []
        query_lower = query.lower()

        for row in self.raw_data:
            val = row[col_index]
            if val is None:
                continue
                
            val_str = str(val).lower()
            
            match = False
            if condition == "Contains":
                match = query_lower in val_str
            elif condition == "Starts With":
                match = val_str.startswith(query_lower)
            elif condition == "Ends With":
                match = val_str.endswith(query_lower)
            elif condition == "Equals":
                match = val_str == query_lower
            elif condition == "Greater Than":
                try: match = float(val_str) > float(query_lower)
                except ValueError: match = val_str > query_lower
            elif condition == "Less Than":
                try: match = float(val_str) < float(query_lower)
                except ValueError: match = val_str < query_lower

            if match:
                results.append(row)

        self.filtered_data = results
        self.populate_table(self.filtered_data)
        self.update_count_label()

    def clear_search(self):
        self.search_input.clear()
        self.filtered_data = list(self.raw_data)
        self.populate_table(self.filtered_data)
        self.update_count_label()

    # ----------------------------------------------------------------
    # SORTING
    # ----------------------------------------------------------------
    def update_algo_info(self, algo_name):
        if algo_name not in ALL_SORTS:
            return
        sample = ALL_SORTS[algo_name]([], 0)
        stable_str = "Stable ✅" if sample.stable else "Not stable ❌"
        self.algo_info.setText(
            f"ℹ️  {sample.algorithm}  •  Time complexity: {sample.complexity}  •  {stable_str}"
        )

    def run_sort(self):
        col_index = self.column_combo.currentIndex()
        algo_name = self.algo_combo.currentText()
        algo_func = ALL_SORTS[algo_name]

        if self.scope_checkbox.isChecked():
            data_to_sort = self.filtered_data
        else:
            data_to_sort = self.raw_data

        if not data_to_sort:
            return

        self.sort_btn.setEnabled(False)
        self.sort_btn.setText("Sorting…")
        QApplication.processEvents()

        try:
            result = algo_func(data_to_sort, col_index)
        except Exception as e:
            QMessageBox.critical(self, "Sort Error", str(e))
            self.sort_btn.setEnabled(True)
            self.sort_btn.setText("🔀  Sort")
            return

        if self.scope_checkbox.isChecked():
            self.filtered_data = result.sorted_data
        else:
            self.raw_data = result.sorted_data
            self.filtered_data = list(self.raw_data)

        self.populate_table(self.filtered_data)

        self.time_label.setText(f"⏱ Time: {result.time_ms:.2f} ms")
        self.comparisons_label.setText(f"🔍 Comparisons: {result.comparisons:,}")
        self.swaps_label.setText(f"🔄 Swaps: {result.swaps:,}")

        self.sort_btn.setEnabled(True)
        self.sort_btn.setText("🔀  Sort")

    # ----------------------------------------------------------------
    # BENCHMARK
    # ----------------------------------------------------------------
    def run_benchmark(self):
        if self.benchmark_worker and self.benchmark_worker.isRunning():
            return

        if not self.raw_data:
            QMessageBox.warning(self, "No data", "Load data first.")
            return

        col_index = self.benchmark_column_combo.currentIndex()

        self.benchmark_table.setRowCount(0)
        self.benchmark_table.setVisible(True)
        self.benchmark_table.setMaximumHeight(200) # Keep it from eating the table space

        self.benchmark_btn.setEnabled(False)
        self.benchmark_btn.setText("Running…")
        self.sort_btn.setEnabled(False)

        self.benchmark_worker = BenchmarkWorker(self.raw_data, col_index)
        self.benchmark_worker.progress.connect(self.on_benchmark_progress)
        self.benchmark_worker.result.connect(self.on_benchmark_result)
        self.benchmark_worker.finished_all.connect(self.on_benchmark_finished)
        self.benchmark_worker.start()

    def on_benchmark_progress(self, current, total, algo_name):
        self.benchmark_status.setText(f"⏳ {algo_name}  ({current}/{total})…")

    def on_benchmark_result(self, row):
        r = self.benchmark_table.rowCount()
        self.benchmark_table.insertRow(r)

        stable_str = "✅ Stable" if row["stable"] else "❌ Not stable"

        values = [
            row["algorithm"],
            f"{row['time_ms']:.2f}" if row["time_ms"] >= 0 else "error",
            f"{row['comparisons']:,}" if row["comparisons"] >= 0 else "—",
            f"{row['swaps']:,}" if row["swaps"] >= 0 else "—",
            f"{row['complexity']}  •  {stable_str}",
        ]

        for c, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignCenter)
            self.benchmark_table.setItem(r, c, item)

    def on_benchmark_finished(self, results):
        self.benchmark_status.setText(f"✅ {len(results)} algorithms tested")
        self.benchmark_btn.setEnabled(True)
        self.benchmark_btn.setText("▶  Run Benchmark")
        self.sort_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()