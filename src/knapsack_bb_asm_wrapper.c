/**
 * C Wrapper for Assembly Branch and Bound Knapsack Solver
 *
 * Responsibilities:
 *   1. Read knapsack instance from file.
 *   2. Sort items by value/weight ratio descending (the ASM solver
 *      assumes sorted input — the greedy fractional bound is only an
 *      LP-relaxation upper bound when items are sorted by ratio).
 *   3. Time the call to knapsack_branch_bound_asm.
 *   4. Print results, mirroring the brute force wrapper's format.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

// External Assembly function. Inputs must be pre-sorted by V/W descending.
extern int64_t knapsack_branch_bound_asm(int* weights, int* values, int n, int capacity);

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

KnapsackInstance read_instance(const char* filepath) {
    KnapsackInstance inst;
    FILE* file = fopen(filepath, "r");
    if (!file) {
        fprintf(stderr, "Error: Could not open file %s\n", filepath);
        exit(1);
    }

    if (fscanf(file, "%d %d", &inst.n_items, &inst.capacity) != 2) {
        fprintf(stderr, "Error: Invalid file format\n");
        exit(1);
    }

    inst.weights = (int*)malloc(inst.n_items * sizeof(int));
    inst.values  = (int*)malloc(inst.n_items * sizeof(int));
    if (!inst.weights || !inst.values) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }

    for (int i = 0; i < inst.n_items; i++) {
        if (fscanf(file, "%d", &inst.weights[i]) != 1) {
            fprintf(stderr, "Error: Failed to read weight %d\n", i);
            exit(1);
        }
    }
    for (int i = 0; i < inst.n_items; i++) {
        if (fscanf(file, "%d", &inst.values[i]) != 1) {
            fprintf(stderr, "Error: Failed to read value %d\n", i);
            exit(1);
        }
    }

    fclose(file);
    return inst;
}

void free_instance(KnapsackInstance* inst) {
    free(inst->weights);
    free(inst->values);
}

// Comparator-friendly view of an item.
typedef struct { int w; int v; } Item;

static int cmp_by_ratio_desc(const void* a, const void* b) {
    const Item* ia = (const Item*)a;
    const Item* ib = (const Item*)b;
    // Avoid division: a.v/a.w > b.v/b.w  <=>  a.v*b.w > b.v*a.w   (all > 0)
    long long lhs = (long long)ia->v * ib->w;
    long long rhs = (long long)ib->v * ia->w;
    if (lhs > rhs) return -1;
    if (lhs < rhs) return  1;
    return 0;
}

Solution solve_instance(const char* filepath, int verbose) {
    Solution sol;
    KnapsackInstance inst = read_instance(filepath);

    // Sort by value/weight descending (required by the ASM bound).
    Item* items = (Item*)malloc(inst.n_items * sizeof(Item));
    int*  sw    = (int*) malloc(inst.n_items * sizeof(int));
    int*  sv    = (int*) malloc(inst.n_items * sizeof(int));
    if (!items || !sw || !sv) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    for (int i = 0; i < inst.n_items; i++) {
        items[i].w = inst.weights[i];
        items[i].v = inst.values[i];
    }
    qsort(items, inst.n_items, sizeof(Item), cmp_by_ratio_desc);
    for (int i = 0; i < inst.n_items; i++) {
        sw[i] = items[i].w;
        sv[i] = items[i].v;
    }
    free(items);

    if (verbose) {
        printf("\n============================================================\n");
        printf("Solving instance: %s\n", filepath);
        printf("============================================================\n");
        printf("Number of items: %d\n", inst.n_items);
        printf("Capacity: %d\n", inst.capacity);
    }

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    int64_t max_value = knapsack_branch_bound_asm(sw, sv, inst.n_items, inst.capacity);

    clock_gettime(CLOCK_MONOTONIC, &end);

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

    // Last line: machine-readable "<value> <time>" for the benchmark parser.
    printf("%d %.9f\n", sol.max_value, sol.time_seconds);

    free(sw);
    free(sv);
    free_instance(&inst);
    return sol;
}

int main(int argc, char** argv) {
    if (argc == 2) {
        solve_instance(argv[1], 1);
        return 0;
    }

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
    printf("0-1 KNAPSACK PROBLEM - BRANCH AND BOUND (x86-64 ASM)\n");
    printf("============================================================\n");

    Solution* results = (Solution*)malloc(n_instances * sizeof(Solution));
    int* n_items_list = (int*)malloc(n_instances * sizeof(int));
    int count = 0;

    for (int i = 0; i < n_instances; i++) {
        FILE* test = fopen(instance_files[i], "r");
        if (test) {
            fclose(test);
            KnapsackInstance inst = read_instance(instance_files[i]);
            n_items_list[count] = inst.n_items;
            free_instance(&inst);

            results[count] = solve_instance(instance_files[i], 1);
            count++;
        } else {
            printf("File not found: %s\n\n", instance_files[i]);
        }
    }

    if (count > 0) {
        printf("\n============================================================\n");
        printf("SUMMARY\n");
        printf("============================================================\n");
        printf("%-25s %-4s %-8s %-12s\n", "Instance", "n", "Opt Val", "Time (s)");
        printf("------------------------------------------------------------\n");
        for (int i = 0; i < count; i++) {
            const char* filename = instance_files[i];
            const char* slash = strrchr(filename, '/');
            if (slash) filename = slash + 1;

            printf("%-25s %-4d %-8d %-12.6f\n",
                   filename, n_items_list[i],
                   results[i].max_value, results[i].time_seconds);
        }
        printf("============================================================\n\n");
    }

    free(results);
    free(n_items_list);
    return 0;
}
