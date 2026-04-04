import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from controller.simulator_controller import SimulatorController


app = QApplication(sys.argv)

window = MainWindow()

controller = SimulatorController(window)

window.show()

app.exec()