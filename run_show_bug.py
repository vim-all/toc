import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from tm_engine.palindrome_machine import create_palindrome_machine

m = create_palindrome_machine('10101', debug=True)
steps = 0
print('Running 10101...')
while m.current_state not in (m.accept_state, m.reject_state) and steps < 200:
    m.step()
    steps += 1
print('Final state:', m.current_state)
print('Steps:', steps)
print('Tape:', ''.join(m.tape.get_tape()))
print('\nHistory:')
for i, h in enumerate(getattr(m, 'get_history')()):
    print(i, h)
