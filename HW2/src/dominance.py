from dataclasses import dataclass
from typing import Generator, Optional

from cfg import CFG, Node

def post_order(graph: CFG) -> Generator[Node, None, None]:
    visited: set[int] = set()

    def visit(node: Node) -> Generator[Node, None, None]:
        visited.add(node.id)

        for successor in node.outs:
            if successor.id not in visited:
                yield from visit(successor)

        yield node

    return visit(graph.entry)

def dominators(graph: CFG) -> list[set[Node]]:
    dom = [set(graph.all) for _ in graph.all]
    dom[graph.entry.id] = {graph.entry}

    post = list(post_order(graph))
    changed = True

    while changed:
        changed = False

        for node in reversed(post):
            if node.id != graph.entry.id:
                new = set(graph.all)

                for predecessor in node.ins:
                    new.intersection_update(dom[predecessor.id])

                new.add(node)

                if new != dom[node.id]:
                    dom[node.id] = new
                    changed = True

    return dom

def dominates(graph: CFG, dom: list[set[Node]]) -> list[set[Node]]:
    dominates: list[set[Node]] = [set() for _ in graph.all]

    for dominated, dominators in zip(graph.all, dom):
        for dominator in dominators:
            dominates[dominator.id].add(dominated)

    return dominates

@dataclass
class DomTree:
    node: Node
    parent: Optional['DomTree']
    children: list['DomTree']

def dom_tree(graph: CFG, dom: list[set[Node]]) -> list[DomTree]:
    all = [DomTree(node, None, []) for node in graph.all]

    for i, node in enumerate(all):
        for dominator in dom[i]:
            if dominator.id == i:
                continue

            for other in dom[i]:
                if dominator in dom[other.id] and dominator.id != other.id != i:
                    break
            else:
                node.parent = all[dominator.id]
                all[dominator.id].children.append(node)

    return all

def dom_frontier(graph: CFG, dom: list[set[Node]]):
    doms = dominates(graph, dom)
    frontier: list[set[Node]] = [set() for _ in graph.all]

    for node in graph.all:
        for dominated in doms[node.id]:
            for successor in dominated.outs:
                if node not in dom[successor.id] or node.id == successor.id:
                    frontier[node.id].add(successor)

    return frontier
