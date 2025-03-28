from cfg import *
from ssa_construct import to_ssa
import json

# Constant header for every program, including:
#   - LLVM preamble stuff
#   - Constants to support Bril primitives
#   - print_bool, print_int, print_space, print_newline, and print_ptr to be
#   used by Bril's print builtin
PROG_HDR = """
; ModuleID = '{}'
source_filename = "{}"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [5 x i8] c"true\\00", align 1
@.str.1 = private unnamed_addr constant [6 x i8] c"false\\00", align 1
@.str.2 = private unnamed_addr constant [4 x i8] c"%ld\\00", align 1
@.str.3 = private unnamed_addr constant [9 x i8] c"[object]\\00", align 1
@.str.4 = private unnamed_addr constant [33 x i8] c"error: expected %d args, got %d\\0A\\00", align 1

; DECLARE LIBRARY CALLS
declare dso_local i32 @putchar(i32)
declare dso_local i32 @printf(i8*, ...)
declare dso_local void @exit(i32)
declare dso_local i64 @atol(i8*)
declare dso_local noalias i8* @malloc(i64)
declare dso_local void @free(i8*)

define dso_local i32 @btoi(i8* %0) #0 {{
  %2 = alloca i8*, align 8
  store i8* %0, i8** %2, align 8
  %3 = load i8*, i8** %2, align 8
  %4 = load i8, i8* %3, align 1
  %5 = sext i8 %4 to i32
  %6 = icmp eq i32 %5, 116
  %7 = zext i1 %6 to i32
  ret i32 %7
}}

define dso_local void @print_bool(i1 %0) {{
  %2 = icmp ne i1 %0, 0
  br i1 %2, label %3, label %5

3:
  %4 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([5 x i8], [5 x i8]* @.str, i64 0, i64 0))
  br label %7

5:
  %6 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str.1, i64 0, i64 0))
  br label %7

7:
  ret void
}}

define dso_local void @print_space() {{
  %1 = call i32 @putchar(i32 32)
  ret void
}}

define dso_local void @print_newline() {{
  %1 = call i32 @putchar(i32 10)
  ret void
}}

define dso_local void @print_int(i64 %0) {{
  %2 = alloca i64, align 8
  store i64 %0, i64* %2, align 8
  %3 = load i64, i64* %2, align 8
  %4 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.2, i64 0, i64 0), i64 %3)
  ret void
}}

define dso_local void @print_ptr(i8* %0) {{
  %2 = alloca i8*, align 8
  store i8* %0, i8** %2, align 8
  %3 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([9 x i8], [9 x i8]* @.str.3, i64 0, i64 0))
  ret void
}}
"""

# Header / Footer for every function
FUN_HDR = """
define dso_local {} @{}({}) {{
"""

FUN_FTR = """
}
"""

# Bril op -> LLVM op
OPS = {'add' : 'add',
       'mul' : 'mul',
       'sub' : 'sub',
       'div' : 'sdiv',
       'eq'  : 'icmp eq',
       'lt'  : 'icmp slt',
       'gt'  : 'icmp sgt',
       'le'  : 'icmp sle',
       'ge'  : 'icmp sge',
       'and' : 'and',
       'or'  : 'or',
}

def is_ptr_type(t):
    """Decide whether the Bril type t is a pointer"""
    return (isinstance(t, dict) and 'ptr' in t)

def ttype(briltype):
    """Given a Bril type, return a string for the corresponding LLVM type"""
    if briltype == 'int':
        return 'i64'
    elif briltype == 'bool':
        return 'i1'

    elif is_ptr_type(briltype):
        return ttype(briltype['ptr']) + '*'

    else: # name of a struct
        return '%' + briltype

# name -> size in bytes (maybe a global isn't the best choice here...)
struct_sizes = {}

# struct name -> mbr name -> mbr offset idx
struct_mbr_offsets = {}

def sizeof(briltype):
    if briltype == 'bool':
        return 1
    elif is_ptr_type(briltype):
        return 8
    elif briltype in struct_sizes:
        return struct_sizes[briltype]
    else: #int
        return 8


class Context:
    """ Function-level information about bril variables.
    types: name -> type            -- bril type label for each var.
    constants: name -> const value -- const values for bril constants
    canonical: name -> name        -- canonical var. names for bril `id` copies
    is_main: bool                  -- true iff this is the main func
    """
    def __init__(self, func):
        types = {}
        consts = {}
        canon = {}
        for i in func['instrs']:
            if 'dest' in i:
                if i['op'] == 'phi':
                    types[i['dest']] = types[i['args'][0]]
                else:
                    types[i['dest']] = i['type']
                    if i['op'] == 'id':
                        if i['args'][0] in consts:
                            consts[i['dest']] = consts[i['args'][0]]
                        elif i['args'][0] in canon:
                            canon[i['dest']] = canon[i['args'][0]]
                        else:
                            canon[i['dest']] = i['args'][0]
            if 'value' in i:
                if i['type'] == 'bool':
                    consts[i['dest']] = 1 if i['value'] else 0
                else:
                    consts[i['dest']] = i['value']
        self.types = types
        self.constants = consts
        self.canonical = canon
        self.mainfunc = func['name'] == '__main'
        self.next_int = 0

    def format_args(self, args, show_types=False):
        alist = []
        for a in args:
            t = self.types[a]
            if a in self.constants:
                a = self.constants[a]
                if is_ptr_type(t) and not a:
                    a = 'null'
            elif a in self.canonical:
                a = '%' + self.canonical[a]
            else:
                a = '%' + a
            s = ttype(t) + ' ' + str(a) if show_types else str(a)
            alist.append(s)
        return ', '.join(alist)

    def new_var(self, t):
        v = 'z' + str(self.next_int)
        self.next_int += 1
        self.types[v] = t
        return v

def emit_instr(instr, ctxt):
    """Emit LLVM instruction(s) implementing instr, a bril instruction"""
    args = instr['args'] if 'args' in instr else []


    if 'op' in instr:

        # VALUE operations:
        if 'dest' in instr:
            if instr['op'] == 'call':
                print('  %{} = call {} @__{}({})'.format(instr['dest'],
                                                         ttype(instr['type']),
                                                         instr['funcs'][0],
                                                         ctxt.format_args(args, show_types=True)))

            elif instr['op'] == 'not':
                print('  %{} = xor i1 1, {}'.format(instr['dest'],
                                                    ctxt.format_args(args)))

            elif instr['op'] in OPS:
                print('  %{} = {} {} {}'.format(instr['dest'],
                                                OPS[instr['op']],
                                                ttype(ctxt.types[args[0]]),
                                                ctxt.format_args(args)))
            elif instr['op'] == 'phi':
                s = '  %{} = phi {} '.format(instr['dest'], ttype(ctxt.types[args[0]]))
                pairs = []
                while args:
                    (a, lbl) = (args.pop(), instr['labels'].pop())
                    pairs.append('[ {}, %{} ]'.format(ctxt.format_args([a]), lbl))
                print(s + ', '.join(pairs))

            elif instr['op'] == 'alloc':
                new_var = ctxt.new_var('int')
                print('  %{} = mul i64 {}, {}'.format(new_var,
                                                      ctxt.format_args(args),
                                                      sizeof(instr['type']['ptr'])))

                ptr = ctxt.new_var(None) # the type is a lie! (but we'll never query for it)
                print('  %{} = call i8* @malloc({})'.format(ptr,
                                                            ctxt.format_args([new_var], show_types=True)))
                print('  %{} = bitcast i8* %{} to {}'.format(instr['dest'],
                                                             ptr,
                                                             ttype(instr['type'])))
            elif instr['op'] == 'load':
                print('  %{} = load {}, {}'.format(instr['dest'],
                                                   ttype(instr['type']),
                                                   ctxt.format_args(args, show_types=True)))

            elif instr['op'] == 'ptradd':
                print('  %{} = getelementptr inbounds {}, {}'.format(instr['dest'],
                                                                     ttype(instr['type']['ptr']),
                                                                     ctxt.format_args(args, show_types=True)))
            elif instr['op'] == 'getmbr':
                struct = ctxt.types[args[0]]['ptr']
                print('  %{} = getelementptr inbounds {}, {}, i64 0, i32 {}'.format(
                                                        instr['dest'],
                                                        ttype(struct),
                                                        ctxt.format_args(args[:1], show_types=True),
                                                        struct_mbr_offsets[struct][args[1]]))
            elif instr['op'] == 'isnull':
                new_var = ctxt.new_var('int')
                print('  %{} = ptrtoint {} to i64'.format(new_var,
                                                          ctxt.format_args(args, show_types=True)))
                print('  %{} = icmp eq i64 0, %{}'.format(instr['dest'],
                                                          new_var))



        # EFFECT operations
        else:
            # control: br jmp ret
            if instr['op'] == 'br':
                print('  br i1 {}, label %{}, label %{}'.format(ctxt.format_args(args),
                                                                instr['labels'][0],
                                                                instr['labels'][1]))
            elif instr['op'] == 'jmp':
                print('  br label %{}'.format(instr['labels'][0]))

            elif instr['op'] == 'ret':
                r = ctxt.format_args(args, show_types=True)
                if not r or ctxt.mainfunc:
                    r = 'void'
                print('  ret {}'.format(r))

            # void call
            elif instr['op'] == 'call':
                print('  call void @__{}({})'.format(instr['funcs'][0],
                                                   ctxt.format_args(args, show_types=True)))
            # print
            elif instr['op'] == 'print':
                s = []
                for a in args:
                    t = ctxt.types[a]
                    s.append('  call void @print_{}({})'.format(t, ctxt.format_args([a], show_types=True)))
                print("\n  call void @print_space()\n".join(s)) # Spaces between args
                print('  call void @print_newline()')           # Newline at end

            elif instr['op'] == 'free':
                byte_ptr = ctxt.new_var(None) # the type is a lie! (but we'll never query for it)
                print('  %{} = bitcast {} to i8*'.format(byte_ptr,
                                                         ctxt.format_args(args, show_types=True)))
                print('  call void @free(i8* %{})'.format(byte_ptr))

            elif instr['op'] == 'store':
                print('  store {}'.format(ctxt.format_args(reversed(args), show_types=True)))

    # LABEL
    else:
        print(instr['label'] + ':')


def emit_func(f, ctxt):

    # Translate return type
    rettype = ttype(f['type']) if 'type' in f else 'void'

    # Translate args
    args = []
    if 'args' in f:
        for a in f['args']:
            args.append(ttype(a['type']) + ' %' + a['name'])
    args = ', '.join(args)

    # Start emitting the fn
    print(FUN_HDR.format(rettype, f['name'], args), end='')

    for instr in f['instrs']:
        emit_instr(instr, ctxt)

    print(FUN_FTR)


MAIN = """
define dso_local i32 @main(i32 %argc, i8** %argv) {{
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca i8**, align 8
  store i32 0, i32* %1, align 4
  store i32 %argc, i32* %2, align 4
  store i8** %argv, i8*** %3, align 8
  %4 = load i32, i32* %2, align 4
  %5 = sub nsw i32 %4, 1
  %6 = icmp ne i32 %5, {}  ; NUM ARGS
  br i1 %6, label %7, label %11

7:
  %8 = load i32, i32* %2, align 4
  %9 = sub nsw i32 %8, 1
  %10 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([33 x i8], [33 x i8]* @.str.4, i64 0, i64 0), i32 {}, i32 %9)
  call void @exit(i32 2) #3
  unreachable

11:
  %12 = load i8**, i8*** %3, align 8
{}
  call void @__main({})
  ret i32 0
}}
"""

def get_argv(i, t):
    """ Return LLVM code to get argv[i], convert, and store in %ai
        i: index needed
        t: 'int' or 'bool'
    """
    if t == 'int':
        return """
  %t{}_0 = getelementptr inbounds i8*, i8** %12, i64 {}
  %t{}_1 = load i8*, i8** %t{}_0, align 8
  %a{} = call i64 @atol(i8* %t{}_1)
  """.format(i, i+1, i, i, i, i)
    else:
        return """
  %t{}_0 = getelementptr inbounds i8*, i8** %12, i64 {}
  %t{}_1 = load i8*, i8** %t{}_0, align 8
  %t{}_2 = call i32 @btoi(i8* %t{}_1)
  %a{} = trunc i32 %t{}_2 to i1
  """.format(i, i+1, i, i, i, i, i, i)

def emit_main(main_args):
    """Process command line args and call bril program's main, i.e., __main
    """
    arg_setup = ''
    arg_list = []
    for i, arg in enumerate(main_args):
        arg_setup += get_argv(i, arg['type'])
        arg_list.append(ttype(arg['type']) + ' %a{}'.format(i))
    arg_list = ', '.join(arg_list)


    print(MAIN.format(len(main_args), len(main_args), arg_setup, arg_list))
