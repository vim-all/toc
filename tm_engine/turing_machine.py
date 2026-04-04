class TuringMachine:

    def __init__(self, tape, transitions, start_state, accept_state, reject_state):

        self.tape = tape
        self.transitions = transitions

        self.current_state = start_state
        self.accept_state = accept_state
        self.reject_state = reject_state

        # debug flag and step counter for CDEBUG logging
        self.debug = False
        self.step_count = 0
        self.history = []
        self.last_transition = None
        self.last_action = None

    def set_debug(self, enabled: bool):
        self.debug = bool(enabled)

    def step(self):
        # Read current symbol and build lookup key
        before_state = self.current_state
        before_head = self.tape.head
        symbol = self.tape.read()
        key = (before_state, symbol)

        # CDEBUG: before step
        if self.debug:
            print(f"CDEBUG: step={self.step_count} state={before_state} head={before_head} sym={symbol} tape={''.join(self.tape.get_tape())}")

        if key not in self.transitions:
            if self.debug:
                print(f"CDEBUG: step={self.step_count} NO_TRANSITION for key={key} -> setting state={self.reject_state}")
            # set reject and record history entry
            self.current_state = self.reject_state
            self.last_transition = None
            self.last_action = f"NO_TRANSITION for key={key} -> {self.reject_state}"
            self.history.append({
                'before_state': before_state,
                'before_head': before_head,
                'read_symbol': symbol,
                'transition': None,
                'after_state': self.current_state,
                'after_head': self.tape.head,
                'tape': ''.join(self.tape.get_tape()),
            })
            self.step_count += 1
            return

        new_state, write_symbol, move = self.transitions[key]
        # record last transition tuple for UI/logging
        self.last_transition = (before_state, symbol, new_state, write_symbol, move)
        self.last_action = f"{before_state},{symbol} -> {new_state},{write_symbol},{move}"

        if self.debug:
            print(f"CDEBUG: step={self.step_count} TRANSITION {key} -> (state={new_state}, write={write_symbol}, move={move})")

        self.tape.write(write_symbol)

        if move == "R":
            self.tape.move_right()
        elif move == "L":
            self.tape.move_left()

        self.current_state = new_state
        # record history entry with after-state/tape
        self.history.append({
            'before_state': before_state,
            'before_head': before_head,
            'read_symbol': symbol,
            'transition': (before_state, symbol, new_state, write_symbol, move),
            'after_state': self.current_state,
            'after_head': self.tape.head,
            'tape': ''.join(self.tape.get_tape()),
        })

        if self.debug:
            # show after state
            cur_sym = self.tape.read()
            print(f"CDEBUG: step={self.step_count} AFTER state={self.current_state} head={self.tape.head} sym={cur_sym} tape={''.join(self.tape.get_tape())}")

        self.step_count += 1

    def get_history(self):
        return list(self.history)