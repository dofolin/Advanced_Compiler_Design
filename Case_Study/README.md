# Case Study. DCE and LVN (Dead Code Elimination and Local Value Numbering) 

## Overview

1. Running the DCE (Dead Code Elimination) pass:

Just like the Slide 14 in Prof. Liao's slide deck for 10/11

Links to an external site.:

  $ bril2json < fizz-buzz.bril | python3 tdce.py | brili -p 5 // This DCE reduces the instruction count from 148 to 144.

You need to run commands and show both before and after. I.e., showing that running the pass "tdce" above indeed reduces the instruction count from before to after.

Turn in the screenshots that shows you reduce the instruction count from 148 to 144, for example. Of course, if you don't want the suggested fizz-buzz.bril, you can use other programs, but your result needs to be better than the fizz-buzz case above.

2. BRIL has a benchmark runner，
Please 使用這個一次量測多個programs的優化結果。
在bril/brench 下就有一個範例，跑完會得到所有 benchmarks下的程式使用 DCE and LVN 兩個優化後的結果，並比較前後的instructions個數輸出成一 csv file。

Read this documentation to learn how to use it:
https://capra.cs.cornell.edu/bril/tools/brench.html

Links to an external site.
Benchmark Runner - Bril: A Compiler Intermediate Representation for Learning (cornell.edu)

3. Briefly explain why LVN framework can handle DCE, CSE, copy propagation and constant propagation in the same LVN framework.