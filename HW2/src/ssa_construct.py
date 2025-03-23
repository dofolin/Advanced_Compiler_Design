import argparse
import json
import sys
from collections import defaultdict

from cfg import BasicBlock, flatten_blocks, func_blocks, CFG, Node, Instruction, Program, Type
from dominance import dom_frontier, dom_tree, dominators

class LabelGenerator:
    def __init__(self, blocks: list[BasicBlock]):
        self.used = {
            block[0]['label'] for block in blocks if 'label' in block[0]
        }
        self.count = 0

    def next(self) -> str:
        while (label := f'anonymous{self.count}') in self.used:
            self.count += 1

        self.count += 1

        return label

def insert_labels(blocks: list[BasicBlock], gen: LabelGenerator):
    for block in blocks:
        if 'label' not in block[0]:
            block.insert(0, {'label': gen.next()})

def get_label(block: BasicBlock) -> str:
    assert 'label' in block[0]

    return block[0]["label"]

def to_ssa(graph: CFG, args: list[str]):
    dom = dominators(graph)
    frontier = dom_frontier(graph, dom)
    tree = dom_tree(graph, dom)

    defs: dict[str, list[Node]] = defaultdict(list)
    vars: list[set[str]] = [set() for _ in graph.all]
    types: dict[str, Type] = {}

    for node in graph.all:
        for item in node.block:
            if 'dest' in item and (var := item['dest']) not in vars[node.id]:
                assert 'type' in item

                vars[node.id].add(var)
                defs[var].append(node)
                types[var] = item['type']

    phis: list[set[str]] = [set() for _ in graph.all]
    orig: dict[int, str] = {}

    for var in defs:
        while defs[var]:
            for node in frontier[defs[var].pop().id]:
                if var not in phis[node.id]:
                    phis[node.id].add(var)

                    instr: Instruction = {
                        'op': 'phi',
                        'dest': var,
                        'labels': [get_label(pred.block) for pred in node.ins],
                        'args': [var for _ in node.ins],
                        'type': types[var],
                    }

                    node.block.insert('label' in node.block[0], instr)
                    orig[id(instr)] = var

                    if var not in vars[node.id]:
                        defs[var].append(node)

    stack: dict[str, list[str]] = {var: [] for var in defs}
    next: dict[str, int] = {var: 0 for var in defs}

    for arg in args:
        stack[arg] = [arg]

    def rename(node: Node):
        pop: dict[str, int] = defaultdict(lambda: 0)

        for item in node.block:
            if 'args' in item and item['op'] != 'phi':
                item['args'] = [stack[arg][-1] for arg in item['args']]

            if 'dest' in item:
                dest = item['dest']

                new = f'{dest}.{next[dest]}'
                next[dest] += 1
                pop[dest] += 1

                item['dest'] = new
                stack[dest].append(new)

        for successor in node.outs:
            for item in successor.block:
                if 'op' in item and item['op'] == 'phi':
                    assert 'args' in item

                    names = stack[orig[id(item)]]
                    renamed = names[-1] if names else '__undef'

                    item['args'][successor.ins.index(node)] = renamed

        for child in tree[node.id].children:
            rename(child.node)

        for var in pop:
            del stack[var][-pop[var]:]

    rename(graph.entry)

def replace_target(block: BasicBlock, old: str, new: str):
    last = block[-1]

    if 'labels' in last:
        last['labels'] = [
            new if label == old else label
                for label in last['labels']
        ]
    else:
        block.append({'op': 'jmp', 'labels': [new]})

def from_ssa(graph: CFG, gen: LabelGenerator):
    for i in range(len(graph.all)):
        node = graph.all[i]

        for j, pred in enumerate(node.ins):
            assignments: list[Instruction] = []

            for item in node.block:
                if 'op' in item and item['op'] == 'phi':
                    assert 'args' in item
                    assert 'dest' in item
                    assert 'type' in item

                    arg = item['args'][j]

                    if arg != '__undef':
                        assignments.append({
                            'op': 'id',
                            'dest': item['dest'],
                            'args': [arg]
                        })
                    else:
                        assignments.append({
                            'op': 'const',
                            'dest': item['dest'],
                            'type': item['type'],
                            'value': 0,
                        })

            if not assignments:
                continue

            this_label = get_label(node.block)
            new_label = gen.next()

            replace_target(pred.block, this_label, new_label)

            graph.all.append(Node(
                len(graph.all),
                [
                    {'label': new_label},
                    *assignments,
                    {'op': 'jmp', 'labels': [this_label]}
                ],
                [pred],
                [node]
            ))

            pred.outs[pred.outs.index(node)] = graph.all[-1]
            node.ins[j] = graph.all[-1]

        node.block = [
            item for item in node.block
                if 'op' not in item or item['op'] != 'phi'
        ]

def insert_explicit_return(graph: CFG):
    for node in graph.exits:
        last = node.block[-1]

        if 'op' not in last or last['op'] != 'ret':
            node.block.append({'op': 'ret'})
