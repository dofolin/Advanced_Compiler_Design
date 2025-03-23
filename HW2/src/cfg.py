from dataclasses import dataclass
from typing import TypedDict, Union

Type = Union[str, dict[str, 'Type']]
Literal = Union[bool, int]

class Label(TypedDict):
    label: str

class _InstructionBase(TypedDict):
    op: str

class Instruction(_InstructionBase, total=False):
    dest: str
    type: Type
    args: list[str]
    funcs: list[str]
    labels: list[str]
    value: Literal

Item = Union[Label, Instruction]

class Argument(TypedDict):
    name: str
    type: Type

class _FunctionBase(TypedDict):
    name: str
    instrs: list[Item]

class Function(_FunctionBase, total=False):
    args: list[Argument]
    type: Type

class Program(TypedDict):
    functions: list[Function]

def is_term(instr: Instruction) -> bool:
    return instr['op'] in ('jmp', 'br', 'ret')

BasicBlock = list[Item]

def func_blocks(func: Function) -> list[BasicBlock]:
    items = func['instrs']

    blocks: list[BasicBlock] = []
    lead = 0

    for i, item in enumerate(items):
        if 'label' in item:
            if lead < i:
                blocks.append(items[lead:i])

            lead = i
        elif is_term(item):
            blocks.append(items[lead:i + 1])
            lead = i + 1

    if lead < len(items):
        blocks.append(items[lead:])

    return blocks

def prog_blocks(prog: Program) -> dict[str, list[BasicBlock]]:
    return {func['name']: func_blocks(func) for func in prog['functions']}

def flatten_blocks(blocks: list[BasicBlock]) -> list[Item]:
    return [item for block in blocks for item in block]

@dataclass(eq=False)
class Node:
    id: int
    block: BasicBlock
    ins: list['Node']
    outs: list['Node']

def successors(i: int, nodes: list[Node], labels: dict[str, Node]):
    last = nodes[i].block[-1]

    if 'labels' in last:
        return [labels[label] for label in last['labels']]

    if 'op' in last and last['op'] == 'ret' or i + 1 == len(nodes):
        return []

    return [nodes[i + 1]]

def is_exit(i: int, nodes: list[Node]):
    last = nodes[i].block[-1]

    if 'op' in last:
        if last['op'] == 'ret':
            return True
        elif last['op'] in ('jmp', 'br'):
            return False

    return i + 1 == len(nodes)

@dataclass
class CFG:
    entry: Node
    exits: list[Node]
    all: list[Node]

    @classmethod
    def from_blocks(cls, blocks: list[BasicBlock]):
        nodes = [Node(id, block, [], []) for id, block in enumerate(blocks)]
        exits = []

        labels = {
            node.block[0]['label']: node
                for node in nodes if 'label' in node.block[0]
        }

        for i, node in enumerate(nodes):
            node.outs = successors(i, nodes, labels)

            for successor in node.outs:
                successor.ins.append(node)

            if is_exit(i, nodes):
                exits.append(node)

        return cls(nodes[0], exits, nodes)
