/*
 * knapsack_asm.c
 *
 * 0-1 Knapsack brute force solver with x86-64 inline assembly inner loop.
 * Reads instance from a text file, prints (optimal_value, elapsed_seconds).
 *
 * Compile with: gcc -O0 -std=c11 knapsack_asm.c -o knapsack_asm
 *
 * Capstone Project: LLM-Assisted Generation of Low-Level Discrete
 * Optimization Solvers. Author: Peter Kamau.
 */

#define _POSIX_C_SOURCE 199309L

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define MAX_N 30

/*
 * test_bit
 *
 * Inline x86-64 assembly. Given a 64-bit mask and a bit index i, return 1
 * if bit i is set in mask, otherwise 0. Uses BT (bit test) instruction
 * which sets the carry flag to the bit value, then SETC to materialize it.
 */
static inline int test_bit(uint64_t mask, int i) {
    int result;
    __asm__ volatile (
        "btq %2, %1\n\t"      /* CF = bit i of mask */
        "setc %b0\n\t"        /* low byte of result = CF */
        "movzbl %b0, %0\n\t"  /* zero-extend to full int */
        : "=r" (result)
        : "r" (mask), "r" ((uint64_t)i)
        : "cc"
    );
    return result;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return 1;
    }

    FILE *f = fopen(argv[1], "r");
    if (!f) {
        fprintf(stderr, "Cannot open %s\n", argv[1]);
        return 1;
    }

    int n, capacity;
    if (fscanf(f, "%d %d", &n, &capacity) != 2) {
        fprintf(stderr, "Bad input format\n");
        fclose(f);
        return 1;
    }
    if (n > MAX_N) {
        fprintf(stderr, "n too large (max %d)\n", MAX_N);
        fclose(f);
        return 1;
    }

    int weights[MAX_N], values[MAX_N];
    for (int i = 0; i < n; i++) fscanf(f, "%d", &weights[i]);
    for (int i = 0; i < n; i++) fscanf(f, "%d", &values[i]);
    fclose(f);

    struct timespec t_start, t_end;
    clock_gettime(CLOCK_MONOTONIC, &t_start);

    int best_value = 0;
    uint64_t total_subsets = (uint64_t)1 << n;

    for (uint64_t mask = 0; mask < total_subsets; mask++) {
        int total_w = 0;
        int total_v = 0;

        /* Inner loop: walk each item bit using inline asm bit test */
        for (int i = 0; i < n; i++) {
            if (test_bit(mask, i)) {
                total_w += weights[i];
                total_v += values[i];
            }
        }

        if (total_w <= capacity && total_v > best_value) {
            best_value = total_v;
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t_end);
    double elapsed = (t_end.tv_sec - t_start.tv_sec)
                   + (t_end.tv_nsec - t_start.tv_nsec) / 1e9;

    printf("%d %.6f\n", best_value, elapsed);
    return 0;
}
