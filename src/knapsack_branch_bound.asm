; ==============================================================================
; Branch and Bound Solver for 0-1 Knapsack Problem in x86-64 Assembly (NASM)
;
; Replaces the O(2^n) brute force enumeration with a DFS Branch and Bound
; search guided by a linear (LP) relaxation upper bound.
;
; The C wrapper pre-sorts items by value/weight ratio descending, so the
; greedy fractional fill walked here is also the LP relaxation optimum.
;
; Algorithm (recursive, via call/ret):
;     branch(level, cur_weight, cur_value):
;         if cur_value > best_value: best_value = cur_value
;         if level == n: return
;         bound = cur_value + integer-floor LP fill of items [level..n)
;         if bound <= best_value: return                (PRUNE)
;         if cur_weight + W[level] <= capacity:
;             branch(level+1, cw + W[level], cv + V[level])  (INCLUDE)
;         branch(level+1, cw, cv)                            (EXCLUDE)
;
; Integer bound is floor(LP optimum); valid because the integer optimum
; is bounded above by the LP optimum, and any integer <= LP is bounded
; above by floor(LP) as well.
;
; Calling Convention: Microsoft x64 ABI (Windows)
;   Args:           RCX, RDX, R8, R9, then stack
;   Volatile:       RAX, RCX, RDX, R8, R9, R10, R11
;   Non-volatile:   RBX, RBP, RDI, RSI, R12-R15
;   Shadow space:   32 bytes reserved by caller above its return address
;   Stack alignment: 16-byte aligned BEFORE the CALL instruction
; ==============================================================================

section .text
global knapsack_branch_bound_asm

; ------------------------------------------------------------------------------
; Register layout across the whole solve (callee-saved "globals"):
;   R12  = sorted weights pointer
;   R13  = sorted values pointer
;   R14d = n
;   R15d = capacity
;   EBX  = best_value
; Scratch (volatile): RAX, R10, R11
; Internal recursion args (in RCX, RDX, R8): level, cw, cv
; ------------------------------------------------------------------------------

; int64_t knapsack_branch_bound_asm(int* W, int* V, int n, int capacity)
;   RCX=W, RDX=V, R8d=n, R9d=capacity   (Win64)
;   returns: RAX = best value
knapsack_branch_bound_asm:
    push    rbp
    mov     rbp, rsp
    push    rbx
    push    r12
    push    r13
    push    r14
    push    r15
    sub     rsp, 40             ; 32 shadow space + 8 keeps 16-byte alignment

    mov     r12, rcx            ; W
    mov     r13, rdx            ; V
    mov     r14d, r8d           ; N
    mov     r15d, r9d           ; capacity
    xor     ebx, ebx            ; best_value = 0

    ; branch(level=0, cw=0, cv=0)
    xor     ecx, ecx
    xor     edx, edx
    xor     r8d, r8d
    call    bb_branch

    mov     eax, ebx            ; return best_value
    cdqe                        ; sign-extend to RAX

    add     rsp, 40
    pop     r15
    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret

; ------------------------------------------------------------------------------
; Recursive branch function.
;   RCX = level
;   RDX = cur_weight
;   R8  = cur_value
; Reads globals R12, R13, R14d, R15d. Updates EBX.
;
; Stack frame layout after prologue (rbp-relative):
;   [rbp-8]   level
;   [rbp-16]  cw
;   [rbp-24]  cv
;   [rbp-32..rbp-63]  shadow space (32 bytes) for the recursive call
; Total local: 64 bytes (sub rsp, 64)
; ------------------------------------------------------------------------------
bb_branch:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 64

    mov     [rbp-8],  rcx       ; level
    mov     [rbp-16], rdx       ; cw
    mov     [rbp-24], r8        ; cv

    ; Update incumbent if current node value beats best
    cmp     r8d, ebx
    jle     .no_update
    mov     ebx, r8d
.no_update:

    ; Leaf check: level == N
    cmp     ecx, r14d
    je      .ret

    ; --- Integer LP-relaxation upper bound ---
    ;   bound (eax) = cv
    ;   rem   (r9d) = cap - cw
    ;   i     (r10d) = level
    mov     eax, r8d
    mov     r9d, r15d
    sub     r9d, edx
    mov     r10d, ecx

.bound_loop:
    cmp     r10d, r14d
    jge     .bound_check
    mov     r11d, [r12 + r10*4]     ; W[i]
    mov     ecx,  [r13 + r10*4]     ; V[i]  (reuse ECX as scratch)
    cmp     r11d, r9d               ; W[i] <= rem?
    jg      .bound_frac
    add     eax, ecx                ; bound += V[i]
    sub     r9d, r11d               ; rem -= W[i]
    inc     r10d
    jmp     .bound_loop

.bound_frac:
    ; bound += (V[i] * rem) / W[i]   (floor, integer)
    ; ECX = V[i], R9d = rem, R11d = W[i]
    ; IDIV clobbers EDX:EAX. Save EAX (running bound) first.
    push    rax
    mov     eax, ecx
    cdq                             ; sign-extend EAX -> EDX:EAX
    imul    r9d                     ; EDX:EAX = V[i] * rem
    idiv    r11d                    ; EAX = quotient
    mov     r10d, eax               ; r10d reused as fractional contribution
    pop     rax
    add     eax, r10d

.bound_check:
    cmp     eax, ebx
    jle     .ret                    ; prune

    ; --- Reload args (volatile registers were trashed during bound calc) ---
    mov     rcx, [rbp-8]            ; level
    mov     rdx, [rbp-16]           ; cw
    mov     r8,  [rbp-24]           ; cv

    ; --- INCLUDE branch (try first; sorted order makes it greedy) ---
    mov     r10d, [r12 + rcx*4]     ; W[level]
    mov     r11d, edx
    add     r11d, r10d              ; cw + W[level]
    cmp     r11d, r15d              ; > capacity?
    jg      .exclude

    mov     eax, [r13 + rcx*4]      ; V[level]
    add     r8d, eax                ; cv + V[level]
    inc     rcx                     ; level + 1
    mov     edx, r11d               ; cw + W[level]
    call    bb_branch

.exclude:
    mov     rcx, [rbp-8]
    mov     rdx, [rbp-16]
    mov     r8,  [rbp-24]
    inc     rcx                     ; level + 1
    call    bb_branch

.ret:
    mov     rsp, rbp
    pop     rbp
    ret
