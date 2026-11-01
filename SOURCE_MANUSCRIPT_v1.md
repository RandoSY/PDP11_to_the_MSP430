# FROM THE PDP-11 TO THE MSP430
## Architecture, Industrial Automation, and the Art of Measuring a Computer

**An experimental course and working laboratory book**  
**First-edition technical manuscript • October 31, 2026**  
**PDP-11 historical reference • MSP430G2553 target • RP2040/Pico instrumentation • Python analysis**

> A computer is not understood merely because a program compiles. It is understood when we can predict its interaction with the world, observe that interaction, and explain the difference.

**Reader's notice.** This is an original educational manuscript built as an add-on to the October 29, 2026 *MSP430 Teacher & Operator Guide* and existing Day One project. It is not an official DEC, Texas Instruments, or Robert Krten publication. Historical material is interpretive, grounded in DEC-era handbooks; code marked *candidate* has not been compiled or tested on the target board during this edition. The exercises require supervised electrical checks. Host-side Python algorithm tests are included and pass.

---

# Preface — The instrument, the controller, and the historical question

In 1970, Digital Equipment Corporation introduced the PDP-11 to a world in which minicomputers were becoming practical instruments of science, manufacturing, and process control. Not every application demanded a mainframe. A smaller computer, equipped with a useful instruction set, memory, a modular I/O system, and software that responded to external events, could measure a physical process and participate in its control. That possibility reshaped laboratories and industrial engineering.

More than half a century later, a small MSP430G2553 microcontroller can reproduce many of the *conceptual* operations that made the PDP-11 attractive: read and write memory-mapped registers, respond to interrupts, perform arithmetic on sensor values, and act upon an event at a pin. The MSP430 is not a miniature PDP-11. The processors differ profoundly in bus architecture, resources, privilege models, peripheral arrangements, and operating environment. But they belong in a productive conversation about what a general-purpose instruction set can accomplish in the physical world.

This book places three machines in deliberate roles. The PDP-11 is the historical and architectural example, explored through documents and optional simulation. The MSP430G2553 is the physical target, with instructions, clocks, pins, and peripherals to understand. The RP2040/Pico is an observer and test instrument, not a substitute for the controlled device. The PC, using Python and familiar development tools, analyzes observations and produces engineering records.

The course adopts CAP: **Capture** raw observations with setup conditions; **Analyze** the calculations, limits, errors, and uncertainty; **Publish** enough information for somebody else to reproduce the work. The pedagogical sequence repeatedly begins with a prediction, then reveals a few relevant instructions, and only then moves to data.

The book is written for teachers, advanced learners, and practitioners who want to understand computers close to the hardware. It is also suitable for a self-directed bench course. A student does not need to know a PDP-11 before starting. A teacher does need the discipline to distinguish an example from an experiment and a measurement from an assertion.

## Conventions and evidence labels

**Historical example** means a representative concept or original source, not a claim that the identical code ran on a particular industrial installation. **Candidate firmware** means plausible target code requiring a specific compiler, linker setup, board pin map, and bench verification. **Host-tested** means the included Python algorithm unit tests were executed without microcontroller hardware. **Verified on bench** may be claimed only when the teacher or learner has preserved the actual programming log, wiring record, instrument configuration, and measurements.

Code listings use their own syntax; do not paste a PDP-11 listing into an MSP430 assembler. The user’s board pin assignments are treated as the proposed custom-board netlist, not universal MSP430 pin definitions. Unless stated otherwise, arithmetic exercises are examples, not actual readings.

## Course outcomes

By the end, a learner should be able to explain a processor register, decode an addressing mode, distinguish an instruction from a peripheral operation, map control bits to a physical pin, compare C with generated machine code, reason about interrupt deadlines, verify a 1-Wire transaction electrically, decode and check a sensor value, and publish a defensible control-system experiment. A student should also recognize that *historical similarity is not proof of direct architectural descent*.

---

# Part I — The industrial computer and its architecture

# Chapter 1 — Why the PDP-11 mattered in industrial automation

## 1.1 The industrial problem before the processor

Consider a tank whose contents must be held between two temperature limits. A human operator could periodically read a thermometer, note a change, and adjust a valve. But the process might demand decisions faster than an operator can make them, or it might require hundreds of simultaneous observations, each recorded and associated with a timestamp. Earlier solutions used electromechanical controllers, analog electronics, dedicated hardware, and specialized process computers. The broader industrial challenge was to make measurement, judgment, and action repeatable.

A programmable minicomputer changed the economics of this problem. One computing system could perform multiple algorithms in software, collect measurements, produce logs, supervise alarms, and be reconfigured without rewiring every decision. That did not abolish sensors, signal conditioning, relays, or safety interlocks. Rather, it made the control logic programmable within a larger engineered system. A computer earns its place in that system only when its failure modes and deadlines are understood.

DEC's PDP-11 family was a particularly influential example. It offered 16-bit computing, a useful and comparatively orthogonal instruction set, modular interface options, and a growing ecosystem of programmers, peripheral equipment, and operating systems. Later models differed from the original PDP-11/20; this was a *family*, not a single fixed machine. A unit installed for laboratory acquisition might have very different memory, interfaces, and operating software from one used in a manufacturing plant.

## 1.2 A canonical industrial control chain

**Physical process → transducer → signal conditioning → interface → processor → output interface → actuator → physical process.** Every arrow represents an engineering contract. A transducer converts temperature, pressure, force, or position to a measurable electrical quantity. The input interface gives the computer sampled data or event signals. Software evaluates the data using a policy. The output interface can command a valve or motor, subject to interlocks that should not rely solely on a software decision.

A separate observer may record time, raw samples, actuator state, fault flags, and energy consumption. This distinction between *control* and *observation* will matter when we put a Pico beside the MSP430. An instrument that reports 1,000 Hz has not demonstrated that the controlled process is safe; a controller that lights an LED has not established the fidelity of a sensor.

## 1.3 UNIBUS, interrupts, and direct memory access

PDP-11 systems used modular interconnects including UNIBUS and, in other family members, Q-bus. The original UNIBUS was more than a convenient connector. It organized requests for bus ownership, data movement, peripheral registers, and interrupts. A disk or instrumentation interface could gain bus access; an interrupt could signal that an external condition needed service; direct-memory transfers reduced repeated CPU involvement for eligible peripherals. DEC's *PDP-11 Bus Handbook* documents bus arbitration and prioritized service in technical detail.

One powerful architectural idea was **memory-mapped I/O**. A peripheral control register could be accessed with a load or store instruction rather than a completely separate I/O instruction set. A programmer who understood addressing and the meaning of each device register could operate a hardware interface. The processor's instructions became the vocabulary for changing external machinery. In today's MSP430, register names such as `P1DIR`, `TA0CCR0`, and `UCA0TXBUF` serve an analogous *programming role*, though there is no external UNIBUS and the actual peripherals are different.

Another idea was **priority**. Not every event could wait for a periodic software poll. A machine could interrupt ongoing work to service an event; a real-time operating system could schedule a task with greater urgency than routine reporting. This did not guarantee deadlines by itself. Priority rules, worst-case service time, shared data, and I/O latency still determined whether the control system met its obligations.

## 1.4 Industrial history without mythology

The PDP-11's industrial importance can be described precisely without calling it a universal solution. It appeared in laboratories, test stands, process monitoring, manufacturing, and machine control. DEC manuals for real-time systems explicitly discussed applications such as refinery and steel-processing control. But a successful installed system was never just a CPU and an operating-system disk. It included electrical isolation, transducers, operator interfaces, maintenance procedures, field wiring, software revisions, and emergency fallbacks.

This is the standard we should import into a teaching lab. We do not demonstrate industrial reliability by making a thermostat LED blink. We demonstrate a first principle: deterministic local decisions, explicit sensor validity, controlled output states, observed timing, and evidence of what happens on failure. Safety-critical industrial control requires far more engineering and certification than this book attempts.

## 1.5 Worked exercise: sketch the process

Draw the temperature-control chain on a sheet of paper. Label: (1) actual temperature, (2) DS18B20 physical transducer, (3) 1-Wire electrical bus, (4) MSP430 state machine, (5) logical cooling request, (6) optional low-voltage fan driver, (7) Pico measurement point, (8) PC observation and report. Ask what remains functional if the PC is unplugged. The desired answer: the MSP430's local state machine must continue, but the observer can lose logging. Then ask what occurs if sensor communication fails. The output must enter a defined, documented state, not silently continue trusting old data.

**CAP prompt.** Capture a labeled system drawing; analyze which connections carry data versus physical energy; publish the reason that an unresponsive operator dashboard must not become an undefined actuator command.

**Instructor note.** Describe the PDP-11's industrial accomplishment accurately while separating it from the much smaller educational demonstrator. Do not equate a DS18B20's internal digital conversion with the modular A/D equipment used in many PDP-11 installations.

# Chapter 2 — The PDP-11 programmer's view

## 2.1 Eight registers and a coherent model

The classic PDP-11 programmer sees eight 16-bit registers. R0–R5 are available for general computations; R6 is the stack pointer (SP); R7 is the program counter (PC). The processor status word records condition information such as negative, zero, overflow, and carry. The fact that the PC and SP appear as addressable registers is not an incidental flourish. Combined with the addressing modes, it gives compact ways to express constants, relative addresses, stacks, and subroutine behavior.

Think of a register as an immediately accessible storage location inside the processor, not a variable in RAM. A `MOV` moves a value; `ADD` combines a source and a destination; condition codes describe the outcome. An instruction can operate on an ordinary register or a memory value selected through an addressing mode. The memory arrangement and peripheral mapping may vary by PDP-11 model and memory-management configuration; these introductory exercises avoid assuming an entire system layout.

## 2.2 Addressing modes are the real lesson

PDP-11 addressing modes include register, register deferred, autoincrement, autoincrement deferred, autodecrement, autodecrement deferred, indexed, and indexed deferred. On many double-operand instructions, the source and destination can use the same broad palette. That symmetry is called *orthogonality*: many operations can apply to operands selected in the same ways. Orthogonality is not absolute, and device or instruction constraints remain, but the design is remarkably elegant.

A register operand such as `R2` means the value currently held in the register. `(R2)` denotes the contents of memory at the address in R2. `(R2)+` accesses memory and then advances R2, typically by the operand size (with special cases). `4(R2)` adds an offset to the register to locate an operand. With PC-relative forms, the same principles can address code or data near the instruction itself.

The PDP-11's user-visible design demonstrates how architecture can reduce a programmer's need to write separate sequences for every kind of memory access. But supporting many addressing modes affects instruction encoding, hardware, timing, and memory transactions. We will see an MSP430 with more registers but fewer flexible destination modes.

## 2.3 Worked program: sum five integers

The short MACRO-11-style illustration in `code/pdp11/01_register_loop.mac` computes 5 + 4 + 3 + 2 + 1 = 15 decimal. R0 counts down; R1 accumulates. The `SOB` instruction subtracts one from a register and branches back if nonzero. Because the PDP-11 traditionally displays addresses and values in octal, 15 decimal is 17 octal. The listing is a teaching example, not a verified simulator session.

Read the program twice. On the first pass, write every value R0 and R1 will hold. On the second pass, count how many times `ADD` executes and explain why the branch eventually stops. Then identify the machine state at `HALT`. Notice that no variable called `sum` is necessary for this exercise: the registers themselves are the state.

## 2.4 Condition codes and signed arithmetic

A processor can represent a 16-bit pattern as an unsigned quantity or a signed two's-complement quantity. The bit pattern alone does not tell the programmer which interpretation is intended. Zero indicates a zero result; negative generally tracks the most significant bit; overflow matters when signed arithmetic cannot be represented; carry matters for unsigned arithmetic or multiword operations. It is a mistake to treat these status flags as interchangeable.

**Exercise.** Add 1 to 0x7FFF in a 16-bit signed context. What bit pattern results? Why does the overflow flag matter even if the resulting bit pattern can be read as a positive unsigned integer? Then subtract one from zero and discuss borrow and negative flag behavior using the processor manual's exact definitions.

## 2.5 Simulation laboratory

An optional Open SIMH PDP-11 configuration permits exploration without a physical minicomputer. Install a reputable emulator, follow its documentation to select a specific simulated CPU and console, and obtain a suitable assembler/OS environment or use documented front-panel deposit/examine functionality. **Do not assume that a MACRO-11 source file can be pasted directly at a SIMH prompt:** the simulator's command language is distinct from an assembler, and assembling software may require an operating-system image or another tool.

The simplest learning artifact is a register trace. Write the instruction, the before-state, the expected after-state, and the actual after-state. Avoid spending a full introductory week installing a historical operating system. An instructor can preconfigure the machine, or substitute a pencil-and-paper execution trace when infrastructure is unavailable.

**CAP gate.** Publish a register-by-register execution table and state whether the values came from a simulator, a documented hand trace, or an actual machine.

# Chapter 3 — The PDP-11 operating systems and the discipline of time

## 3.1 A process does not wait for a terminal

A commercial accounting program can often wait for an operator to type a command. A machine monitoring molten steel or a pressure vessel has different obligations. A measurement may need to occur within a deadline; an alarm may need to preempt a report; a sensor may fail at the worst possible instant. The distinction is not merely whether a computer is *fast*, but whether its behavior is appropriately bounded and supervised.

The PDP-11 hosted several software environments. RT-11 served compact single-user, real-time and laboratory uses. RSX-11M and RSX-11S are particularly instructive for industrial history because they exposed ideas of tasks, scheduling, event-driven activity, and dedicated real-time environments. Other members of the family supported interactive computing, business applications, and UNIX development. We should not teach those environments as interchangeable or suggest every PDP-11 installation ran the same software.

## 3.2 Three kinds of time

Students often confuse clock frequency, execution time, and response latency. **Clock frequency** gives the rate of timing events driving some processor or peripheral. **Instruction execution time** depends on the actual instruction, selected operands, memory accesses, and implementation. **Response latency** is the time from an external event to a meaningful system reaction. A fourth term, **jitter**, describes variations in event timing or latency. Industrial systems need good answers for all four, not just an impressive processor clock specification.

Consider a system that samples pressure every 10 ms. A large average CPU capacity does not prove that every sample arrives on time. A priority inversion, slow interrupt routine, or unbounded busy wait may cause a deadline miss. A real-time operating system can help organize work but cannot remove physical constraints. A small bare-metal MSP430 can also meet selected deadlines if its program is simple, measured, and carefully controlled.

## 3.3 Interrupts as promises with costs

An interrupt lets the CPU abandon its current instruction stream at a defined point, save enough state, and execute service code. A reliable interrupt service routine (ISR) does not casually execute arbitrary work. It should usually do the minimum needed to capture a state or acknowledge a device, then defer expensive formatting, calculations, or communication until appropriate. The exact costs differ between PDP-11 models, MSP430 family members, clock settings, and software conventions.

In RSX-11M, task priorities and event mechanisms help coordinate activities. In an MSP430 lab, a hardware timer and ISR can provide a simpler demonstration of responsiveness. The lesson is not to recreate RSX-11M on a chip with 512 bytes of SRAM. It is to identify which responsibilities should happen promptly and which can wait.

## 3.4 Exercise: a scheduling timeline

Draw a 100-ms timeline with a periodic sampling event at 0, 10, 20, ... 90 ms; add a serial logging task that takes 15 ms of CPU time and a higher-priority alarm needing immediate attention. Use a colored pencil to show what happens if the program simply delays 15 ms at an inconvenient moment. Redraw with an interrupt that records the urgent event and with a foreground loop that handles logging. Then list assumptions: interrupt masking, time spent in ISR, interrupt priority, and whether logging can be interrupted.

This is a model, not a measured MSP430 timing result. The physical experiment in Chapter 7 will test a real program and show where our model is incomplete.

**CAP gate.** Publish a timeline annotated with deadlines, expected latency, and at least one plausible failure mode.

# Chapter 4 — PDP-11 and MSP430: kinship and tradeoffs

## 4.1 Architectural similarities that matter

The MSP430 has sixteen 16-bit register designators: R0/PC, R1/SP, R2/SR and special-purpose decoding, R3/constant generator, and R4–R15 as twelve general working registers. The PDP-11 has eight programmer-visible 16-bit registers, with PC and SP incorporated into the same general register numbering. Both machines permit many source/destination operations and address memory through register-based modes. The surface resemblance in assembly language is not an accident of spelling: the machines share powerful ideas about registers and operands.

However, one must be precise. The MSP430 is not binary-compatible with the PDP-11 and cannot execute PDP-11 machine code directly. Its source and destination addressing bits are asymmetric, its interrupt system and peripherals differ, and its registers have specialized encodings. TI documentation historically noted that the MSP430 can emulate much of the PDP-11 *instruction functionality*; that is not the same as running an unchanged PDP-11 executable.

## 4.2 A side-by-side example

PDP-11: `MOV #10,R4`, `ADD R4,R5`, `MOV (R5)+,R6`. MSP430: `MOV.W #10,R4`, `ADD.W R4,R5`, `MOV.W @R5+,R6`. The final line on both sides reads through a register-held pointer and advances that pointer. Syntax differs, and exact encoded instructions differ, but the conceptual mapping is unusually close.

Why does the MSP430 have twelve general working registers? Its 16-bit instruction encoding assigns four bits to a register number, allowing sixteen register choices. But those bits consume space. In the common two-operand format, the source has two mode bits while the destination has just one, so the destination cannot use every source addressing form. The PDP-11 uses three mode bits plus three register bits for either operand in many double-operand instructions. That symmetry yields richer addressing while leaving fewer register numbers.

## 4.3 The constant generator is a design lesson

MSP430 addressing encodings involving R2 and R3 can synthesize common constants such as 0, 1, 2, 4, 8, and -1 without fetching an additional immediate word in many circumstances. This reduces code space for frequent operations. Yet R2 and R3 are not interchangeable with general working registers; the same encoding fields acquire specialized meaning. Architectural elegance is always a balance between programmer convenience, instruction word capacity, hardware complexity, and code density.

**Prediction exercise.** Consider repeated operations adding 1 or subtracting 1. Why might an instruction set devote encoding shortcuts to such constants? What is the tradeoff in address-mode flexibility? Find two instructions in the MSP430 generated assembly whose constants are encoded without an immediate extension word; verify with a listing file, not by assumption.

## 4.4 RISC and CISC: useful words, unhelpful labels

The 2003 Jonathan Kirwan essay supplied in the course materials notes the PDP-11 resemblance and questions the MSP430's marketing classification as RISC. That is a worthwhile historical debate. Traditional load/store RISC designs separated memory access from arithmetic and often aimed for simpler instruction decoding and more regular pipeline behavior. MSP430 instructions frequently allow memory operands and variable instruction lengths; TI nevertheless describes its processor family as a 16-bit RISC architecture. The value of the comparison lies in examining what the hardware actually permits, not awarding a categorical label.

Compare an MSP430 instruction that moves a word from memory with one that moves between registers. Assemble both. Inspect number of words, encoding fields, and documented cycle counts. Then measure where possible—but never confuse a GPIO pulse around a sequence with timing of one isolated instruction unless all overhead has been measured or subtracted.

## 4.5 Worked paper exercise: same algorithm, different syntax

Write a summation loop for 5 through 1. On the PDP-11, the `SOB` instruction can both decrement a register and branch. On the MSP430, use `DEC.W` and `JNZ` as a corresponding two-instruction idiom. Explain why semantically equivalent code may require differing instruction counts and cycles. Keep one table for arithmetic state and a separate table for instruction addresses and encodings.

**CAP gate.** Publish an annotated comparison with the exact CPU variant, assembler syntax, source listing, and a note explaining what has *not* been tested. No statement of common binary lineage is supported by this example.

---

# Part II — The MSP430 becomes a physical experiment

# Chapter 5 — Build a one-kilohertz signal, then measure it

## 5.1 The question and the apparatus

The first physical question is deliberately narrow: Can an MSP430G2553 produce a nominal 1,000-Hz square wave, and can our external instrument observe it? The learner needs only a few ideas: clock, timer count, compare operation, output pin, and frequency meter. Everything else is initially support infrastructure. The existing Day One guide uses a custom MSP430G2553 board, the MSP-EXP430G2ET as a debugging/programming bridge, and a Pico W meter with a Web Bluetooth dashboard.

The board map in the existing documentation identifies P1.6/TA0.1 at custom header J2 pin 7, connected to Pico GP3; common ground is essential. The G2ET debugger-side interface connects to the custom board through power, ground, RST/SBWTDIO and TEST/SBWTCK after appropriate isolation of the LaunchPad target. The board must have one verified target 3.3-V source. The Pico may use separate USB power, but its 3.3-V rail should not simply be tied to another active 3.3-V regulator. No 5-V signal should be connected to the MSP430 or Pico input.

These are *project-specific proposed connections*, not instructions to bypass the physical check. Before programming, identify printed board labels, orientation, target power, possible alternate-function conflicts, and whether the board is populated and electrically tested. Do not assume a routed KiCad design proves a safe physical device.

## 5.2 Derive the expected frequency

Start with a nominal 1,000,000-Hz SMCLK. Timer_A in up mode counts from zero through `CCR0` inclusive, giving `CCR0+1` timer ticks. Select `TA0CCR0 = 499`; the timer period is 500 microseconds. If output mode 4 toggles channel TA0.1 once per timer period at a compare point `CCR1`, a *full* square-wave period requires two toggles. Thus the nominal output frequency is `f_out = f_SMCLK / [2 × (CCR0+1)] = 1,000,000 / (2 × 500) = 1,000 Hz`.

A common mistake is to conclude that 500 ticks at 1 MHz produces a full 2-kHz square-wave cycle. It produces one **edge** every 500 microseconds in this configuration, not a full high-low-high cycle. A second common mistake is to treat exactly 1 MHz as a measured DCO frequency. Factory constants nominally configure a clock, but actual oscillator behavior depends on calibration conditions, supply, temperature, and time.

## 5.3 The code is a causal chain

The supplied candidate C program `code/msp430/01_timer_1khz.c` stops the watchdog, checks factory calibration, configures the DCO, selects P1.6's Timer_A function, writes two compare registers, and starts the timer. Its `for (;;)` loop does not generate edges: the peripheral operates independently while the CPU does nothing useful. That separation is the moment when the student begins to see a computer as a collection of concurrent hardware actors rather than a single stream of software instructions.

To align with the user's earlier work, repeat the experiment using the already built assembly source in the existing Day One project. Keep assembly and C as separate builds, not firmware concatenated into one image. Preserve compiler commands, generated listings, maps, binary/TI-TXT files, and target part numbers for both.

## 5.4 Measure honestly

The original Pico W meter configuration for the exercise requires its generator OFF, input GP3, one sample per reading, and a documented gate, such as 1,000 ms. The user's guide notes that saved Pico settings can override power-on defaults; read the live status before trusting the display. A one-second count near 1,000 edges can be informative, but integer-edge counting and the meter timebase limit absolute accuracy.

Take five distinct readings, with true observation times and instrument settings. Record frequency, edge count, elapsed microseconds, and any failed reads. Calculate minimum, maximum, mean, observed range, difference from the 1,000-Hz nominal target, and any reported decimal precision. Do not infer traceable calibration from the number of digits on the screen. A five-reading cluster near 1,000 Hz establishes repeatability under those conditions more readily than absolute accuracy.

## 5.5 The controlled-change test

Before changing code, predict what will happen when `TA0CCR0` changes from 499 to 999 while the compare is still within the count range. The expected nominal result is 500 Hz. Build and program, measure again, and compare the direction and magnitude of change. If the measured frequency increases, suspect a wrong assumption, a wrong pin, an old image, or instrument configuration before claiming an unexpected physical law.

**CAP gate.** Submit a wiring sketch, board and firmware revisions, five real captures, a clear derivation, one deliberate modification, and a statement distinguishing nominal design from measured outcome.

**Instructor note.** This lab was source-built in the earlier project, but a complete hardware bench result was not established in the source guide available to this edition. Mark that status until fresh evidence is saved.

# Chapter 6 — Memory-mapped I/O: from an instruction to a wire

## 6.1 What a register write really means

In C, a statement such as `P1DIR |= BIT0` looks like an ordinary expression. The left side represents a hardware register at a defined address. `BIT0` is a mask selecting one bit. The operator `|=` means read the current value, set that bit, and write the result back without intentionally changing the other bits. A write to a GPIO direction register can change the electrical function of a pin: input versus output. A write to an output register can change the output latch level.

The corresponding MSP430 assembly typically uses bit-oriented operations such as `BIS.B` and `BIC.B` with a mask and a direct hardware-register address. The PDP-11 had its own memory-mapped peripheral registers; the vocabulary of addressable device state carries across even when instruction encodings and buses do not. The student's mental model should always include the target memory address and the physical device beyond it.

## 6.2 An active-low switch

The project guide maps a switch to P2.0, with a connection to ground when pressed. To read this reliably, make the pin an input, enable its internal resistor, and select pull-up. The idle input should read 1 and the pressed input 0, assuming wiring matches the proposed netlist. This inversion surprises beginners until they draw the circuit. `P2IN & BIT0` is a masked hardware read, not a declaration that a button is 'true' or 'false' by itself.

The source `code/msp430/02_gpio_switch.c` reads the switch and commands P1.0. Check LED polarity in the actual board; logic 1 may not mean 'visibly illuminated' in every circuit. A voltmeter at the pin can distinguish program logic from an LED installed backward or a missing current-limiting component. Build each example separately, and do not reuse P1.6 for an LED if the frequency-meter lesson currently occupies it.

## 6.3 Volatile and changing external state

A hardware input can change between two processor instructions without any assignment in C. That is why device-register definitions carry volatile semantics and why an optimizing compiler must not blindly reuse a previously loaded value as though it were an ordinary local variable. `volatile` does not solve atomicity, protect access from interrupts, create a memory barrier for all possible hardware, or make an operation fast. It tells the compiler a narrower but essential truth about observable accesses.

**Prediction exercise.** Write out the eight bits of P1DIR before and after `P1DIR |= BIT0`, then after `P1DIR &= ~BIT0`. If a second unrelated output occupies BIT4, why is a direct `P1DIR = BIT0` assignment dangerous? What could happen if two interrupt contexts both modify a shared software variable, even though that variable is `volatile`?

## 6.4 Control versus observation

Attach a physical switch, then probe the GPIO output or LED with the Pico or a meter. Record input state and output state as distinct data. If you can only see the LED, you know less than if you can also measure voltage at the pin. If the output is wrong, debug the chain in order: observed switch level, pin direction, pull-up, input mask, code branch, output latch, external circuit. Treat a failed test as evidence about one link in the chain.

**CAP gate.** Publish a truth table with real input/output states and a diagram that identifies electrical levels rather than only labels such as 'pressed' and 'on'.


# Chapter 7 — Real time is a promise, not a clock speed

## 7.1 When an external event interrupts a calculation

Imagine a filling station. A sensor reports that a container has reached its target level. The controller must close a valve before the contents overflow. The correctness of the action depends on two dimensions: the valve closes, and the command arrives in time. A beautifully structured program that misses the deadline is not a correct real-time program. This distinction was central to the operating environments developed for the PDP-11, particularly RSX-11M and RSX-11S, and it remains central to the MSP430.

A novice program might repeatedly inspect a switch: `while (1) if (switch_pressed()) close_valve();`. Polling can be appropriate when the interval between polls is bounded and the application tolerates it. But the loop can be delayed by display formatting, serial transmission, or unexpectedly slow arithmetic. Interrupts provide another mechanism: when an event occurs, dedicated hardware redirects execution to a service routine. Neither mechanism is magically deterministic. We must account for interrupt masking, instruction completion, nested interrupts, resource sharing, and the time consumed by the ISR.

A PDP-11 installation might combine interrupts, device controllers, and RSX task priorities. The MSP430 has no RSX executive in this example; instead, its vector table, peripheral interrupt flags, status register, and a small main loop accomplish the necessary coordination. We should teach the *responsibility* that survives across both systems rather than pretending their implementations are the same.

## 7.2 Three kinds of timing

**Elapsed time** is the physical interval measured between events. **CPU time** is the interval spent executing instructions. **Response latency** is the time between an external event and the intended reaction. The first two are not enough to establish the third. In addition, **jitter** is variation in observed timing from one instance to another. A control event can be timely on average and still occasionally miss a deadline.

For the 1-MHz clock used in the introductory lab, a cycle is nominally 1 microsecond. But it is incorrect to conclude that an arbitrary C statement takes 1 microsecond. Instructions differ in cycle counts, access modes, compiler output, and effects on interrupts. Instead, use a timer-based stimulus and a second GPIO pin as an observation point; measure the separation between events using a pulse-width-capable instrument. Keep the CPU clock assumption separate from the observation instrument's clock uncertainty.

## 7.3 Interrupt exercise: a periodically changing output

In `code/msp430/03_interrupt_led.c`, Timer1_A is configured with nominal SMCLK 1 MHz divided by four. With `TA1CCR0 = 24999`, the 25,000-count interval is nominally 100 milliseconds, and a Timer_A interrupt toggles P1.0. A full high-low-high LED output cycle therefore takes nominally 200 milliseconds. This experiment contrasts with Chapter 5, where Timer_A output hardware toggles a pin without CPU intervention.

```c
TA1CCR0  = 24999;                      /* 100 ms at 250 kHz */
TA1CCTL0 = CCIE;                       /* interrupt on CCR0 */
TA1CTL   = TASSEL_2 | ID_2 | MC_1 | TACLR;
__bis_SR_register(LPM0_bits | GIE);

#pragma vector=TIMER1_A0_VECTOR
__interrupt void timer1_a0_isr(void) {
    P1OUT ^= BIT0;                     /* visible toggling */
}
```

This excerpt needs the complete initialization and compiler support found in the companion candidate. A useful advanced variant is to toggle a **spare verified GPIO** on ISR entry and exit. The measured pulse width then estimates ISR execution time plus GPIO overhead; a second stimulus or marker is needed to measure interrupt latency. Explain the difference before presenting any timing plot. Do not claim a one-microsecond response simply because SMCLK is near 1 MHz.

## 7.4 Design exercise: a deadline budget

Suppose a hypothetical process requires response within 5 milliseconds. Allocate 1.0 ms for sampling, 0.5 ms for computation, 0.5 ms for output update, and 1.0 ms for worst-case waiting. The sum is 3.0 ms, leaving 2.0 ms of illustrative margin. Each number must eventually be replaced with measured or justified maxima. If the process has a relay that takes 20 ms to release, the software budget alone is irrelevant; actuator physics must be included.

**CAP gate.** Show a measured interval distribution with a defined start event and end event, and report the maximum seen—not just the mean. State what would be required to establish a true worst-case bound.

# Chapter 8 — A machine that can report what it does

## 8.1 From front panel to serial telemetry

A PDP-11 system could communicate through terminals, device interfaces, and connected peripherals. The ability to report state was essential in a plant: an operator needed to distinguish a command from an actual sensor reading and an alarm from a missing measurement. The MSP430G2553's USCI_A0 UART makes the same lesson accessible on a small board. It converts bytes into a start bit, data bits, and stop bit on a wire. The PC does not need to guess whether a line was printed: a terminal can show what arrived.

The user's custom-board guide identifies J3 as the 3.3-V TTL serial interface, with MSP430 P1.2 as TX and P1.1 as RX. Verify the board in hand. Connect target TX to adapter RX and common ground. Do not connect a legacy +/-12 V RS-232 port directly to the microcontroller. If the adapter has a 3.3-V power pin, leave that power pin disconnected unless a single-target-supply plan deliberately uses it.

## 8.2 An initial transmitter

The candidate `code/msp430/04_uart_hello.c` configures a nominal 1-MHz SMCLK, selects the USCI peripheral function on P1.1 and P1.2, and sets a nominal 9600-baud divider. It sends a known status sentence. The first lab should transmit a single `A`, inspect the terminal's 8N1 settings, and establish that every byte is correctly received before adding decimal formatting or periodic reports.

```c
static void putc_uart(char c) {
    while (!(IFG2 & UCA0TXIFG)) { }   /* await TX buffer ready */
    UCA0TXBUF = (unsigned char)c;
}
static void puts_uart(const char *p) {
    while (*p) putc_uart(*p++);
}
```

The loop waits for transmit-buffer availability; it does **not** guarantee that all bits of the preceding character have left the physical pin at that instant. For a known baud and frame size, estimate serialization time: an 8N1 frame contains ten bit times, so 9600 baud takes approximately 1.04 ms per character. A long print operation can dominate a tight loop. That is why industrial control should avoid placing blocking report functions inside time-critical interrupt routines.

## 8.3 Design a telemetry contract

Use short, explicit text records such as `T,123456,25.0625,77.1125,OK` for a timestamp in milliseconds, Celsius, Fahrenheit, and status. **That string is illustrative, not a measured value.** Prefer an unambiguous parser contract that also includes firmware version and sensor validity, for example `TEMP,v1,seq=12,raw=401,status=OK` where raw units are 1/16 degree Celsius. Host software can perform the engineering-unit conversion. This reduces formatting code in an MSP430 with limited RAM and flash.

Do not invent a timestamp source. If the MCU provides only a sample counter, label it `sample_id`, not Unix time. If a host later supplies reception timestamps, distinguish them from sample-acquisition timestamps; serial latency and clock offsets make these different observations.

**CAP gate.** Capture a real terminal transcript, a pin map, UART settings, clock source, and one known sequence of bytes. Deliberately change the host baud rate and explain the corruption as a mismatched communication contract rather than an inaccurate temperature sensor.

# Chapter 9 — One wire, two participants, and a microsecond-scale contract

## 9.1 The discipline of releasing a line

The Dallas/Maxim/Analog Devices 1-Wire protocol combines a physical electrical rule with a timed conversation. The master and device may pull the data line low. Under normal externally powered operation, neither should force the shared line high against the other; instead, the pull-up restores the high level after release. The distinction matters because the microcontroller output latch and output-direction register can cause an electrical conflict if the pin is inadvertently configured as a driven high output.

For this curriculum, use a genuine, externally powered DS18B20, with its VDD and ground correctly connected and a verified data pull-up to 3.3 V. The existing board's P1.7 net is a plausible location because the prior netlist assigns it an approximately 4.7-kΩ pull-up, but this must be confirmed on the actual board and checked for I²C conflicts. The sensor package pinout must come from its manufacturer datasheet, not from a generic drawing.

## 9.2 The primitive operations

A master needs only a few physical primitives: reset, sense presence, write one bit, and read one bit. Byte operations then build on bit operations, least-significant-bit first. The conceptual state transitions are:

```
IDLE high -> MASTER LOW -> MASTER RELEASE -> DEVICE RESPONSE -> IDLE high
```

The reset interval and the read/write slots each have bounds specified in the datasheet. The critical time is the voltage transition observed *at the pin*. A C delay loop that says `wait_us(6)` is merely a hypothesis about the signal. Compiler optimization, overhead, interrupts, clock frequency, and pin capacitance can change what actually occurs. The physical test should show reset low time, release interval, presence response, a write-1 slot, a write-0 slot, and the read sampling point.

The optional candidate `code/msp430/09_onewire_transport_CANDIDATE.c` shows a Timer_A-based strategy, but it is intentionally **not presented as validated target firmware** in this edition. Its Timer_A ownership conflicts with the 1-kHz experiment, and its microsecond busy-wait and interrupt effects need independent bench evidence. The companion `code/msp430/07_onewire_transport_design.txt` is the deliberate interface contract for implementing and verifying transport in a separate target project.

## 9.3 Layer the driver; do not write everything at once

First construct and verify `ow_drive_low()` and `ow_release()` with a voltmeter or scope. Second verify reset/presence without sending any sensor command. Third verify one write-0, one write-1, and one read slot, including interrupt timing assumptions. Fourth implement LSB-first byte transmission and reception. Fifth read the sensor's 64-bit ROM identity or use Skip ROM only when exactly one device is attached. Finally command a conversion and read a nine-byte scratchpad.

For the DS18B20 at the factory-default 12-bit resolution, a conversion may require up to 750 ms; do not assume it is complete because 100 ms elapsed. Externally powered mode avoids the extra strong-pull-up complexity associated with parasite power. Use a valid completion condition or a sufficient documented wait. Preserve raw bytes, the CRC result, and the status of every failed transaction.

## 9.4 A measurement contract for the Pico

A frequency meter that counts rising edges over one second is excellent for a thousand-hertz signal but insufficient as evidence for a six-microsecond 1-Wire pulse. For the 1-Wire laboratory, configure a separate validated pulse-width capture or logic-analyzer program. The measurement instrument's edge timing resolution, input threshold, buffer capacity, reference timebase, and acquisition trigger should appear in the report. A GPS-disciplined timebase can be a later experiment, not a condition for beginning.

**CAP gate.** Show at least one annotated physical reset/presence waveform and one of each bit-slot type. Include the independent pin-level measurement, timer configuration, interrupt policy, pull-up value, and device power mode.

# Chapter 10 — Bytes become temperature: integrity, units, and meaning

## 10.1 A conversion is more than two bytes

The DS18B20 stores its current result in a scratchpad. After a completed conversion, the two least-significant scratchpad bytes contain a signed fixed-point value. At 12-bit resolution the raw unit is 1/16 °C; the remaining scratchpad bytes include alarm/configuration values, reserved fields, and an 8-bit CRC. The CRC covers the first eight scratchpad bytes and is supplied in byte nine. A successful CRC check detects many data-transfer faults, but does not certify the sensor's thermometric accuracy or its thermal coupling to the environment.

The physical reading sequence for **one confirmed DS18B20** is: reset/presence; Skip ROM `0xCC`; Convert T `0x44`; wait for conversion; reset/presence; Skip ROM `0xCC`; Read Scratchpad `0xBE`; read nine bytes; verify CRC; decode temperature. If multiple 1-Wire devices are attached, Skip ROM is not the correct general addressing strategy for a read. Use ROM identification and device selection.

## 10.2 Decode signed fixed point without hiding arithmetic

Suppose bytes 0 and 1 are `0x91` and `0x01`. The raw little-endian word is `0x0191`, or 401 decimal. It represents 401/16 = 25.0625 °C, equivalent to 77.1125 °F. These are **constructed teaching bytes**; the book does not claim they came from a sensor. For a negative example, `0xFF5E` interpreted as a signed two's-complement word is -162, giving -10.125 °C. The source file `code/msp430/06_ds18b20_decode.c` implements CRC and signed decoding separately from physical bus transport.

```c
/* Only after a successful nine-byte scratchpad read: */
int16_t raw_x16;
int status = ds18b20_decode_x16(scratchpad, &raw_x16);
if (status == 0) {
    /* Keep the integer raw value in the target telemetry. */
    /* Celsius = raw_x16 / 16.0, preferably on host. */
} else {
    /* Report invalid reading; do not publish stale data as current. */
}
```

On the host, floating-point conversion can be used for display and plots. On the MSP430, a signed 16-bit or 32-bit fixed-point representation is often simpler. Beware of ordinary C integer division: `401 / 16` gives 25, losing the fractional component. Also avoid treating resolution as accuracy. The nominal 0.0625 °C step of 12-bit representation does not imply that the real temperature is known to that accuracy. Analog Devices specifies a typical marketed accuracy bound of ±0.5 °C across a defined central range; consult the complete electrical and operating conditions of the datasheet for actual application limits.

## 10.3 CRC as a protocol laboratory

The code `code/python/ds18b20_math.py` provides a host algorithm for the reflected Dallas CRC-8 polynomial, and the companion MSP430 C source uses the same bitwise logic. Start by giving learners an eight-byte synthetic message and a computed check byte. Flip one bit and observe that the CRC no longer matches. Then discuss the distinction between **correctly received bytes**, **physically correct measurement**, and **safely handled failure**.

The DS18B20 can report the power-on 85 °C register value before a completed conversion. The controller should not accept a number merely because it looks like a valid temperature. Its validity contract should require a completed conversion, successful transport, CRC integrity, and a sensible acquisition status. A CRC-valid frame can still be old or associated with the wrong sensor.

**CAP gate.** Supply all nine raw bytes from a real conversion, power mode, firmware version, timestamp or sample index, CRC result, signed integer decode, Celsius and Fahrenheit, and an independent approximate temperature check. Report unsuccessful transactions rather than silently discarding them.

# Chapter 11 — Industrial control, hysteresis, and failure behavior

## 11.1 A controller needs memory

A naive thermostat uses one threshold: if temperature is above 29 °C, activate cooling, otherwise turn cooling off. A noisy sensor close to 29 °C can cause repeated rapid on/off decisions, a problem called chatter. Hysteresis gives the controller a memory of its previous state. In our educational example cooling becomes requested when temperature rises to 30 °C and remains requested until it falls to 28 °C. Between those values, the previous state is retained.

```
               temperature rising
         28 C             30 C
OFF -------------------------------> ON
     remain in previous state
ON  <------------------------------- OFF
               temperature falling
```

The drawing describes transition thresholds, not an assertion that a real fan, heater, or thermal plant will achieve them. Without a physical actuator connected, this is an *alarm/control decision demonstrator*. To call it closed-loop control, the commanded output must measurably affect the controlled process, and the sensor must observe that effect. A simulated output LED is a useful intermediate step; it is not a substitute for actuation.

## 11.2 Separate the control law from the pin driver

The included `code/msp430/05_thermostat_logic.h` is deliberately device-independent, so it can be studied and tested without energizing equipment. It takes three inputs: the prior state, signed temperature in 1/16 °C, and a validity flag. Its outputs are OFF, ON, or FAULT.

```c
control_state_t next = control_step(previous_state, temp_x16, sensor_valid);
/* A separate, reviewed driver maps next state to a real output. */
```

When the sensor is invalid, the example returns `CONTROL_FAULT`; the actuator policy must define what that means. For a classroom LED, fail-to-off is a reasonable demonstration. For a real freezer, incubator, furnace, or fluid process, arbitrarily switching off could be dangerous. Safety policy belongs to the physical application and may require independent hardwired protections.

The pure decision function is testable with data such as 27 °C, 29 °C, 31 °C, and an invalid sensor. Students can predict the state sequence before running the test. A good test covers the threshold itself, the band between thresholds, a recovery from FAULT, and the case where a sensor returns an old but plausible value. Recovery policy should not be accidental; our sample chooses OFF if a valid temperature returns inside the band after a fault.

## 11.3 Scheduling a process supervisor

One feasible architecture uses a periodic timer flag to schedule sensor work, a bounded state machine to initiate and complete conversions, and a low-priority output path to transmit telemetry. A 750-ms conversion at 12-bit resolution should not be implemented as a single interrupt handler that busy-waits for 750 ms. The controller can issue conversion, return to other work, and collect data after completion. However, the 1-Wire timing-critical slots do require carefully bounded microsecond-scale operations.

```
SAMPLE_IDLE -> START_CONVERSION -> WAIT_CONVERSION
            -> READ_SCRATCHPAD -> VALIDATE_CRC
            -> UPDATE_CONTROLLER -> REPORT -> SAMPLE_IDLE
                 | any error -> FAULT -> REPORT
```

This is the same architectural separation that real-time industrial systems demand: acquisition, decision, actuation, and reporting have different timing and failure requirements. On a PDP-11 with RSX-11M, the responsibilities might be distributed among driver interrupt service, prioritized tasks, and data-logging processes. On the MSP430 they can be functions in a compact event-driven loop. Compare the responsibilities, not the software scale.

## 11.4 A verification matrix, not a show-and-tell

Test at least four independent properties. **Sensor integrity:** disconnect DQ or corrupt a CRC and verify FAULT. **Control correctness:** sweep temperatures upward and downward across both thresholds, verifying transitions. **Timing:** measure acquisition interval and any output transition delay. **Independence:** disconnect the PC display during an active experiment; the local MCU logic should continue its documented behavior. If it does not, the architecture has unintentionally moved control into the observation path.

**CAP gate.** Record a state-transition table including invalid data and recovery, wiring, raw values, state outputs, and one failure-injection test. Conclude only what the test establishes.

# Chapter 12 — Publish an experiment that another engineer can reproduce

## 12.1 Evidence is a design product

Industrial computing did not become credible solely because computers were faster than relays. It became credible through documented interfaces, repeatable procedures, diagnosis, and control of configuration. The same habits can be taught using a modern editor, a small microcontroller, and an inexpensive measuring instrument. A scientific report should state the intended behavior, the actual build, the observed evidence, the instrument's limits, and what would falsify the conclusion.

At minimum, preserve: board model and revision, electrical supply, sensor identity and power mode, wiring drawing, compiler/toolchain version, source hash or version tag, programmed image, measurement firmware/configuration, raw measurements, host-analysis script version, and a photograph or schematic of the actual experimental arrangement. A teacher should never substitute a synthetic expected measurement for a missing physical observation; mark the experiment incomplete.

## 12.2 Python as the laboratory notebook engine

The companion `code/python/cap_analyze.py` reads an honest frequency CSV, calculates basic descriptive statistics and difference from nominal, and publishes a small Markdown report. The `worksheets/frequency_capture_template.csv` provides blank fields rather than plausible pre-filled numbers. Every field should be treated as a measurement contract: units and instrument state must be present, and missing observations must remain missing.

A reporting script cannot independently calibrate the Pico or the MSP430. It can calculate `mean`, `min`, `max`, `range`, and standard deviation, but the meaning of these statistics depends on the sampling protocol. Five measurements that share the same incorrect reference clock can be closely clustered and all wrong. Report repeatability and evidence of calibration separately.

## 12.3 An uncertainty budget in plain language

For the 1-kHz test, plausible error contributors include the MSP430 DCO frequency, Pico reference crystal, gate timing, and integer count quantization. A rectangular one-second gate with count N has an idealized one-count granularity of about one hertz; the actual system may include other timing errors. If the measurement system later uses an external GPS 1 PPS signal to characterize its oscillator, confirm GNSS lock, missed pulses, event selection, and the counter implementation. An average of several intervals reduces some random variation but cannot by itself eliminate constant bias or misidentified timing edges.

The objective of a classroom uncertainty budget is not to manufacture a precision claim. It is to teach the student to ask: what was compared to what, for how long, under which conditions, and how could the conclusion be wrong?

## 12.4 A defensible final demonstration

Ask students to present a ten-minute evidence-based demonstration. Their controller should read temperature or report an explicit fault, calculate a control state, emit truthful telemetry, and preserve all raw sensor bytes. The Pico should provide at least one independent timing observation, not necessarily continuously. The final report should compare measured behavior to the stated requirements and distinguish any unfinished hardware validation.

A passing project need not have a beautiful dashboard or advanced network infrastructure. The most important product is *explainable behavior* that remains useful without the PC. The PDP-11's industrial heritage is honored when students understand their sensor, timing, decisions, and failures—not when they merely reproduce a vintage machine in miniature.

# Part III — Teacher's and operator's companion

# Chapter 13 — Twelve-session teaching plan

Each session assumes 75–90 minutes after hardware setup. The pedagogical pattern is Predict (10 minutes), Explain (15), Build/observe (35), Analyze (15), Publish (10). Extend the hands-on period when students encounter genuine debugging. The outcome is a structured record, not a claim of completion regardless of evidence.

| Session | Historical/architectural idea | Physical or simulated investigation | Minimum evidence |
|---|---|---|---|
| 1 | PDP-11 as industrial controller | Draw an acquisition/control system | Labeled interfaces and failure modes |
| 2 | PDP-11 registers and modes | Trace MACRO-11-style register loop | Register-state table |
| 3 | Architecture tradeoffs | Compare PDP-11/MSP430 syntax and encodings | Annotated instruction comparison |
| 4 | Timer vs CPU | MSP430 1-kHz square wave | Five measured gates and wiring |
| 5 | Compiler behavior | C/assembly Timer_A comparison | Listing plus paired measurements |
| 6 | Memory-mapped I/O | Read switch, drive LED | Measured logic truth table |
| 7 | Interrupts and deadlines | Timer-driven interrupt output | Timing and variation plot |
| 8 | UART and observability | Send known character and telemetry | Captured terminal bytes |
| 9 | Timed serial protocol | Verify 1-Wire slots and presence | Pin-level waveforms |
| 10 | Integrity and temperature | Read nine scratchpad bytes and check CRC | Raw bytes, CRC, C/F conversion |
| 11 | Industrial decision logic | Hysteresis and injected faults | Transition/failure matrix |
| 12 | Reproducible engineering | Capstone CAP report | Versioned evidence bundle |

## 13.1 Three teaching levels

A newcomer should explain cause and effect with a wiring drawing and a small source slice. An intermediate student should predict numeric behavior, read a disassembly, and collect genuine measurements. An advanced student should examine ISR latency, oscillator uncertainty, code-size/encoding tradeoffs, and driver timing. All three levels should meet the same standard of honesty about the observed evidence.

## 13.2 Grading rubric

Allocate equal weight to (1) safe and traceable setup, (2) model and prediction, (3) real observation and analysis, and (4) reproducible publication. Award credit for a well-documented failure with a sound diagnosis. Do not award a fabricated five-reading data table. A student should be able to state which subsystem generated each claimed signal and which instrument observed it.

## 13.3 The instructor's stop list

Stop and investigate before applying power if the board is unpopulated, unknown, reversed, connected to competing supplies, or exposed to 5-V GPIO. Preserve MCU information flash calibration and do not use erase-all as a workaround. Do not combine stand-alone Timer_A examples into one program without resolving peripheral ownership and ISR-vector conflicts. Do not trust sensor data until transport and CRC are verified. Keep high-voltage and hazardous actuators entirely outside the introductory build.

# Chapter 14 — The historical bridge: what survives fifty years?

The PDP-11, launched in 1970, established a notably coherent programming model for small computers. Through an ecosystem of hardware modules, data acquisition equipment, MACRO-11, and real-time systems such as RSX-11M, it participated in the physical automation of industrial work. In DEC's own 1977 *Introduction to RSX-11M*, oil refineries and steel rolling mills appear as examples of monitored and controlled processes. The historical claim is not that every industrial controller was a PDP-11, but that the PDP-11 was an important, documented platform for programmable real-time control.

The MSP430G2553 is a very different machine but retains features worth comparing: a 16-bit programmer's view, addressable PC and SP, two-operand operations, memory-mapped peripherals, interrupts, and modest enough resources that machine behavior remains visible. The extra registers and compact constant generator come with addressing-mode restrictions. Jonathan Kirwan's July 18, 2003 essay, *A Perspective on the MSP-430 Instructions and Addressing Modes*, is a useful contemporary discussion of that precise tradeoff. It also reminds us that TI's `RISC` marketing label should not replace a careful understanding of instruction encoding and actual execution cost.

The Pico instrument adds a third and equally important idea. Rather than judging the MSP430 by whether a program compiles, the class measures pulses, examines timing, records error, and publishes evidence. The development hardware may be sophisticated while the deployed controller is inexpensive. That separation of development capability from deployment cost is as educationally important as the individual instruction sets.

The historical bridge can be summarized as **architecture → real-time operation → physical process → independent measurement → explainable evidence**. This is the course's durable idea. It can be extended to an STM32, an ESP32, a modern industrial PLC, or a simulated historical minicomputer without losing the fundamental engineering questions.

# Appendices

## Appendix A — Compact PDP-11 and MSP430 register comparison

| Concept | PDP-11 | MSP430G2553 |
|---|---|---|
| Data path | 16-bit | 16-bit |
| Visible CPU registers | R0–R7 | R0–R15 |
| General working registers | R0–R5 | R4–R15 |
| PC | R7 | R0 |
| SP | R6 | R1 |
| Status/flags | Processor Status Word | R2 Status Register |
| Constant generator | No dedicated counterpart | Encodings involving R2/R3 |
| Two-operand operations | Yes | Yes |
| General autoincrement destination | Yes | No |
| Memory-mapped I/O | Yes | Yes |
| Target context | Minicomputer and peripheral system | On-chip microcontroller peripherals |

Instruction formats and semantics are not interchangeable. The PDP-11 has broader symmetrical operand modes, while the MSP430 uses different fields for its source and destination. The MSP430's emulated instructions and constant generation should be learned from TI's CPU chapter, not inferred from one assembler's mnemonics.

## Appendix B — Safe bench reference

Treat these as proposed custom-board connections, to be confirmed against the actual PCB and schematic: P1.6/TA0.1 to Pico GP3 for frequency measurement; P1.7 to DS18B20 DQ with one verified ~4.7-kΩ 3.3-V pull-up; P1.2 UART TX and P1.1 RX; P2.0 switch input; P1.0 LED output. Use debugger-side Spy-Bi-Wire from the G2ET eZ-FET, matching labeled 3.3 V, GND, RST, and TEST. Use regulated single-source target power and a common reference ground. Keep GPIO below the relevant device absolute maximum and never use 5-V logic directly.

The board documents and earlier Teacher/Operator Guide remain the controlling source for physical wiring. This book does not certify the PCB as manufactured or populated.

## Appendix C — Operator worksheet: capture, analyze, publish

**Prediction:** What exact observable event should occur and what numeric value is expected? **Configuration:** target power, pin map, program hash, clock source, meter firmware, gate duration, acquisition settings. **Capture:** preserve raw data without rewriting, including failures. **Analyze:** show equations, observed variation, one limitation, and an alternative explanation. **Publish:** concise claim, strongest evidence, configuration needed for repetition, and next controlled test.

A reproducible lab should always contain a **status label**: historical demonstration, host-tested algorithm, candidate target code, bench-observed physical behavior, or verified calibration. This prevents a source example from evolving into an unsupported claim as the curriculum is redistributed.

## Appendix D — References and provenance

1. Digital Equipment Corporation, *Introduction to RSX-11M*, Version 3.1, December 1977, especially Chapter 2, process-control and data-acquisition applications. https://bitsavers.trailing-edge.com/pdf/dec/pdp11/rsx11m_s/RSX11M_V3.1_Dec77/1A_System_Reference_Information/AA-2555C-TC_Introduction_to_RSX-11M_3.1_Dec77.pdf
2. DEC, *PDP-11 Processor Handbook* and *PDP-11 Peripherals Handbook*, multiple editions, archived at Bitsavers. https://bitsavers.org/pdf/dec/pdp11/
3. Texas Instruments, *MSP430F2xx, MSP430G2xx Family User's Guide*, SLAU144K. https://www.ti.com/lit/ug/slau144/slau144.pdf
4. Texas Instruments, *MSP430G2553 Datasheet*. https://www.ti.com/lit/ds/symlink/msp430g2553.pdf
5. Texas Instruments, *MSP-EXP430G2ET LaunchPad Development Kit User's Guide*. https://www.ti.com/lit/ug/slau772/slau772.pdf
6. Analog Devices (Maxim Integrated), *DS18B20: Programmable Resolution 1-Wire Digital Thermometer*, Rev. 6. https://www.analog.com/media/en/technical-documentation/data-sheets/ds18b20.pdf
7. Jonathan Kirwan, *A Perspective on the MSP-430 Instructions and Addressing Modes*, embedded-systems discussion, July 18, 2003. Historic author analysis supplied by reader; treat opinions as attributed rather than definitive processor taxonomy.
8. *MSP430 Day One Teacher & Operator Guide* and *MSP430 Teacher & Operator Guide v2.0*, October 29, 2026, user-provided project references, with code audit and bench-validation caveats.

**Historical accuracy note.** The instruction-set similarities do not establish that the MSP430 was directly derived from the PDP-11. The industrial descriptions in this book describe documented capabilities and representative system engineering, not reconstruction of a specific customer's proprietary plant program.

## Appendix E — Reference implementation inventory

- `code/pdp11/01_register_loop.mac`: conceptual MACRO-11-style loop; assemble in a confirmed PDP-11 toolchain before describing as executed.
- `code/msp430/01_timer_1khz.c`: nominal Timer_A 1-kHz output; target compilation/physical validation needed.
- `code/msp430/02_gpio_switch.c`: active-low button and LED; board polarity validation needed.
- `code/msp430/03_interrupt_led.c`: Timer1_A interrupt demonstration; target compilation/measurement needed.
- `code/msp430/04_uart_hello.c`: UART test at nominal 1 MHz and ~9600 baud; verify actual clock/baud.
- `code/msp430/05_thermostat_logic.h`: pure digital supervisor function; no mains/load connection.
- `code/msp430/06_ds18b20_decode.c` and `.h`: CRC and signed scratchpad decoder, separate from bus acquisition.
- `code/msp430/07_onewire_transport_design.txt`: proposed physical-layer contracts and evidence requirements; **not runnable driver firmware**.
- `code/msp430/09_onewire_transport_CANDIDATE.c`: experimental timing primitives for review and scope-based validation; **not bench-proven**, and must not be merged into the Timer_A frequency example without redesign.
- `code/python/ds18b20_math.py`, `code/python/cap_analyze.py`: host data examples with unit tests; not instruments or clocks.
- `worksheets/`: blank temperature and frequency capture forms.
- `tests/test_host.py`: tests host-based arithmetic and parsing only; not target CPU, real I/O, real timing, or calibration.
