# Homework 3: Translating Bril SSA to LLVM IR

## Overview

In this homework, you will implement a translator that converts a Bril program in SSA form into LLVM IR. The goal is to produce a valid LLVM IR program that can be executed using lli, and whose output matches that of the original Bril program when executed with brili. You will build upon your SSA construction from Homework 2 and focus on the translation process to LLVM IR.

## Prerequisites

- Python 3.7+
- llvm 17.0.0+
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

3. Copy Your SSA Implementation from Homework 2:
- **Copy your implementations from Homework 2 into the `src/` directory.** This should include your SSA construction code and any other supporting files you created.
- Ensure that your SSA construction code works correctly, as you will build upon it in this assignment.

## Project Structure
```
homework-directory/
├── src/
│   ├── driver.py
│   ├── bril.py
│   ├── cfg.py
│   ├── dominance.py
│   ├── ssa_construct.py
│   ├── ssa_to_llvm.py
│   └── [other source files]
├── tests/
│   ├── loop.bril
│   └── [additional test cases]
├── bril/
├── install_bril.sh
├── run_test_case.sh
├── student_id.txt
└── README.md
```


## Implementation Tasks

1. LLVM IR Generation (`ssa_to_llvm.py`):
- Implement a translator that takes a Bril program in SSA form and outputs equivalent LLVM IR.
- Ensure that the generated LLVM IR is compatible with LLVM version 17.

## Running and Testing

1. Generate LLVM IR from a Bril Program:
```bash
bril2json < ./tests/[your_test_program].bril | python3 ./src/driver.py > output.ll
```
2. Execute the Original Bril Program:
```bash
bril2json < ./tests/[your_test_program].bril | brili [arguments] > original.out
```
3. Execute the LLVM IR Program:
```bash
lli output.ll [arguments] > transformed.out
```
4. Compare the outputs:
```bash
diff original.out transformed.out
```
The outputs should match exactly if your translation is correct.

## Submission Instructions

1. Open `student_id.txt` and replace the placeholder with your actual student ID.
2. Implement all required functionalities in the `src/` directory, focusing on `ssa_to_llvm.py`.
3. Test your implementation thoroughly.
4. Commit and push your changes:
   ```bash
   git add src/ student_id.txt
   git commit -m "Completed Homework 3"
   git push origin main
   ```
5. Verify that the GitHub Actions workflow passes all tests.

## Do and Don't

- You are allowed to modify any part of the starter code within the src/ directory to suit your approach.
- Make sure you have a solid understanding of LLVM IR and its mapping from Bril IR before starting your implementation.
- Ensure your student ID is correctly entered in the student_id.txt file before submission.
- DO NOT modify anything outside the src/ directory except student_id.txt. Any such changes will be considered cheating.

## Additional Resources

- [LLVM Language Reference Manual](https://llvm.org/docs/LangRef.html)
- [Bril Language Reference](https://capra.cs.cornell.edu/bril/lang/index.html)
