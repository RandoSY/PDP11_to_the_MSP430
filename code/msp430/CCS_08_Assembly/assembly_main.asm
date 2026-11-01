; Standalone wrapper for the book's register-loop fragment.
    .text
    .global main
main:
    MOV.W #0x5A80, &0x0120 ; stop watchdog before stepping
    MOV.W #5, R4
    CLR.W R5
loop:
    ADD.W R4, R5
    DEC.W R4
    JNZ loop
done:
    JMP done
