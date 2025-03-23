# Homework 2: SSA Construction for Bril

## Overview

In this homework, you will implement the SSA construction algorithm for the Bril intermediate representation (IR). The goal is to transform a given non-SSA Bril program into its SSA form with considering the optimization of eliminating redundant ϕ-functions. You will work through several modular components, each building upon the previous to achieve the final SSA-form program.

## Prerequisites

- Python 3.7+
- Bril toolchain

## Getting Started

1. Clone the repository:
   ```bash
   git clone --recursive <url-of-your-forked-repo>
   ```

2. Navigate to the homework directory:
   ```bash
   cd <homework-directory>
   ```

## Project Structure
```
homework-directory/
├── src/
│ ├── driver.py
│ ├── bril.py
│ ├── cfg.py
│ ├── dominance.py
│ ├── is_ssa.py
│ └── ssa_construct.py
├── tests/
│ ├── simple.bril
│ └── [additional test cases]
├── bril/
├── install_bril.sh
├── run_test_case.sh
├── student_id.txt
└── README.md
```


## Implementation Tasks

1. CFG Construction (`cfg.py`)
2. Dominator Computation (`dominance.py`)
3. Phi-Function Insertion (`ssa_construct.py`)
4. Variable Renaming (`ssa_construct.py`)

## Running and Testing

1. To generate the SSA form of your program:
```bash
bril2json < ./tests/[your_test_program].bril | python3 ./src/driver.py | bril2txt > output.bril
```
2. To check if the generated program is in SSA form:
```bash
bril2json < ./output.bril | python3 src/is_ssa.py
```
3. To compare the execution output of the original and transformed programs:
```bash
# Original program
bril2json < ./tests/[your_test_program].bril | brili [arguments] > original.out

# Transformed SSA program
bril2json < ./output.bril | brili [arguments] > transformed.out

# Compare outputs
diff original.out transformed.out
```


## Submission Instructions

1. Open `student_id.txt` and replace the placeholder with your actual student ID.
2. Implement all required functionalities in the `src/` directory.
3. Test your implementation thoroughly.
4. Commit and push your changes:
   ```bash
   git add src/ student_id.txt
   git commit -m "Completed Homework 2"
   git push origin main
   ```
5. Verify that the GitHub Actions workflow passes all tests.

## Do and Don't

- You are allowed to modify any part of the starter code within the src/ directory, except for is_ssa.py, to suit your approach. While the current structure serves as a guideline, ensuring the driver script functions properly is key for grading.
- Make sure you have a solid understanding of the algorithm before starting your implementation.
- Ensure your student ID is correctly entered in the student_id.txt file before submission.
- DO NOT modify the src/is_ssa.py file or anything outside the src/ directory except student_id.txt. Any such changes will be considered cheating.

## Additional Resources

- Engineering a Compiler
- [Bril Language Reference](https://capra.cs.cornell.edu/bril/lang/index.html)
- Course lecture notes on SSA form and related algorithms
