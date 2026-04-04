from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QSlider,
    QCheckBox,
    QFileDialog,
)
from ui.tape_widget import TapeWidget


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Turing Machine Simulator")

        layout = QVBoxLayout()

        self.input_box = QLineEdit()
        layout.addWidget(self.input_box)

        # control row: Start / Play-Pause / Next Step
        controls = QHBoxLayout()
        self.start_button = QPushButton("Start")
        controls.addWidget(self.start_button)

        self.play_button = QPushButton("Play")
        controls.addWidget(self.play_button)

        self.step_button = QPushButton("Next Step")
        controls.addWidget(self.step_button)

        layout.addLayout(controls)

        # second row: speed, debug toggle, export log
        controls2 = QHBoxLayout()
        self.speed_slider = QSlider()
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(2000)
        self.speed_slider.setValue(300)
        controls2.addWidget(QLabel("Speed"))
        controls2.addWidget(self.speed_slider)

        self.debug_checkbox = QCheckBox("Console Debug")
        controls2.addWidget(self.debug_checkbox)

        self.export_button = QPushButton("Export Log")
        controls2.addWidget(self.export_button)

        # auto-save detailed narrated log on completion
        self.auto_save_checkbox = QCheckBox("Auto-save Detailed Log")
        controls2.addWidget(self.auto_save_checkbox)

        layout.addLayout(controls2)

        self.tape_label = QLabel("Tape")
        layout.addWidget(self.tape_label)

        self.state_label = QLabel("State")
        layout.addWidget(self.state_label)

        self.step_label = QLabel("Step: 0")
        layout.addWidget(self.step_label)

        self.transition_label = QLabel("Last transition: -")
        layout.addWidget(self.transition_label)

        self.tape_widget = TapeWidget()
        layout.addWidget(self.tape_widget)
        
        self.setLayout(layout)