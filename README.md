# Turing Machine Simulator

This project contains a small Turing Machine simulator with three example machines:
- Palindrome recognizer (binary alphabet 0/1)
- Binary addition (two binary numbers)
- Unary multiplication (two unary numbers)

It also includes a minimal PyQt UI to step and auto-run machine executions.

**Project layout**

- `main.py` — application entrypoint (Qt application)
- `controller/simulator_controller.py` — glue between UI and Turing machine objects
- `tm_engine/` — Turing machine implementations and helper classes
  - `turing_machine.py` — core `TuringMachine` class (transition execution, history)
  - `tape.py` — simple tape abstraction with blank symbol and head position
  - `palindrome_machine.py` — palindrome Turing machine factory
  - `binary_addition.py` — binary-addition helpers and stepwise machine adapter
  - `unary_multiplication.py` — unary-multiplication machine adapter
- `ui/` — Qt UI widgets (`main_window.py`, `tape_widget.py`)
- `requirements.txt` — Python dependencies

**NOTE:** The UI imports `PyQt6` in `main.py` while `requirements.txt` lists `PyQt5`. If you are using the GUI, install `PyQt6` (or adapt imports to PyQt5).

**Quick Start**

1. Create and activate a virtual environment (recommended):

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (Command Prompt):

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies (adjust if you need PyQt6):

On all platforms (after activating the virtual environment):

```bash
pip install -r requirements.txt
```

If you intend to use the PyQt6-based UI (the code imports `PyQt6` in `main.py`), also install:

```bash
pip install PyQt6
```

Note: `requirements.txt` currently lists `PyQt5`. Either install `PyQt5` or install `PyQt6` and update imports accordingly.

3. Run the GUI:

```bash
python3 main.py
```

4. In the GUI:
- Type an input in the input box
- Select an operation: `Palindrome`, `Binary Addition`, or `Unary Multiplication`
- Click `Start`, then use `Step` to step once or `Play` to auto-run
- Use the `Debug` checkbox for verbose internal logs

Detailed Machine Explanations

**Turing Machine primitives**

- `Tape` (`tm_engine/tape.py`): a list of symbols with a `blank` symbol `_`, a `tape` list, and a `head` index. Methods: `read()`, `write(symbol)`, `move_right()`, `move_left()`, `get_tape()`.
- `TuringMachine` (`tm_engine/turing_machine.py`): takes a `Tape` instance, a `transitions` dict mapping `(state, symbol)` to `(new_state, write_symbol, move)` where `move` is `'L'` or `'R'`. The machine exposes `step()` and maintains `history`, `step_count`, `last_action`, and `last_transition` for logging and UI display.

**Palindrome recognizer** (`tm_engine/palindrome_machine.py`)

Overview:

- Input alphabet: `0`, `1` (blank `_` used as blank).
- The machine recognizes whether the input string is a palindrome.
- It uses an in-place marking strategy: marks matched symbols with `X` and progressively removes matched outermost pairs.

Key states and behavior (as implemented):

- `q0` (start): Move from the leftmost unmarked symbol. If current symbol is `0` go to `q1` (mark left `0`); if `1` go to `q2` (mark left `1`); if `_` (empty) accept.
- `q1`: Scan right over `0`, `1`, and `X` until blank `_`, then switch to `q3` to search left for a matching `0`.
- `q2`: Same as `q1` but will search left for a matching `1` (switches to `q5`).
- `q3`: From the right end move left skipping `X` until finding a `0` (match) — if finds `0`, write `X` and go to `q4`; if finds `1` → reject; if sees `_` → accept (odd-length center processed).
- `q5`: Symmetric to `q3` but matches `1`.
- `q4`: Return left to left side (move left until left blank) then resume at `q0` to continue outermost pair processing.
- `q_accept` / `q_reject`: Halting states.

Worked example:

- Input: `0110`
  - `q0` marks leftmost `0` → `X 1 1 0`
  - move to rightmost and try to match `0` → mark it `X 1 1 X`
  - return left and continue; next pair `1` matched with `1` → all symbols become `X` → accept.

Why it works:

- By always marking and removing the outermost pair, the machine ensures matched pairs symmetrically; any mismatch is detected when scanning from the right for a specific symbol.

**Binary addition** (`tm_engine/binary_addition.py`)

Available interfaces:

- `binary_addition_tm(tape_input)` — simple functional implementation returning resulting binary string. Input format: two binary numbers separated by `+` (e.g. `101+11`). The implementation computes bitwise sum from LSB to MSB using integer arithmetic and a `carry` variable, then returns the result.
- `binary_addition_tm_steps(tape_input)` — returns a list of textual steps describing each bit addition and carry updates.
- `create_binary_addition_machine(input_string, debug=False)` — returns a stateful `BinaryAdditionMachine` object with a `step()` method and a `tape` representation that shows input and incremental result area. This adapter is used by the GUI so users can see partial results and step-by-step progression.

Algorithm (functional version):

- Split input around `+` into `left` and `right` strings.
- Reverse both strings to process LSB first.
- For each bit position, compute `total = bit1 + bit2 + carry` where `bit1` and `bit2` default to `0` when one operand is shorter.
- Output bit = `total % 2`, carry = `total // 2`.
- After iterating positions, if `carry` remains, append `1`.

Complexity: linear in the length of the longer operand.

Example:

- `101 + 11` → process positions: 1+1→0 carry1, 0+1+1→0 carry1, 1+0+1→1 carry1 → final carry → `1000`.

Stepwise adapter (GUI):

- The `BinaryAdditionMachine` builds a `Tape` containing `left + '+' + right` and appends blank cells for a result area.
- Each `step()` computes one result bit (LSB-first), writes the current partial result into the result area (reversed to show MSB-first in the UI), and updates `last_action`, `history`, and `step_count` for the controller to display.

**Unary multiplication** (`tm_engine/unary_multiplication.py`)

Overview:

- Input format: `a*b` where `a` and `b` are unary numbers represented by the symbol `1`. Example: `111*11` means 3 * 2.
- The adapter computes the product by producing `a * b` ones on the tape. This is a simplified, stepwise write-on-tape machine: each `step()` writes one `1` into the result area until `a*b` ones are written, then accepts.

Implementation notes:

- The adapter parses input and computes integer lengths `a = len(left)` and `b = len(right)`.
- `result_len = a * b` determines how many `1` symbols will be written.
- The `Tape` is initialized with blanks and the machine writes one `1` per `step()` at successive cells; when `write_index` reaches `result_len` the machine enters `q_accept`.

Example:

- Input: `111*1111` (3 * 4) → `result_len = 12` → after 12 `step()` calls the tape contains twelve `1` symbols and the machine accepts.

GUI & Logging

- The controller `controller/simulator_controller.py` creates a machine based on UI selection, opens a timestamped run log file, and records a human-readable `history` suitable for building plain-text or simple HTML timelines.
- The UI exposes controls for `Start`, `Step`, `Play` (auto-step using a `QTimer`), `Speed` slider, `Debug` checkbox (toggles `.set_debug(True)` on the machine), and `Export` to save logs.

Troubleshooting

- If the GUI fails to start due to Qt import errors, ensure you installed the correct PyQt version and that the virtual environment is activated.
- If you see unexpected symbols on the tape display, check that inputs follow the documented formats:
  - Palindrome: a binary string of `0`/`1` (no separators)
  - Binary addition: `a+b` where `a` and `b` are binary strings
  - Unary multiplication: `1...1*1...1` (only `1` and `*` allowed)

Extending the project

- Add more example machines by creating new factories similar to `create_palindrome_machine` and adding them to the UI selector and controller.
- Improve the visual tape widget to show indexed cells or to support long tapes with scroll/pan.

License & Credits

This repository is intended for educational use. Feel free to reuse code for learning and coursework; if you redistribute, include attribution.

-- End of README
