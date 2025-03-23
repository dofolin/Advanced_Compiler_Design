import sys
from bril import parse_bril, Program, Const, ValueOperation

def is_ssa(bril_program: Program):
    """
    Verifies if the given Bril program is in SSA form.
    Returns True if it is, False otherwise.
    """
    for function in bril_program.functions:
        assigned_vars = set()
        for instr in function.instrs:
            if isinstance(instr, (Const, ValueOperation)):
                var = instr.dest
                if var in assigned_vars:
                    # Variable assigned more than once
                    return False
                assigned_vars.add(var)
    return True

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Check if a Bril program is in SSA form')
    parser.add_argument('--input', type=str, help='Input Bril JSON file', default=None)
    args = parser.parse_args()

    if args.input:
        with open(args.input, 'r') as f:
            json_input = f.read()
    else:
        json_input = sys.stdin.read()

    program = parse_bril(json_input)
    result = is_ssa(program)
    print("SSA" if result else "Not SSA")
    exit(0 if result else 1)

if __name__ == '__main__':
    main()