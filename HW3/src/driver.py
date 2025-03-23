from cfg import *
from ssa_to_llvm import *
from ssa_construct import to_ssa
import json


def main():
    """ Read a bril program from stdin, convert to ssa, then emit LLVM by function.
    """
    f = None
    fname = ''

    if len(sys.argv) <= 1:
        f = sys.stdin
        fname = 'stdin'
    else:
        f = open(sys.argv[1])
        fname = sys.argv[1]

    prog = to_ssa(json.load(f))
    if 'structs' not in prog:
        prog['structs'] = []

    main_args = []

    print(PROG_HDR.format(fname, fname))

    # Compute struct size for allocation,
    # Build mbr offset reference, and
    # Emit LLVM declaration.
    for struct in prog['structs']:
        name = struct['name']
        size = 0

        struct_mbr_offsets[name] = {}

        mbrs = []
        for i, mbr in enumerate(struct['mbrs']):
            size += sizeof(mbr['type'])

            struct_mbr_offsets[name][mbr['name']] = i

            mbrs.append(ttype(mbr['type']))

        struct_sizes[name] = size
        print('%{} = type {{ {} }}'.format(name, ', '.join(mbrs)))


    # Iterate and emit functions
    for func in prog['functions']:

        if (func['name'] == 'main'):
            if 'args' in func:
                main_args = func['args']
            if 'type' in func:
                func.pop('type') # We wouldn't actually return the value anyway
        func['name'] = '__' + func['name'] # Avoid name collisions in C world

        emit_func(func, Context(func))

    emit_main(main_args)

if __name__ == '__main__':
    main()
