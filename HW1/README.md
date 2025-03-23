# Homework 1: Affine-partitioned

## Overview

FOR j = 1 TO n

                 FOR i = 1 TO n

                        A[i,j] = A[i,j]+B[i-1,j];                       (S1)

                        B[i,j] = A[i,j-1]*B[i,j];                       (S2)

 (a) Is this program parallelizable that allows each core execute its own iteration? In Chinese, "這個程式可否透過 Affine Partition 來做平行化."

 (b) Systematically show how you generate the affine-partitioned code.