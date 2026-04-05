from .tape import Tape


def create_unary_multiplication_machine(input_string, debug=False):
    """Adapter that exposes a machine-like object for unary multiplication.

    Expected input format: a string containing two unary numbers separated
    by `*`, e.g. `111*1111` (meaning 3 * 4). The adapter writes the
    result (a*b ones) onto the tape incrementally on `step()` calls and
    then enters the accept state.
    """

    class UnaryMultiplicationMachine:

        def __init__(self, inp, debug=False):
            self.raw_input = inp
            self.debug = bool(debug)
            # parse input
            if "*" in inp:
                parts = inp.split("*")
            else:
                parts = [inp, ""]

            left, right = parts[0], parts[1]
            # lengths of unary numbers
            try:
                if left == "":
                    a = 0
                else:
                    a = len(left)
                if right == "":
                    b = 0
                else:
                    b = len(right)
            except Exception:
                a = 0
                b = 0

            self.a = a
            self.b = b
            self.result_len = a * b

            # create a Tape with blanks around; we'll write result starting at index 1
            self.tape = Tape("")
            # initialize tape with blanks and space for result
            self.tape.tape = [self.tape.blank] + [self.tape.blank] * (self.result_len + 2) + [self.tape.blank]
            self.tape.head = 1

            self.current_state = 'q0'
            self.accept_state = 'q_accept'
            self.reject_state = 'q_reject'

            self.step_count = 0
            self.history = []
            self.last_action = None
            self.write_index = 0

        def set_debug(self, enabled: bool):
            self.debug = bool(enabled)

        def step(self):
            if self.current_state in (self.accept_state, self.reject_state):
                return

            before_state = self.current_state
            before_head = self.tape.head
            self.history.append({
                'before_state': before_state,
                'before_head': before_head,
                'read_symbol': ''.join(self.tape.get_tape()),
                'transition': None,
                'after_state': None,
                'after_head': None,
                'tape': ''.join(self.tape.get_tape()),
            })

            # if invalid input (non '1' characters other than '*') -> reject
            if any(c not in ('1', '*') for c in self.raw_input):
                self.current_state = self.reject_state
                self.last_action = 'reject: invalid chars'
                self.history[-1].update({'after_state': self.current_state, 'after_head': self.tape.head, 'tape': ''.join(self.tape.get_tape())})
                self.step_count += 1
                return

            # write one '1' per step until result_len reached
            if self.write_index < self.result_len:
                # write at current write index
                self.tape.tape[self.write_index + 1] = '1'
                self.tape.head = self.write_index + 1
                self.last_action = f'write 1 at {self.tape.head}'
                self.write_index += 1
            else:
                self.current_state = self.accept_state
                self.last_action = 'accept'

            # record after
            self.history[-1].update({'after_state': self.current_state, 'after_head': self.tape.head, 'tape': ''.join(self.tape.get_tape())})
            self.step_count += 1

        def get_history(self):
            return list(self.history)

    return UnaryMultiplicationMachine(input_string, debug=debug)
