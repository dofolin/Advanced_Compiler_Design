import json
from typing import Any, Dict, List, Optional

class Instruction:
    def __init__(self, instr: Dict[str, Any]):
        self.op: Optional[str] = instr.get('op')
        self.instr = instr

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.op is not None:
            result['op'] = self.op
        return result

    def __repr__(self):
        return json.dumps(self.to_dict())

class Const(Instruction):
    def __init__(self, instr: Dict[str, Any]):
        super().__init__(instr)
        self.dest = instr.get('dest')
        self.type = instr.get('type')
        self.value = instr.get('value')

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.dest is not None:
            result['dest'] = self.dest
        if self.type is not None:
            result['type'] = self.type
        if self.value is not None:
            result['value'] = self.value
        return result

class ValueOperation(Instruction):
    def __init__(self, instr: Dict[str, Any]):
        super().__init__(instr)
        self.dest = instr.get('dest')
        self.type = instr.get('type')
        self.args = instr.get('args', [])
        self.funcs = instr.get('funcs', [])
        self.labels = instr.get('labels', [])

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.dest is not None:
            result['dest'] = self.dest
        if self.type is not None:
            result['type'] = self.type
        if self.args:
            result['args'] = self.args
        if self.funcs:
            result['funcs'] = self.funcs
        if self.labels:
            result['labels'] = self.labels
        return result

class EffectOperation(Instruction):
    def __init__(self, instr: Dict[str, Any]):
        super().__init__(instr)
        self.args = instr.get('args', [])
        self.funcs = instr.get('funcs', [])
        self.labels = instr.get('labels', [])

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.args:
            result['args'] = self.args
        if self.funcs:
            result['funcs'] = self.funcs
        if self.labels:
            result['labels'] = self.labels
        return result

class Label(Instruction):
    def __init__(self, instr: Dict[str, Any]):
        super().__init__(instr)
        self.label = instr.get('label')

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.label is not None:
            result['label'] = self.label
        return result

class Function:
    def __init__(self, func: Dict[str, Any]):
        self.name = func.get('name')
        self.args = func.get('args', [])
        self.type = func.get('type')
        self.instrs = [self._parse_instr(instr) for instr in func.get('instrs', [])]

    def _parse_instr(self, instr: Dict[str, Any]) -> Instruction:
        if 'label' in instr:
            return Label(instr)
        else:
            op = instr.get('op')
            if op == 'const':
                return Const(instr)
            elif 'dest' in instr:
                return ValueOperation(instr)
            else:
                return EffectOperation(instr)

    def to_dict(self) -> Dict[str, Any]:
        result = {'name': self.name}
        if self.args:
            result['args'] = self.args
        if self.type is not None:
            result['type'] = self.type
        result['instrs'] = [instr.to_dict() for instr in self.instrs]
        return result

class Program:
    def __init__(self, prog: Dict[str, Any]):
        self.functions = [Function(func) for func in prog.get('functions', [])]

    def to_dict(self) -> Dict[str, Any]:
        return {'functions': [func.to_dict() for func in self.functions]}

def parse_bril(json_str: str) -> Program:
    prog = json.loads(json_str)
    return Program(prog)

def serialize_bril(prog: Program) -> str:
    return json.dumps(prog.to_dict(), indent=2)