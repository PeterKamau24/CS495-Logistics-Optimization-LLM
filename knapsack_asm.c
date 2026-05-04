// =============================================================
// knapsack_asm.c
// 0-1 Knapsack brute force with the inner subset-evaluation
// loop written in x86-64 inline assembly (AT&T syntax).
//
// This shows what "low-level" really looks like: registers,
// instructions, no abstractions. The C code only handles I/O
// and calls the asm routine.
//
// Capstone: LLM-Assisted Generation of Low-Level Discrete
// Optimization Solvers
// =============================================================
//
// Compile: gcc -O0 -std=c11 knapsack_asm.c -o knapsack_asm
// Run:     ./knapsack_asm <input_file>
//
// Note: -O0 is used so the compiler does not optimise away the
// inline asm. In real low-level code you'd hand-tune further.
// =============================================================

#define _POSIX_C_SOURCE 199309L

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

/*
 * eval_subset_asm
 *
 * Given a bitmask describing which items are in the subset,
 * compute total_weight and total_value using x86-64 assembly.
 *
 * Inputs:
 *   mask    - 64-bit bitmask of selected items
 *   n       - number of items
 *   weights - pointer to weights array (int64_t)
 *   values  - pointer to values  array (int64_t)
 *   out_w   - pointer to total weight output
 *   out_v   - pointer to total value  output
 *
 * The assembly loop iterates i = 0..n-1, tests bit i of the mask,
 * and conditionally adds weights[i] and values[i] to the running
 * totals. We use cmovne to keep the loop branch-free for the add.
 */
static inline void eval_subset_asm(uint64_t mask, int n,
                                   const int64_t* weights,
                                   const int64_t* values,
                                   int64_t* out_w, int64_t* out_v) {
    int64_t total_w = 0;
    int64_t total_v = 0;

    __asm__ volatile (
        "xorq %%r10, %%r10              \n\t"  // i = 0
        "1:                             \n\t"  // loop_start:
        "   cmpq %[n], %%r10            \n\t"  // if i >= n, exit
        "   jge 2f                      \n\t"
        "   movq %[mask], %%r11         \n\t"  // r11 = mask
        "   movq %%r10, %%rcx           \n\t"  // rcx = i (shift count)
        "   shrq %%cl, %%r11            \n\t"  // r11 >>= i
        "   testq $1, %%r11             \n\t"  // bit i set?
        "   jz 3f                       \n\t"  // if 0, skip add
        "   movq (%[w], %%r10, 8), %%rax\n\t"  // rax = weights[i]
        "   addq %%rax, %[tw]           \n\t"  // total_w += weights[i]
        "   movq (%[v], %%r10, 8), %%rax\n\t"  // rax = values[i]
        "   addq %%rax, %[tv]           \n\t"  // total_v += values[i]
        "3:                             \n\t"  // skip:
        "   incq %%r10                  \n\t"  // i++
        "   jmp 1b                      \n\t"
        "2:                             \n\t"  // exit:
        : [tw] "+r" (total_w), [tv] "+r" (total_v)
        : [mask] "r" (mask), [n] "r" ((int64_t)n),
          [w] "r" (weights), [v] "r" (values)
        : "rax", "rcx", "r10", "r11", "cc", "memory"
    );

    *out_w = total_w;
    *out_v = total_v;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return 1;
    }

    FILE* fp = fopen(argv[1], "r");
    if (!fp) {
        fprintf(stderr, "Error: cannot open %s\n", argv[1]);
        return 1;
    }

    int n;
    int64_t capacity;
    fscanf(fp, "%d %ld", &n, &capacity);

    int64_t* weights = malloc(n * sizeof(int64_t));
    int64_t* values  = malloc(n * sizeof(int64_t));
    for (int i = 0; i < n; i++) fscanf(fp, "%ld", &weights[i]);
    for (int i = 0; i < n; i++) fscanf(fp, "%ld", &values[i]);
    fclose(fp);

    if (n > 25) {
        fprintf(stderr, "Warning: asm brute force is slow for n > 25.\n");
    }

    // ---- Brute force using asm inner routine ----
    struct timespec t_start, t_end;
    clock_gettime(CLOCK_MONOTONIC, &t_start);

    int64_t best_value = 0;
    uint64_t total_subsets = 1ULL << n;

    for (uint64_t mask = 0; mask < total_subsets; mask++) {
        int64_t total_w, total_v;
        eval_subset_asm(mask, n, weights, values, &total_w, &total_v);

        if (total_w <= capacity && total_v > best_value) {
            best_value = total_v;
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t_end);
    double elapsed = (t_end.tv_sec - t_start.tv_sec)
                   + (t_end.tv_nsec - t_start.tv_nsec) / 1e9;

    printf("%ld %.6f\n", best_value, elapsed);

    free(weights);
    free(values);
    return 0;
}
