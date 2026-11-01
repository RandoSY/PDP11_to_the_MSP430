; ============================================================================
; DAY 1: MAKE A NOMINAL 1 kHz SIGNAL WITH AN MSP430G2553
; ============================================================================
; The goal is to make something real and measurable on the first day.
; Timer_A generates a square wave on P1.6 (TA0.1). On the lab board this is
; J2 pin 7. The Pico W meter measures it on GP3, physical pin 5. Connect the
; two boards' grounds as described in README.md before taking a measurement.
;
; A square-wave cycle has one high and one low half. We set up the timer to
; toggle the output once every 500 clock ticks. With a nominal 1 MHz clock:
;
;     1,000,000 ticks/second / (500 ticks/toggle * 2 toggles/cycle)
;       = 1,000 cycles/second = 1 kHz nominal.
;
; The DCO clock is factory-calibrated, not a precision frequency reference.
; The actual signal and meter reading may differ from 1,000 Hz.
;
; Reading this assembly:
;   ';' starts a comment. The assembler ignores everything after it on a line.
;   A label such as RESET: names a location in the program.
;   '.b' means operate on a byte (8 bits); '.w' means a word (16 bits).
;   '#value' means an immediate value, such as the number 499 itself.
;   '&name' means the byte or word stored at the absolute address named name.
;   Source comes first and destination second: MOV source, destination.
;   The symbol '|' combines independent bit settings into one value.
; The names of hardware registers and bit settings come from TI's device file.
;
; These are TI assembler directives, not instructions executed by the CPU.
    .cdecls C,LIST,"msp430g2553.h" ; import register names and bit constants
    .text                         ; put the following program in the code section
    .retain                       ; keep this section when the linker builds it
    .retainrefs                   ; retain sections referenced by this section
    .global RESET                 ; make RESET visible as the linker entry point

; The reset vector at the bottom of this file tells the MCU to start here.
RESET:
    ; The G2553's RAM occupies addresses 0x0200 through 0x03FF. The stack
    ; grows downward, so initialize the stack pointer to 0x0400, just above RAM.
    mov.w   #0x0400, SP

    ; The watchdog automatically resets the chip unless serviced. For this
    ; small first exercise, stop it. WDTCTL requires the password WDTPW when
    ; written; WDTHOLD is the bit that stops the watchdog timer.
    mov.w   #(WDTPW|WDTHOLD), &WDTCTL

    ; The factory stores two 1 MHz DCO calibration bytes in information flash.
    ; An erased byte reads 0xFF. CMP compares without changing the byte, and
    ; JEQ jumps if the comparison was equal. If either byte is erased, stop:
    ; we cannot honestly assume the intended clock setting is available.
    cmp.b   #0xFF, &CALBC1_1MHZ
    jeq     calibration_missing
    cmp.b   #0xFF, &CALDCO_1MHZ
    jeq     calibration_missing

    ; Configure the digitally controlled oscillator (DCO) near 1 MHz.
    ; Clear DCOCTL first, then load the factory settings into BCSCTL1 and
    ; DCOCTL. These instructions READ the calibration bytes; they do not write
    ; to information flash. The 'build/program' instructions use ERASE_MAIN
    ; specifically to preserve that calibration area.
    mov.b   #0, &DCOCTL
    mov.b   &CALBC1_1MHZ, &BCSCTL1
    mov.b   &CALDCO_1MHZ, &DCOCTL

    ; BCSCTL2 = 0 selects the DCO for SMCLK with a divide-by-one setting.
    ; SMCLK is the peripheral clock that will advance Timer_A.
    mov.b   #0, &BCSCTL2

    ; Configure the P1.6 pin to output the timer signal. BIT6 is the bit mask
    ; for bit 6, or 0x40. BIC clears selected bits; BIS sets selected bits.
    ; Unlike writing a whole register, these operations leave other bits alone.
    bic.b   #BIT6, &P1SEL2        ; P1SEL2.6 = 0: select timer, not I2C
    bis.b   #BIT6, &P1DIR         ; P1DIR.6 = 1: configure P1.6 as an output
    bis.b   #BIT6, &P1SEL         ; P1SEL.6 = 1: connect TA0.1 to that pin

    ; Timer_A runs in 'up mode': its count goes from 0 through TA0CCR0,
    ; inclusive, then starts again at 0. Thus 499 gives 500 ticks per count
    ; cycle. TA0CCR1 = 250 produces one comparison in each count cycle.
    mov.w   #499, &TA0CCR0
    mov.w   #250, &TA0CCR1

    ; OUTMOD_4 tells capture/compare channel 1 to toggle its output at each
    ; TA0CCR1 match. One timer cycle is one HALF of the output square wave:
    ; every other toggle returns the signal to its original level.
    mov.w   #OUTMOD_4, &TA0CCTL1

    ; Start Timer_A: TASSEL_2 chooses SMCLK, MC_1 chooses up mode, and TACLR
    ; clears the timer counter and divider as the timer is started. Interrupts
    ; are not needed: the timer peripheral changes the output by itself.
    mov.w   #(TASSEL_2|MC_1|TACLR), &TA0CTL

running:
    ; JMP branches to the named label. The CPU waits here forever while the
    ; timer continues generating the square wave in hardware.
    jmp     running

calibration_missing:
    ; Reaching this loop means at least one factory calibration byte was FF.
    ; The program stops before enabling the timer output. It does not recover
    ; those values. Investigate calibration before using it as a 1 kHz source.
    jmp     calibration_missing

    ; On reset, the MSP430 reads a 16-bit start address from its reset vector.
    ; The linker places this section at 0xFFFE; .short stores the RESET address
    ; there. This is a linker directive and data, not a CPU instruction.
    .sect   ".reset"
    .short  RESET
