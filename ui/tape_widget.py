from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel


class TapeWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.cells = []

    def update_tape(self, tape, head):

        # clear old cells
        for cell in self.cells:
            self.layout.removeWidget(cell)
            cell.deleteLater()

        self.cells = []

        for i, symbol in enumerate(tape):

            label = QLabel(symbol)
            label.setFixedSize(40,40)
            # color code common symbols
            base_style = "border:1px solid white; font-size:18px; text-align:center;"
            if symbol == 'X':
                label.setStyleSheet(base_style + " background-color: yellow; color: black;")
            elif symbol == '_':
                label.setStyleSheet(base_style + " background-color: #333333; color: #bbbbbb;")
            else:
                label.setStyleSheet(base_style)

            if i == head:
                # emphasize head
                label.setStyleSheet(label.styleSheet() + " border:2px solid black;")

            self.layout.addWidget(label)
            self.cells.append(label)