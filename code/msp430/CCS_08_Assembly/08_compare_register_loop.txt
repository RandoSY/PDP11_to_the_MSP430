; TI-style MSP430 assembly fragment (not a standalone firmware image).
; R4 counts down 5..1, R5 accumulates 15 decimal.
        MOV.W   #5, R4
        CLR.W   R5
loop:   ADD.W   R4, R5
        DEC.W   R4
        JNZ     loop
; Place inside correct TI assembler source with reset/startup/linker vectors.
