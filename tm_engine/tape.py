class Tape:

    def __init__(self, input_string):
        self.blank = "_"
        # place a blank at both ends so head can move left/right safely
        self.tape = [self.blank] + list(input_string) + [self.blank]
        # start head on the first input symbol (index 1)
        self.head = 1

    def read(self):
        if self.head >= len(self.tape):
            self.tape.append(self.blank)
        return self.tape[self.head]

    def write(self, symbol):
        if self.head >= len(self.tape):
            self.tape.append(self.blank)
        self.tape[self.head] = symbol

    def move_right(self):
        self.head += 1

    def move_left(self):
        if self.head > 0:
            self.head -= 1

    def get_tape(self):
        return self.tape