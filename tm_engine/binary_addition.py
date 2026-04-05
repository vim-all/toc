from .tape import Tape

def binary_addition_tm(tape_input):

    if "+" not in tape_input:
        return "Invalid format (use number1+number2)"

    left, right = tape_input.split("+")

    # Validate binary input
    if not all(c in "01" for c in left + right):
        return "Input must contain only binary digits (0 and 1)"

    # Reverse for right-to-left processing (like TM head movement)
    left = left[::-1]
    right = right[::-1]

    carry = 0
    result = ""

    max_len = max(len(left), len(right))

    for i in range(max_len):

        bit1 = int(left[i]) if i < len(left) else 0
        bit2 = int(right[i]) if i < len(right) else 0

        total = bit1 + bit2 + carry

        result += str(total % 2)
        carry = total // 2

    if carry:
        result += "1"

    return result[::-1]


def binary_addition_tm_steps(tape_input):
    """
    Simulated Turing Machine binary addition
    with step-by-step execution trace.

    Returns:
        list of computation steps
    """

    if "+" not in tape_input:
        return ["Invalid format (use number1+number2)"]

    left, right = tape_input.split("+")

    if not all(c in "01" for c in left + right):
        return ["Input must contain only binary digits (0 and 1)"]

    left_rev = left[::-1]
    right_rev = right[::-1]

    carry = 0
    result = ""
    steps = []

    max_len = max(len(left_rev), len(right_rev))

    steps.append(f"Initial Tape: {left}+{right}")

    for i in range(max_len):

        bit1 = int(left_rev[i]) if i < len(left_rev) else 0
        bit2 = int(right_rev[i]) if i < len(right_rev) else 0

        total = bit1 + bit2 + carry

        result += str(total % 2)
        carry = total // 2

        steps.append(
            f"Step {i+1}: Read {bit1} and {bit2}, Carry = {carry}, Partial Result = {result[::-1]}"
        )

    if carry:
        result += "1"
        steps.append(f"Final Carry Added → Result = {result[::-1]}")

    steps.append(f"Final Output Tape: {result[::-1]}")

    return steps


def create_binary_addition_machine(input_string, debug=False):
    """Create a stepwise binary addition machine adapter.

    The machine writes one result bit per `step()` starting from the
    least-significant bit and records history entries like the
    `TuringMachine`-based palindrome machine.
    """

    class BinaryAdditionMachine:

        def __init__(self, inp, debug=False):
            self.raw_input = inp
            self.is_binary_addition = True
            self.debug = bool(debug)
            self.current_state = 'start'
            self.accept_state = 'q_accept'
            self.reject_state = 'q_reject'
            self.step_count = 0
            self.history = []
            self.last_action = None

            # parse and validate
            if '+' not in inp:
                self.invalid = 'Invalid format (use number1+number2)'
                self.left = ''
                self.right = ''
            else:
                self.invalid = None
                self.left, self.right = inp.split('+')

            if self.invalid is None and not all(c in '01' for c in (self.left + self.right)):
                self.invalid = 'Input must contain only binary digits (0 and 1)'

            # prepare for stepwise addition
            self.left_rev = (self.left or '')[::-1]
            self.right_rev = (self.right or '')[::-1]
            self.max_len = max(len(self.left_rev), len(self.right_rev))
            self.i = 0
            self.carry = 0
            self.result_bits = []

            # Build tape: show input then reserve space for result after a blank
            # layout: [_] left + '+' + right + ['_'] + result_space + [_]
            result_space = self.max_len + 2
            self.tape = Tape(self.left + '+' + self.right)
            # append blanks for result area
            self.tape.tape = self.tape.tape + [self.tape.blank] * result_space
            # result starts AFTER right operand and the existing separator blank
            self.result_start = len(self.left) + len(self.right) + 3
            self.write_index = 0

        def set_debug(self, enabled: bool):
            self.debug = bool(enabled)

        def step(self):
            # record before
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

            if self.invalid:
                self.current_state = self.reject_state
                self.last_action = f'reject: {self.invalid}'
                self.history[-1].update({'after_state': self.current_state, 'after_head': self.tape.head, 'tape': ''.join(self.tape.get_tape())})
                self.step_count += 1
                return

            if self.current_state in (self.accept_state, self.reject_state):
                return

            # if still bits to process
            if self.i < self.max_len:
                self.current_state = 'q_add'
                bit1 = int(self.left_rev[self.i]) if self.i < len(self.left_rev) else 0
                bit2 = int(self.right_rev[self.i]) if self.i < len(self.right_rev) else 0
                carry_in = self.carry
                total = bit1 + bit2 + carry_in
                out_bit = str(total % 2)
                self.carry = total // 2

                # append to result_bits (LSB first)
                self.result_bits.append(out_bit)
                self.write_index += 1
                self.i += 1

                # rewrite the displayed result area in MSB-first order so users see a human-readable partial result
                partial = ''.join(reversed(self.result_bits))
                for idx, ch in enumerate(partial):
                    pos = self.result_start + idx
                    if pos >= len(self.tape.tape):
                        self.tape.tape.extend([self.tape.blank] * (pos - len(self.tape.tape) + 1))
                    self.tape.tape[pos] = ch

                # move head to the last written result digit for visibility
                self.tape.head = self.result_start + len(partial) - 1
                step_no = self.i
                self.last_action = (
                    f'step {step_no}: {bit1}+{bit2}+carry({carry_in})='
                    f'{total} -> write {out_bit}, carry={self.carry}, partial={partial}'
                )

            else:
                # no more aligned bits; handle final carry
                if self.carry:
                    self.current_state = 'q_carry'
                    # append carry as LSB and then rewrite display
                    self.result_bits.append(str(self.carry))
                    self.write_index += 1
                    self.carry = 0

                    partial = ''.join(reversed(self.result_bits))
                    for idx, ch in enumerate(partial):
                        pos = self.result_start + idx
                        if pos >= len(self.tape.tape):
                            self.tape.tape.extend([self.tape.blank] * (pos - len(self.tape.tape) + 1))
                        self.tape.tape[pos] = ch
                    self.tape.head = self.result_start + len(partial) - 1
                    self.last_action = f'final carry step: append 1 -> partial={partial}'
                else:
                    # finished - convert LSB-first result_bits into MSB-first on tape
                    self.current_state = self.accept_state
                    # build final result left-to-right
                    final_result = ''.join(reversed(self.result_bits))
                    # write final result starting at result_start
                    for idx, ch in enumerate(final_result):
                        pos = self.result_start + idx
                        if pos >= len(self.tape.tape):
                            self.tape.tape.extend([self.tape.blank] * (pos - len(self.tape.tape) + 1))
                        self.tape.tape[pos] = ch
                    # set head to start of result (or leave where it was)
                    if len(final_result) > 0:
                        self.tape.head = self.result_start
                    self.last_action = f'accept -> result={final_result}'

            # update after in history
            self.history[-1].update({'after_state': self.current_state, 'after_head': self.tape.head, 'tape': ''.join(self.tape.get_tape())})
            self.step_count += 1

        def get_history(self):
            return list(self.history)

    return BinaryAdditionMachine(input_string, debug=debug)