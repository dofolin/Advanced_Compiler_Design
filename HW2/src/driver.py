import argparse
import json
import sys
from collections import defaultdict

from cfg import BasicBlock, flatten_blocks, func_blocks, CFG, Node, Instruction, Program, Type
from dominance import dom_frontier, dom_tree, dominators
from ssa_construct import get_label, insert_labels, LabelGenerator, to_ssa, from_ssa, insert_explicit_return


def main():
    parser = argparse.ArgumentParser(description='SSA conversion.')

    parser.add_argument(
        'file',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin
    )
    parser.add_argument(
        '--roundtrip',
        action='store_true'
    )

    args = parser.parse_args()
    prog: Program = json.load(args.file)

    for func in prog['functions']:
        func_args = func['args'] if 'args' in func else []

        blocks = func_blocks(func)
        blocks.insert(0, [{'label': '__entry'}])

        graph = CFG.from_blocks(blocks)
        gen = LabelGenerator(blocks)

        insert_labels(blocks, gen)
        insert_explicit_return(graph)

        to_ssa(graph, [arg['name'] for arg in func_args])

        if args.roundtrip:
            from_ssa(graph, gen)

        func['instrs'] = flatten_blocks([node.block for node in graph.all])

    json.dump(prog, sys.stdout)

if __name__ == '__main__':
    main()
