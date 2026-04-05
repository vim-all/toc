
def binary_addition_tm(tape_input):

    if "#" not in tape_input:
        return "Invalid format (use number1#number2)"

    left, right = tape_input.split("#")

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

    if "#" not in tape_input:
        return ["Invalid format (use number1#number2)"]

    left, right = tape_input.split("#")

    if not all(c in "01" for c in left + right):
        return ["Input must contain only binary digits (0 and 1)"]

    left_rev = left[::-1]
    right_rev = right[::-1]

    carry = 0
    result = ""
    steps = []

    max_len = max(len(left_rev), len(right_rev))

    steps.append(f"Initial Tape: {left}#{right}")

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