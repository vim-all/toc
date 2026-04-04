from .turing_machine import TuringMachine
from .tape import Tape


def create_palindrome_machine(input_string, debug=False):

    tape = Tape(input_string)

    transitions = {
        # start: mark leftmost unmarked symbol and choose matching routine
        ("q0", "0"): ("q1", "X", "R"),
        ("q0", "1"): ("q2", "X", "R"),
        ("q0", "X"): ("q0", "X", "R"),
        ("q0", "_"): ("q_accept", "_", "R"),

        # scan right to the blank
        ("q1", "0"): ("q1", "0", "R"),
        ("q1", "1"): ("q1", "1", "R"),
        ("q1", "X"): ("q1", "X", "R"),
        ("q1", "_"): ("q3", "_", "L"),

        # q3: looking for matching 0 from the right
        ("q3", "0"): ("q4", "X", "L"),
        ("q3", "1"): ("q_reject", "1", "R"),
        ("q3", "X"): ("q3", "X", "L"),
        ("q3", "_"): ("q_accept", "_", "R"),

        # symmetric: scanned initial 1
        ("q2", "0"): ("q2", "0", "R"),
        ("q2", "1"): ("q2", "1", "R"),
        ("q2", "X"): ("q2", "X", "R"),
        ("q2", "_"): ("q5", "_", "L"),

        # q5: looking for matching 1 from the right
        ("q5", "1"): ("q4", "X", "L"),
        ("q5", "0"): ("q_reject", "0", "R"),
        ("q5", "X"): ("q5", "X", "L"),
        ("q5", "_"): ("q_accept", "_", "R"),

        # q4: return left to the leftmost blank, then continue
        ("q4", "0"): ("q4", "0", "L"),
        ("q4", "1"): ("q4", "1", "L"),
        ("q4", "X"): ("q4", "X", "L"),
        ("q4", "_"): ("q0", "_", "R"),
    }

    tm = TuringMachine(
        tape,
        transitions,
        "q0",
        "q_accept",
        "q_reject"
    )
    if debug:
        tm.set_debug(True)
    return tm