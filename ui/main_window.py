import os
import sys
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QHeaderView, QMessageBox, QComboBox, QFrame,
    QLineEdit, QCheckBox
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
    color: #00d4aa; font-size: 20px; font-weight: bold; padding: 4px;
}
QLabel#count_label {
    color: #a0a0b0; font-size: 13px; padding: 4px;
}
QLabel#metrics_label {
    color: #e0e0e0; font-size: 12px; padding: 4px 8px;
    background-color: #252535; border-radius: 4px;
}
QLabel#algo_info {
    color: #00d4aa; font-size: 11px; font-style: italic; padding: 2px;
}
QFrame#sort_panel {
    background-color: #252535; border-radius: 6px; padding: 6px;
}
QComboBox, QLineEdit {
    background-color: #2d2d44; color: #e0e0e0;
    border: 1px solid #33334d; border-radius: 4px;
    padding: 4px 8px; font-size: 12px; min-width: 90px;
}
QComboBox:hover, QLineEdit:hover { border: 1px solid #00d4aa; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #2d2d44; color: #e0e0e0;
    selection-background-color: #00d4aa;
    selection-color: #1e1e2e;
    border: 1px solid #33334d;
}
QCheckBox { color: #e0e0e0; font-size: 11px; padding: 2px; }
QCheckBox::indicator { width: 14px; height: 14px; }
QPushButton {
    background-color: #00d4aa; color: #1e1e2e;
    border: none; padding: 4px 10px;
    border-radius: 4px; font-size: 12px; font-weight: bold;
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
    padding: 8px; border: none;
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
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSA Project - Books Database")
        self.resize(1500, 950)
        self.setStyleSheet(STYLESHEET)

        self.raw_data = []
        self.filtered_data = []
        self.benchmark_worker = None

        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # ==========================================
        # TOP WIDGET (Compressed Controls)
        # ==========================================
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4) # Extremely tight spacing

        # 1. Top bar
        top_bar = QHBoxLayout()
        self.title_label = QLabel("📚 Books Database")
        self.title_label.setObjectName("title_label")
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        self.count_label = QLabel("Total: 0")
        self.count_label.setObjectName("count_label")
        top_bar.addWidget(self.count_label)
        top_layout.addLayout(top_bar)

        # 2. Search Panel
        search_panel = QFrame()
        search_panel.setObjectName("sort_panel")
        search_layout = QHBoxLayout(search_panel)
        search_layout.setSpacing(6)
        search_layout.setContentsMargins(6, 6, 6, 6)

        search_layout.addWidget(QLabel("🔍 Search:"))
        self.search_col_combo = QComboBox()
        self.search_col_combo.addItems(COLUMNS)
        search_layout.addWidget(self.search_col_combo)

        self.search_cond_combo = QComboBox()
        self.search_cond_combo.addItems(["Contains", "Starts With", "Ends With", "Equals", "Greater Than", "Less Than"])
        search_layout.addWidget(self.search_cond_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type query…")
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

        # 3. Multi-Level Sort Panel
        sort_panel = QFrame()
        sort_panel.setObjectName("sort_panel")
        sort_layout = QVBoxLayout(sort_panel)
        sort_layout.setSpacing(4)
        sort_layout.setContentsMargins(6, 6, 6, 6)

        sort_row1 = QHBoxLayout()
        sort_row1.addWidget(QLabel("Primary:"))
        self.column_combo = QComboBox()
        self.column_combo.addItems(COLUMNS)
        sort_row1.addWidget(self.column_combo)
        
        sort_row1.addWidget(QLabel("Algorithm:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(list(ALL_SORTS.keys()))
        self.algo_combo.currentTextChanged.connect(self.update_algo_info)
        sort_row1.addWidget(self.algo_combo)
        
        self.sort_btn = QPushButton("🔀  Sort")
        self.sort_btn.clicked.connect(self.run_sort)
        sort_row1.addWidget(self.sort_btn)
        
        self.scope_checkbox = QCheckBox("Sort only filtered")
        sort_row1.addWidget(self.scope_checkbox)
        sort_row1.addStretch()
        sort_layout.addLayout(sort_row1)

        sort_row2 = QHBoxLayout()
        sort_row2.addWidget(QLabel("Secondary:"))
        self.column_combo_2 = QComboBox()
        self.column_combo_2.addItems(["- None -"] + COLUMNS)
        sort_row2.addWidget(self.column_combo_2)

        sort_row2.addWidget(QLabel("Tertiary:"))
        self.column_combo_3 = QComboBox()
        self.column_combo_3.addItems(["- None -"] + COLUMNS)
        sort_row2.addWidget(self.column_combo_3)
        sort_row2.addStretch()
        sort_layout.addLayout(sort_row2)
        top_layout.addWidget(sort_panel)

        # 4. Metrics & Benchmark Panel
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

        bench_panel = QFrame()
        bench_panel.setObjectName("sort_panel")
        bench_layout = QHBoxLayout(bench_panel)
        bench_layout.setSpacing(6)
        bench_layout.setContentsMargins(6, 6, 6, 6)
        
        bench_layout.addWidget(QLabel("📊 Benchmark:"))
        self.benchmark_column_combo = QComboBox()
        self.benchmark_column_combo.addItems(COLUMNS)
        bench_layout.addWidget(self.benchmark_column_combo)
        
        self.benchmark_btn = QPushButton("▶  Run")
        self.benchmark_btn.clicked.connect(self.run_benchmark)
        bench_layout.addWidget(self.benchmark_btn)
        
        self.benchmark_status = QLabel("")
        self.benchmark_status.setObjectName("algo_info")
        bench_layout.addWidget(self.benchmark_status)
        bench_layout.addStretch()
        top_layout.addWidget(bench_panel)

        # Hidden Benchmark Table
        self.benchmark_table = QTableWidget()
        self.benchmark_table.setColumnCount(5)
        self.benchmark_table.setHorizontalHeaderLabels(["Algorithm", "Time", "Comparisons", "Swaps", "Complexity"])
        self.benchmark_table.setAlternatingRowColors(True)
        self.benchmark_table.verticalHeader().setDefaultSectionSize(24)
        self.benchmark_table.setShowGrid(False)
        self.benchmark_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.benchmark_table.setVisible(False)
        top_layout.addWidget(self.benchmark_table)

        # THIS IS THE ABSOLUTE FIX: Lock the top half to exactly 230 pixels
        top_widget.setFixedHeight(230)
        
        # Add top widget to main layout without stretch
        main_layout.addWidget(top_widget, 0)

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

        # THIS IS THE ABSOLUTE FIX: Stretch=1 gives this table 100% of the remaining space!
        main_layout.addWidget(self.table, 1)

        # --- Initial load ---
        self.load_books()
        self.update_algo_info(self.algo_combo.currentText())

    # ----------------------------------------------------------------
    # DATA LOADING & POPULATION
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
            if val is None: continue
            val_str = str(val).lower()
            
            match = False
            if condition == "Contains": match = query_lower in val_str
            elif condition == "Starts With": match = val_str.startswith(query_lower)
            elif condition == "Ends With": match = val_str.endswith(query_lower)
            elif condition == "Equals": match = val_str == query_lower
            elif condition == "Greater Than":
                try: match = float(val_str) > float(query_lower)
                except ValueError: match = val_str > query_lower
            elif condition == "Less Than":
                try: match = float(val_str) < float(query_lower)
                except ValueError: match = val_str < query_lower

            if match: results.append(row)

        self.filtered_data = results
        self.populate_table(self.filtered_data)
        self.update_count_label()

    def clear_search(self):
        self.search_input.clear()
        self.filtered_data = list(self.raw_data)
        self.populate_table(self.filtered_data)
        self.update_count_label()

    # ----------------------------------------------------------------
    # MULTI-LEVEL SORTING
    # ----------------------------------------------------------------
    def update_algo_info(self, algo_name):
        if algo_name not in ALL_SORTS: return
        sample = ALL_SORTS[algo_name]([], 0)
        stable_str = "Stable ✅" if sample.stable else "Not stable ❌"
        self.algo_info.setText(f"ℹ️ {sample.algorithm} • {sample.complexity} • {stable_str}")

    def run_sort(self):
        primary_index = self.column_combo.currentIndex()
        secondary_text = self.column_combo_2.currentText()
        tertiary_text = self.column_combo_3.currentText()
        algo_name = self.algo_combo.currentText()
        algo_func = ALL_SORTS[algo_name]

        data = list(self.filtered_data) if self.scope_checkbox.isChecked() else list(self.raw_data)
        if not data: return

        self.sort_btn.setEnabled(False)
        self.sort_btn.setText("Sorting…")
        QApplication.processEvents()

        try:
            if tertiary_text != "- None -":
                data = algo_func(data, COLUMNS.index(tertiary_text)).sorted_data
            if secondary_text != "- None -":
                data = algo_func(data, COLUMNS.index(secondary_text)).sorted_data
            final_result = algo_func(data, primary_index)
            sorted_data = final_result.sorted_data
        except Exception as e:
            QMessageBox.critical(self, "Sort Error", str(e))
            self.sort_btn.setEnabled(True)
            self.sort_btn.setText("🔀  Sort")
            return

        if self.scope_checkbox.isChecked():
            self.filtered_data = sorted_data
        else:
            self.raw_data = sorted_data
            self.filtered_data = list(self.raw_data)

        self.populate_table(self.filtered_data)
        self.time_label.setText(f"⏱ Time: {final_result.time_ms:.2f} ms")
        self.comparisons_label.setText(f"🔍 Comp: {final_result.comparisons:,}")
        self.swaps_label.setText(f"🔄 Swaps: {final_result.swaps:,}")
        self.sort_btn.setEnabled(True)
        self.sort_btn.setText("🔀  Sort")

    # ----------------------------------------------------------------
    # BENCHMARK
    # ----------------------------------------------------------------
    def run_benchmark(self):
        if self.benchmark_worker and self.benchmark_worker.isRunning(): return
        if not self.raw_data: return

        col_index = self.benchmark_column_combo.currentIndex()
        self.benchmark_table.setRowCount(0)
        self.benchmark_table.setVisible(True)
        self.benchmark_table.setMaximumHeight(150) # Limits benchmark table height

        self.benchmark_btn.setEnabled(False)
        self.benchmark_btn.setText("Running…")
        self.sort_btn.setEnabled(False)

        self.benchmark_worker = BenchmarkWorker(self.raw_data, col_index)
        self.benchmark_worker.progress.connect(self.on_benchmark_progress)
        self.benchmark_worker.result.connect(self.on_benchmark_result)
        self.benchmark_worker.finished_all.connect(self.on_benchmark_finished)
        self.benchmark_worker.start()

    def on_benchmark_progress(self, current, total, algo_name):
        self.benchmark_status.setText(f"⏳ {algo_name} ({current}/{total})…")

    def on_benchmark_result(self, row):
        r = self.benchmark_table.rowCount()
        self.benchmark_table.insertRow(r)
        stable_str = "✅" if row["stable"] else "❌"
        values = [
            row["algorithm"],
            f"{row['time_ms']:.1f}" if row["time_ms"] >= 0 else "err",
            f"{row['comparisons']:,}" if row["comparisons"] >= 0 else "—",
            f"{row['swaps']:,}" if row["swaps"] >= 0 else "—",
            f"{row['complexity']} • {stable_str}",
        ]
        for c, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignCenter)
            self.benchmark_table.setItem(r, c, item)

    def on_benchmark_finished(self, results):
        self.benchmark_status.setText(f"✅ {len(results)} algorithms tested")
        self.benchmark_btn.setEnabled(True)
        self.benchmark_btn.setText("▶  Run")
        self.sort_btn.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()