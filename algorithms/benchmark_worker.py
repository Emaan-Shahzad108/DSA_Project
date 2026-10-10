from PyQt5.QtCore import QThread, pyqtSignal
from algorithms.sorting import ALL_SORTS


class BenchmarkWorker(QThread):
    progress = pyqtSignal(int, int, str)
    result = pyqtSignal(dict)
    finished_all = pyqtSignal(list)

    def __init__(self, data, col_index):
        super().__init__()
        self.data = data
        self.col_index = col_index
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        results = []
        algo_names = list(ALL_SORTS.keys())
        total = len(algo_names)

        for i, name in enumerate(algo_names):
            if self._cancel:
                break

            self.progress.emit(i + 1, total, name)

            try:
                sort_result = ALL_SORTS[name](self.data, self.col_index)
                row = {
                    "algorithm": sort_result.algorithm,
                    "time_ms": sort_result.time_ms,
                    "comparisons": sort_result.comparisons,
                    "swaps": sort_result.swaps,
                    "complexity": sort_result.complexity,
                    "stable": sort_result.stable,
                }
            except Exception as e:
                row = {
                    "algorithm": name,
                    "time_ms": -1,
                    "comparisons": -1,
                    "swaps": -1,
                    "complexity": "Error",
                    "stable": False,
                    "error": str(e),
                }

            results.append(row)
            self.result.emit(row)

        results.sort(key=lambda r: r["time_ms"])
        self.finished_all.emit(results)