; ==============================================================================
; Brute Force Solver for 0-1 Knapsack Problem in ARM64 Assembly
;
; This implements a complete enumeration approach to solve the 0-1 knapsack.
; Time complexity: O(2^n) where n is the number of items.
; Space complexity: O(n) for storing the solution.
;
; The brute force approach evaluates all possible subsets of items (2^n combinations)
; and selects the one with maximum value that doesn't exceed the capacity constraint.
;
; Algorithm:
;     For each subset S ⊆ {0, 1, ..., n-1}:
;         if sum(weights[i] for i in S) ≤ capacity:
;             compute total_value = sum(values[i] for i in S)
;             track maximum value and corresponding subset
;
; Calling Convention: ARM64 AAPCS
; Arguments passed in: X0-X7
; ==============================================================================

.global _knapsack_brute_force_asm
.align 4

; Function: knapsack_brute_force_asm
; Args:
;   X0 = int* weights (pointer to weights array)
;   X1 = int* values (pointer to values array)
;   X2 = int n (number of items)
;   X3 = int capacity
; Returns:
;   X0 = maximum value found
;
_knapsack_brute_force_asm:
    // Save callee-saved registers
    stp     x29, x30, [sp, #-64]!
    stp     x19, x20, [sp, #16]
    stp     x21, x22, [sp, #32]
    stp     x23, x24, [sp, #48]
    mov     x29, sp

    // Save arguments
    mov     x19, x0              // x19 = weights pointer
    mov     x20, x1              // x20 = values pointer
    mov     x21, x2              // x21 = n (number of items)
    mov     x22, x3              // x22 = capacity

    // Initialize best solution
    mov     w23, #0              // w23 = max_value = 0

    // Calculate 2^n (total number of subsets)
    mov     x10, #1
    lsl     x10, x10, x21        // x10 = 2^n (total subsets)

    mov     x11, #0              // x11 = subset_mask = 0

subset_loop:
    cmp     x11, x10             // if subset_mask >= 2^n
    b.ge    done                 // exit loop

    // Evaluate current subset
    mov     w12, #0              // w12 = total_weight = 0
    mov     w13, #0              // w13 = total_value = 0

    // Inner loop: decode binary representation
    mov     x14, #0              // x14 = item_idx = 0

item_loop:
    cmp     x14, x21             // if item_idx >= n
    b.ge    check_feasibility    // exit inner loop

    // Check if bit item_idx is set in subset_mask
    mov     x15, #1
    lsl     x15, x15, x14        // x15 = 1 << item_idx
    tst     x11, x15             // test if bit is set
    b.eq    next_item            // skip if not set

    // Add weight and value for this item
    lsl     x16, x14, #2         // x16 = item_idx * 4 (sizeof(int))

    ldr     w17, [x19, x16]      // w17 = weights[item_idx]
    add     w12, w12, w17        // total_weight += weights[item_idx]

    ldr     w17, [x20, x16]      // w17 = values[item_idx]
    add     w13, w13, w17        // total_value += values[item_idx]

next_item:
    add     x14, x14, #1         // item_idx++
    b       item_loop

check_feasibility:
    // Check if total_weight <= capacity and total_value > max_value
    cmp     w12, w22             // total_weight <= capacity?
    b.gt    next_subset          // skip if too heavy

    cmp     w13, w23             // total_value > max_value?
    b.le    next_subset          // skip if not better

    // Update best solution
    mov     w23, w13             // max_value = total_value

next_subset:
    add     x11, x11, #1         // subset_mask++
    b       subset_loop

done:
    // Return max_value
    mov     w0, w23

    // Restore callee-saved registers
    ldp     x23, x24, [sp, #48]
    ldp     x21, x22, [sp, #32]
    ldp     x19, x20, [sp, #16]
    ldp     x29, x30, [sp], #64
    ret
