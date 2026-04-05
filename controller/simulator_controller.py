from tm_engine.palindrome_machine import create_palindrome_machine
from tm_engine.binary_addition import create_binary_addition_machine
from tm_engine.unary_multiplication import create_unary_multiplication_machine
from PyQt6.QtCore import QTimer
import datetime
import os


class SimulatorController:

    def __init__(self, window):

        self.window = window
        self.machine = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._auto_step)
        self.log_file = None

        window.start_button.clicked.connect(self.start)
        window.step_button.clicked.connect(self.step)
        window.play_button.clicked.connect(self.toggle_play)
        window.speed_slider.valueChanged.connect(self._update_timer_interval)
        window.debug_checkbox.stateChanged.connect(self._update_debug)
        window.export_button.clicked.connect(self._export_log)

    def start(self):

        input_string = self.window.input_box.text()

        print(f"GUI: Starting machine for input='{input_string}'")
        # enable debug if checkbox is checked
        debug = bool(self.window.debug_checkbox.isChecked())
        # select machine based on UI selector
        try:
            op = self.window.operation_selector.currentText()
        except Exception:
            op = 'Palindrome'

        if op == 'Binary Addition':
            # binary addition expects input like "a+b"
            self.machine = create_binary_addition_machine(input_string, debug=debug)
        elif op == 'Unary Multiplication':
            # unary multiplication expects input like "111*11"
            self.machine = create_unary_multiplication_machine(input_string, debug=debug)
        else:
            self.machine = create_palindrome_machine(input_string, debug=debug)

        # open a timestamped log file to record the run
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        logname = f"run_{input_string or 'empty'}_{ts}.log"
        self.log_file = open(logname, 'w')
        self._log(f"RUN START input={input_string} debug={debug} log={logname}\n")

        # set timer interval from slider
        self._update_timer_interval()

        # show initial display/log
        self.update_display()

    # Explanations for states (more formal/complete 'why' text)
    STATE_EXPLANATIONS = {
        'q0': "Start state: scan from leftmost unmarked symbol; mark it with 'X' and choose the routine to match it from the right. This ensures we process outermost pairs first.",
        'q1': "Scanning right after marking a left '0': move right past symbols and X's until the blank to reach the rightmost candidate.",
        'q2': "Scanning right after marking a left '1': move right past symbols and X's until the blank to reach the rightmost candidate.",
        'q3': "Searching left for a '0' to match the left '0'. Skip any X markers encountered; if a '0' is found, mark it and return left.",
        'q5': "Searching left for a '1' to match the left '1'. Skip any X markers encountered; if a '1' is found, mark it and return left.",
        'q4': "Returning left to the tape's left area: move left over symbols and X markers until the left blank, then resume at q0 to process the next outermost pair.",
        'q_accept': "Accepting state: all symbols have been matched and marked; the input is a palindrome.",
        'q_reject': "Rejecting state: a required matching symbol was not found or an unexpected symbol was encountered; the input is not a palindrome.",
    }

    def step(self):

        if not self.machine:
            print("GUI: no machine — press Start first")
            return

        # prevent stepping once machine has halted
        if self.machine.current_state in (self.machine.accept_state, self.machine.reject_state):
            msg = f"GUI: machine already halted in state={self.machine.current_state} — ignoring step"
            print(msg)
            if self.log_file:
                self._log(msg + "\n")
            return

        # execute one step and log
        self.machine.step()
        self._after_step()

    def update_display(self):
        # get raw tape and then trim leading/trailing blanks for a cleaner display
        raw_tape = self.machine.tape.get_tape()
        blank = getattr(self.machine.tape, 'blank', '_')

        # find first/last non-blank
        first = 0
        last = len(raw_tape) - 1
        while first < len(raw_tape) and raw_tape[first] == blank:
            first += 1
        while last >= 0 and raw_tape[last] == blank:
            last -= 1

        if first > last:
            # nothing but blanks: show a single blank cell
            display_tape = [blank]
            display_head = self.machine.tape.head
            display_start = 0
        else:
            # include one blank of context on each side when possible
            start = max(0, first - 1)
            end = min(len(raw_tape) - 1, last + 1)
            display_tape = raw_tape[start:end + 1]
            display_start = start
            display_head = self.machine.tape.head - start

        # update UI with trimmed tape
        if getattr(self.machine, 'is_binary_addition', False):
            left = getattr(self.machine, 'left', '')
            right = getattr(self.machine, 'right', '')
            partial = ''.join(reversed(getattr(self.machine, 'result_bits', [])))
            if partial == '':
                partial = '-'
            phase = 'Final Output' if self.machine.current_state == self.machine.accept_state else 'Partial Output'
            pretty = f"Input: {left} + {right}\n{phase}: {partial}"
            self.window.tape_label.setText(pretty)
        else:
            self.window.tape_label.setText(" ".join(display_tape))
        self.window.state_label.setText(self.machine.current_state)
        self.window.tape_widget.update_tape(
            display_tape,
            display_head
        )
        # print a concise GUI log line for each display update
        try:
            step = self.machine.step_count
        except Exception:
            step = '?'
        msg = f"GUI_LOG: step={step} state={self.machine.current_state} head={self.machine.tape.head} tape={''.join(display_tape)}"
        print(msg)
        if self.log_file:
            self._log(msg + "\n")

        # update extra labels
        self.window.step_label.setText(f"Step: {step}")
        last = getattr(self.machine, 'last_action', '-')
        self.window.transition_label.setText(f"Last transition: {last}")
        if self.log_file:
            self._log(f"Last transition: {last}\n")

        # when halted, auto-stop timer
        if self.machine.current_state in (self.machine.accept_state, self.machine.reject_state):
            final = f"RUN END state={self.machine.current_state} steps={step}\n"
            print(final)
            if self.log_file:
                self._log(final)
                self.log_file.flush()

            # if auto-save detailed log is enabled, create detailed text and HTML timeline
            try:
                if self.window.auto_save_checkbox.isChecked():
                    txt, html = self._build_detailed_and_html()
                    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    base = f"detailed_{(self.window.input_box.text() or 'empty')}_{ts}"
                    txtname = base + '.txt'
                    htmlname = base + '.html'
                    with open(txtname, 'w') as f:
                        f.write(txt)
                    with open(htmlname, 'w') as f:
                        f.write(html)
                    msg = f"GUI: saved detailed logs: {os.path.abspath(txtname)}, {os.path.abspath(htmlname)}"
                    print(msg)
                    if self.log_file:
                        self._log(msg + "\n")
            except Exception as e:
                print('GUI: failed to auto-save detailed logs', e)

    def _after_step(self):
        # helper called after each step to update UI and logs
        step = getattr(self.machine, 'step_count', '?')
        last = getattr(self.machine, 'last_action', '-')
        print(f"STEP_LOG: {step} {last} tape={''.join(self.machine.tape.get_tape())}")
        if self.log_file:
            self._log(f"STEP_LOG: {step} {last} tape={''.join(self.machine.tape.get_tape())}\n")
        self.update_display()

    def toggle_play(self):
        if not self.machine:
            print("GUI: no machine — press Start first")
            return
        if self.timer.isActive():
            self.timer.stop()
            self.window.play_button.setText('Play')
            print('GUI: Auto-run paused')
        else:
            # if already halted, don't start
            if self.machine.current_state in (self.machine.accept_state, self.machine.reject_state):
                print('GUI: machine already halted — cannot Play')
                return
            ms = max(1, int(self.window.speed_slider.value()))
            self.timer.start(ms)
            self.window.play_button.setText('Pause')
            print(f'GUI: Auto-run started at interval={ms}ms')

    def _auto_step(self):
        # QTimer calls this repeatedly
        if not self.machine:
            return
        if self.machine.current_state in (self.machine.accept_state, self.machine.reject_state):
            self.timer.stop()
            self.window.play_button.setText('Play')
            return
        self.machine.step()
        self._after_step()

    def _update_timer_interval(self):
        ms = max(1, int(self.window.speed_slider.value()))
        # If timer is already running, restart with the new interval so speed changes apply immediately.
        if self.timer.isActive():
            self.timer.start(ms)
        else:
            self.timer.setInterval(ms)

    def _update_debug(self):
        if not self.machine:
            return
        enabled = bool(self.window.debug_checkbox.isChecked())
        self.machine.set_debug(enabled)
        print(f"GUI: set debug={enabled}")

    def _export_log(self):
        if not self.log_file:
            print('GUI: no log to export — run first')
            return
        # flush and show path
        self.log_file.flush()
        print(f"GUI: log saved: {os.path.abspath(self.log_file.name)}")

    def _build_detailed_and_html(self):
        # Build a detailed text narration and an HTML timeline from machine.history
        hist = getattr(self.machine, 'get_history', lambda: [])()
        txt_lines = []
        txt_lines.append(f"Detailed run for input={self.window.input_box.text()}\n\n")

        # Build HTML parts
        html_parts = [
            '<!doctype html>',
            '<html><head><meta charset="utf-8"><title>Turing run timeline</title>',
            '<style>body{font-family:Arial; background:#222; color:#eee} .step{padding:8px;border-bottom:1px solid #444} .head{font-weight:bold;color:#ffdd57} .tape{font-family:monospace; background:#111; padding:4px; display:inline-block}</style>',
            '</head><body>',
            f'<h1>Run timeline: input={self.window.input_box.text()}</h1>',
            '<div id="timeline">'
        ]

        for i, entry in enumerate(hist):
            before = entry.get('before_state')
            read = entry.get('read_symbol')
            trans = entry.get('transition')
            after = entry.get('after_state')
            tape = entry.get('tape')
            head = entry.get('after_head')

            reason = self.STATE_EXPLANATIONS.get(before, '')
            if trans:
                trans_str = f"{trans[0]},{trans[1]} -> {trans[2]},{trans[3]},{trans[4]}"
            else:
                trans_str = 'NO_TRANSITION'

            txt_lines.append(f"Step {i}: state={before} read='{read}'\n  reason: {reason}\n  transition: {trans_str}\n  after: state={after} head={head} tape={tape}\n\n")

            # HTML block for step
            html_parts.append(
                f'<div class="step" id="step{i}">'
                f'<div><span class="head">Step {i} — {before}</span> &nbsp; read: <code>{read}</code></div>'
                f'<div style="margin-top:6px">{reason}</div>'
                f'<div style="margin-top:6px">Transition: <code>{trans_str}</code></div>'
                f'<div style="margin-top:6px">After: state={after} head={head} tape=<span class="tape">{tape}</span></div>'
                f'<div style="margin-top:6px"><a href="#step{i}">Link to this step</a></div>'
                f'</div>'
            )

        html_parts.append('</div></body></html>')

        return (''.join(txt_lines), '\n'.join(html_parts))

    def _log(self, s: str):
        try:
            if self.log_file:
                self.log_file.write(s)
        except Exception:
            pass