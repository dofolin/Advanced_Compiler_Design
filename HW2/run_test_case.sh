#!/bin/bash
# Usage: ./run_test_case.sh test_file

TEST_FILE="$1"

if [ ! -f student_id.txt ]; then
  echo "student_id.txt not found. Cannot proceed with testing."
  exit 1
fi

STUDENT_ID=$(cat student_id.txt)

SEED=$(echo -n "$STUDENT_ID" | sha256sum | cut -c1-16)
PYTHON_SEED="${SEED}"

ARGS_LINE=$(head -n 1 "$TEST_FILE")
ARGS=""
NUM_ARGS=0
if echo "$ARGS_LINE" | grep -q '^# ARGS:'; then
  ARGS_SPEC=$(echo "$ARGS_LINE" | sed 's/^# ARGS://')
  NUM_ARGS=$(echo "$ARGS_SPEC" | wc -w)
  ARGS=$(python3 -c "
import random
random.seed(int('$PYTHON_SEED',16))
print(' '.join([str(random.randint(100,1000)) for _ in range($NUM_ARGS)]))
")
fi

BASENAME=$(basename "$TEST_FILE" .bril)
OUTPUT_BIL="output_${BASENAME}.bril"
ORIGINAL_OUT="original_${BASENAME}.out"
TRANSFORMED_OUT="transformed_${BASENAME}.out"

bril2json < "$TEST_FILE" | python3 ./src/driver.py | bril2txt > "$OUTPUT_BIL"
if [ $? -ne 0 ]; then
  echo "Error transforming $TEST_FILE"
  rm -f "$OUTPUT_BIL"
  exit 1
fi

bril2json < "$OUTPUT_BIL" | python3 src/is_ssa.py
if [ $? -ne 0 ]; then
  echo "Transformed program is not in SSA form for $TEST_FILE"
  rm -f "$OUTPUT_BIL"
  exit 1
fi

if [ -z "$ARGS" ]; then
  bril2json < "$TEST_FILE" | brili > "$ORIGINAL_OUT"
else
  bril2json < "$TEST_FILE" | brili $ARGS > "$ORIGINAL_OUT"
fi

if [ $? -ne 0 ]; then
  echo "Error running original program $TEST_FILE with arguments $ARGS"
  rm -f "$OUTPUT_BIL" "$ORIGINAL_OUT"
  exit 1
fi

if [ -z "$ARGS" ]; then
  bril2json < "$OUTPUT_BIL" | brili > "$TRANSFORMED_OUT"
else
  bril2json < "$OUTPUT_BIL" | brili $ARGS > "$TRANSFORMED_OUT"
fi

if [ $? -ne 0 ]; then
  echo "Error running transformed program $OUTPUT_BIL with arguments $ARGS"
  rm -f "$OUTPUT_BIL" "$ORIGINAL_OUT" "$TRANSFORMED_OUT"
  exit 1
fi

diff "$ORIGINAL_OUT" "$TRANSFORMED_OUT"
if [ $? -ne 0 ]; then
  echo "Outputs do not match for $TEST_FILE"
  rm -f "$OUTPUT_BIL" "$ORIGINAL_OUT" "$TRANSFORMED_OUT"
  exit 1
fi

echo "Test $TEST_FILE passed"

rm -f "$OUTPUT_BIL" "$ORIGINAL_OUT" "$TRANSFORMED_OUT"