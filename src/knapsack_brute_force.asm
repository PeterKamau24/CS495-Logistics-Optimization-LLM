; ==============================================================================
; Brute Force Solver for 0-1 Knapsack Problem in x86-64 Assembly (NASM)
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
; Calling Convention: System V AMD64 ABI (macOS/Linux)
; Arguments passed in: RDI, RSI, RDX, RCX, R8, R9
; ==============================================================================

section .text
global _knapsack_brute_force_asm

; Function: knapsack_brute_force_asm
; Args:
;   RDI = int* weights (pointer to weights array)
;   RSI = int* values (pointer to values array)
;   RDX = int n (number of items)
;   RCX = int capacity
; Returns:
;   RAX = maximum value found
;
_knapsack_brute_force_asm:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15

    ; Save arguments
    mov r12, rdi              ; r12 = weights pointer
    mov r13, rsi              ; r13 = values pointer
    mov r14, rdx              ; r14 = n (number of items)
    mov r15, rcx              ; r15 = capacity

    ; Initialize best solution
    xor r8, r8                ; r8 = max_value = 0

    ; Calculate 2^n (total number of subsets)
    mov rcx, 1
    mov rax, r14              ; n
    shl rcx, cl               ; rcx = 2^n (total subsets)

    xor rbx, rbx              ; rbx = subset_mask = 0

.subset_loop:
    cmp rbx, rcx              ; if subset_mask >= 2^n
    jge .done                 ; exit loop

    ; Evaluate current subset
    xor r9, r9                ; r9 = total_weight = 0
    xor r10, r10              ; r10 = total_value = 0

    ; Inner loop: decode binary representation
    xor rsi, rsi              ; rsi = item_idx = 0

.item_loop:
    cmp rsi, r14              ; if item_idx >= n
    jge .check_feasibility    ; exit inner loop

    ; Check if bit item_idx is set in subset_mask
    mov rax, 1
    mov rcx, rsi
    shl rax, cl               ; rax = 1 << item_idx
    test rbx, rax             ; test if bit is set
    jz .next_item             ; skip if not set

    ; Add weight and value for this item
    mov rdi, rsi
    shl rdi, 2                ; multiply by 4 (sizeof(int))

    mov eax, [r12 + rdi]      ; weights[item_idx]
    add r9d, eax              ; total_weight += weights[item_idx]

    mov eax, [r13 + rdi]      ; values[item_idx]
    add r10d, eax             ; total_value += values[item_idx]

.next_item:
    inc rsi                   ; item_idx++
    jmp .item_loop

.check_feasibility:
    ; Check if total_weight <= capacity and total_value > max_value
    cmp r9d, r15d             ; total_weight <= capacity?
    jg .next_subset           ; skip if too heavy

    cmp r10d, r8d             ; total_value > max_value?
    jle .next_subset          ; skip if not better

    ; Update best solution
    mov r8d, r10d             ; max_value = total_value

.next_subset:
    inc rbx                   ; subset_mask++
    jmp .subset_loop

.done:
    mov rax, r8               ; return max_value

    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret
