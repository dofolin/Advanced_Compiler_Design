# llvm-pass-skeleton

LLVM pass for HW4.
r12631055

Build:

    $ cd ..
    $ mkdir build
    $ cd build
    $ cmake ..
    $ make
    $ cd ..

Run:

    $ clang -fpass-plugin=`echo build/skeleton/SkeletonPass.*` something.c
