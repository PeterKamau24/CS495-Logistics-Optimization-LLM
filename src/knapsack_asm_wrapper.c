/**
 * C Wrapper for Assembly Brute Force Knapsack Solver
 *
 * This wrapper provides file I/O and timing functionality for the
 * x86-64 Assembly implementation of the knapsack brute force algorithm.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

// External Assembly function
extern int64_t knapsack_brute_force_asm(int* weights, int* values, int n, int capacity);

typedef struct {
    int n_items;
    int capacity;
    int* weights;
    int* values;
} KnapsackInstance;

typedef struct {
    int max_value;
    double time_seconds;
} Solution;

/**
 * Read knapsack instance from file
 */
KnapsackInstance read_instance(const char* filepath) {
    KnapsackInstance inst;
    FILE* file = fopen(filepath, "r");

    if (!file) {
        fprintf(stderr, "Error: Could not open file %s\n", filepath);
        exit(1);
    }

    // Read first line: n_items capacity
    if (fscanf(file, "%d %d", &inst.n_items, &inst.capacity) != 2) {
        fprintf(stderr, "Error: Invalid file format\n");
        exit(1);
    }

    // Allocate arrays
    inst.weights = (int*)malloc(inst.n_items * sizeof(int));
    inst.values = (int*)malloc(inst.n_items * sizeof(int));

    if (!inst.weights || !inst.values) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }

    // Read weights
    for (int i = 0; i < inst.n_items; i++) {
        if (fscanf(file, "%d", &inst.weights[i]) != 1) {
            fprintf(stderr, "Error: Failed to read weight %d\n", i);
            exit(1);
        }
    }

    // Read values
    for (int i = 0; i < inst.n_items; i++) {
        if (fscanf(file, "%d", &inst.values[i]) != 1) {
            fprintf(stderr, "Error: Failed to read value %d\n", i);
            exit(1);
        }
    }

    fclose(file);
    return inst;
}

/**
 * Free instance memory
 */
void free_instance(KnapsackInstance* inst) {
    free(inst->weights);
    free(inst->values);
}

/**
 * Solve instance using Assembly implementation
 */
Solution solve_instance(const char* filepath, int verbose) {
    Solution sol;
    KnapsackInstance inst = read_instance(filepath);

    if (verbose) {
        printf("\n============================================================\n");
        printf("Solving instance: %s\n", filepath);
        printf("============================================================\n");
        printf("Number of items: %d\n", inst.n_items);
        printf("Capacity: %d\n", inst.capacity);
        printf("Total combinations to evaluate: %lld\n", 1LL << inst.n_items);
    }

    // Time the Assembly solver
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    int64_t max_value = knapsack_brute_force_asm(
        inst.weights,
        inst.values,
        inst.n_items,
        inst.capacity
    );

    clock_gettime(CLOCK_MONOTONIC, &end);

    // Calculate elapsed time
    sol.time_seconds = (end.tv_sec - start.tv_sec) +
                       (end.tv_nsec - start.tv_nsec) / 1e9;
    sol.max_value = (int)max_value;

    if (verbose) {
        printf("\n------------------------------------------------------------\n");
        printf("SOLUTION\n");
        printf("------------------------------------------------------------\n");
        printf("Optimal value: %d\n", sol.max_value);
        printf("------------------------------------------------------------\n");
        printf("Computation time: %.6f seconds\n", sol.time_seconds);
        printf("============================================================\n\n");
    }

    free_instance(&inst);
    return sol;
}

/**
 * Main entry point
 */
int main(int argc, char** argv) {
    const char* instance_files[] = {
        "notebooks/plan_md_instance.txt",
        "notebooks/instance_n10.txt",
        "notebooks/instance_n15.txt",
        "notebooks/instance_n20.txt",
        "notebooks/instance_n22.txt",
        "notebooks/instance_n25.txt"
    };
    int n_instances = 6;

    printf("\n============================================================\n");
    printf("0-1 KNAPSACK PROBLEM - BRUTE FORCE SOLVER (x86-64 ASM)\n");
    printf("============================================================\n");

    // Store results
    Solution* results = (Solution*)malloc(n_instances * sizeof(Solution));
    int* n_items_list = (int*)malloc(n_instances * sizeof(int));
    int count = 0;

    for (int i = 0; i < n_instances; i++) {
        FILE* test = fopen(instance_files[i], "r");
        if (test) {
            fclose(test);

            // Get n_items for summary
            KnapsackInstance inst = read_instance(instance_files[i]);
            n_items_list[count] = inst.n_items;
            free_instance(&inst);

            // Solve
            results[count] = solve_instance(instance_files[i], 1);
            count++;
        } else {
            printf("File not found: %s\n\n", instance_files[i]);
        }
    }

    // Summary table
    if (count > 0) {
        printf("\n============================================================\n");
        printf("SUMMARY\n");
        printf("============================================================\n");
        printf("%-25s %-4s %-8s %-12s\n", "Instance", "n", "Opt Val", "Time (s)");
        printf("------------------------------------------------------------\n");

        for (int i = 0; i < count; i++) {
            // Extract filename
            const char* filename = instance_files[i];
            const char* slash = strrchr(filename, '/');
            if (slash) filename = slash + 1;

            printf("%-25s %-4d %-8d %-12.6f\n",
                   filename,
                   n_items_list[i],
                   results[i].max_value,
                   results[i].time_seconds);
        }
        printf("============================================================\n\n");
    }

    free(results);
    free(n_items_list);
    return 0;
}
