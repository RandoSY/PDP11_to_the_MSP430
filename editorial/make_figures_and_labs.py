from pathlib import Path
import os, re, shutil, textwrap, math, zipfile, json
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUT=Path(__file__).resolve().parents[1]
OUT.mkdir(exist_ok=True)
(OUT/'figures').mkdir(exist_ok=True)

REG='#0c2437'; NAVY=(11,35,53); MID=(31,75,97); TEAL=(22,135,118); CREAM=(246,244,236); GOLD=(222,172,94)
FONT='/usr/share/fonts/truetype/lato/Lato-Regular.ttf'
FONTB='/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'
FONTL='/usr/share/fonts/truetype/lato/Lato-Light.ttf'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
def font(n,b=False,l=False):
    candidates=[FONTB if b else FONTL if l else FONT,'DejaVuSans.ttf','LiberationSans-Regular.ttf']
    for candidate in candidates:
        try:return ImageFont.truetype(candidate,n)
        except OSError:pass
    return ImageFont.load_default()
def draw_cover():
    w,h=1800,2600; im=Image.new('RGB',(w,h),NAVY); d=ImageDraw.Draw(im)
    d.rectangle((0,0,40,h), fill=TEAL); d.rectangle((40,0,w,28),fill=GOLD)
    for x in range(110,w,150): d.line((x,1100,x,h-380),fill=(25,54,73),width=3)
    for y in range(1160,h-360,150): d.line((90,y,w-90,y),fill=(25,54,73),width=3)
    d.text((145,145),'FROM THE',font=font(68,b=True), fill=(138,207,200))
    d.text((132,275),'PDP-11',font=font(175,b=True), fill=CREAM)
    d.text((142,500),'TO THE',font=font(66,b=True),fill=(138,207,200))
    d.text((132,627),'MSP430',font=font(175,b=True),fill=CREAM)
    d.rounded_rectangle((135,875,w-135,990), radius=14,fill=(27,68,83))
    d.text((170,899),'THE INDUSTRIAL COMPUTER, REIMAGINED',font=font(37,b=True),fill=CREAM)
    # three eras flow diagram
    centers=[380,900,1415]; ys=1475
    for j,(c,name,desc) in enumerate(zip(centers,['PDP-11','MSP430','RP2040'],['ARCHITECTURE','CONTROL','MEASUREMENT'])):
        d.rounded_rectangle((c-210,ys-170,c+210,ys+170),radius=25,outline=TEAL if j==2 else GOLD,width=7,fill=(19,50,66))
        d.text((c,ys-106),name,anchor='mm',font=font(65,b=True),fill=CREAM)
        d.text((c,ys+30),desc,anchor='mm',font=font(28,b=True),fill=(151,212,201))
        # stylized pulses
        pts=[(c-130,ys+105),(c-80,ys+105),(c-80,ys+75),(c-25,ys+75),(c-25,ys+105),(c+32,ys+105),(c+32,ys+75),(c+105,ys+75)]
        d.line(pts,fill=GOLD,width=6)
    for c in [640,1158]:
        d.line((c,ys,c+45,ys), fill=CREAM,width=5)
        d.polygon([(c+45,ys),(c+25,ys-18),(c+25,ys+18)],fill=CREAM)
    d.text((145,1950),'Hardware  /  Assembly  /  C  /  Python',font=font(50), fill=CREAM)
    d.text((145,2030),'Timing  /  Sensors  /  Industrial Control',font=font(48),fill=CREAM)
    d.line((145,2190,1660,2190),fill=GOLD,width=4)
    d.text((145,2280),'FINAL EDITORIAL TEXTBOOK EDITION',font=font(39,b=True),fill=(153,218,204))
    d.text((145,2355),'2026  •  COURSEBOOK + LABORATORY COMPANION',font=font(34),fill=CREAM)
    im.save(OUT/'figures'/'cover.png',quality=96)

def diagram(name,title,lanes,caption):
    W=1480; h=520; im=Image.new('RGB',(W,h),'#fbfaf6'); d=ImageDraw.Draw(im)
    d.text((70,30),title,font=font(45,True),fill=NAVY)
    items=len(lanes); g=25; margin=70; iw=(W-2*margin-(items-1)*g)//items
    for i,(h1,h2) in enumerate(lanes):
        x=margin+i*(iw+g); y=140
        d.rounded_rectangle((x,y,x+iw,y+205),radius=20,fill=(235,246,243),outline=TEAL,width=4)
        d.text((x+25,y+44),h1,font=font(33,True),fill=NAVY)
        # Wrap description
        for j,line in enumerate(textwrap.wrap(h2,24)):
            d.text((x+26,y+112+j*32),line,font=font(26),fill=MID)
        if i<items-1:
            ax=x+iw+6; ay=y+100; d.line((ax,ay,ax+18,ay),fill=GOLD,width=5)
    d.line((70,403,W-70,403),fill=(220,225,218),width=2)
    for j,line in enumerate(textwrap.wrap(caption,90)):
        d.text((70,425+j*30),line,font=font(24),fill=MID)
    im.save(OUT/'figures'/name)

def timing_diagram():
    w,h=1480,560; im=Image.new('RGB',(w,h),'#fcfbf7'); d=ImageDraw.Draw(im)
    d.text((65,30),'Timer_A: one output period requires two edges',font=font(43,True),fill=NAVY)
    d.text((70,110),'TIMER COUNT',font=font(25,b=True),fill=MID)
    x0=210; scale=270
    for k in range(4):
        x=x0+k*scale
        d.line((x,165,x,385),fill=(217,227,224),width=3)
        d.text((x+4,135),str(k*500)+' µs',font=font(24),fill=MID)
        d.line((x,220,x+scale-25,220),fill=TEAL,width=7)
        d.line((x+scale-25,220,x+scale-25,175),fill=TEAL,width=7)
        d.line((x+scale-25,175,x+scale,175),fill=TEAL,width=7)
    d.text((70,295),'P1.6 OUTPUT',font=font(25,b=True),fill=MID)
    pts=[(x0,350),(x0+scale,350),(x0+scale,290),(x0+2*scale,290),(x0+2*scale,350),(x0+3*scale,350),(x0+3*scale,290),(x0+4*scale,290)]
    d.line(pts,fill=GOLD,width=8)
    d.text((70,452),'500 timer ticks between toggles × 2 toggles = 1,000 µs per output period (nominal).',font=font(27),fill=NAVY)
    im.save(OUT/'figures'/'timer_timing.png')

draw_cover()
diagram('industrial_loop.png','From industrial process to digital decision', [('Process','temperature or pressure'),('Interface','signal conditioning'),('Computer','registers and logic'),('Output','alarm or actuator')], 'A practical controller requires electrical protection, a defined deadline, and a safe response to faults.')
diagram('roles.png','Three distinct jobs on one laboratory bench',[('PDP-11','historical architecture'),('MSP430','real-time controller'),('Pico','external instrument'),('PC','analysis and report')], 'The measurement instrument does not substitute for the controller, and neither proves industrial safety.')
diagram('data.png','Evidence moves through a chain',[('Raw edges','Pico timing capture'),('Records','CSV with settings'),('Analysis','Python statistics'),('Claim','bounded conclusion')], 'Never allow a formatted display or calculated summary to replace raw observations.')
diagram('supervisor.png','A minimal industrial temperature supervisor',[('DS18B20','data with CRC'),('MSP430','hysteresis and fault'),('LED','safe test output'),('Host','UART monitoring')], 'The software state machine is testable separately from the physical sensor and actuator.')
timing_diagram()

LABS=[
{
'id':'01','title':'A Computer at the Steel Mill','theme':'Industrial-control anatomy and the PDP-11',
'context':'''A rolling mill is a useful thought experiment because it combines measurements, delayed material transport, and outputs that have physical consequences. An imaginary sensor produces a pulse each time a piece reaches an inspection station. A second sensor reports a temperature. The computer must distinguish a product defect from an instrumentation defect. Historical PDP-11 installations existed in industries of this kind; the scenario in this lab is intentionally fictional, not a reconstruction of any installation. Beginning with a plausible process avoids the false implication that a minicomputer alone provides safe control. Experienced engineers will ask first about mechanical guards, interlocks, independent emergency stops, and who is allowed to energize an actuator.''',
'model':'''Draw two paths: the CONTROL path from sensor to decision to actuator, and the EVIDENCE path from raw signal to timestamp to stored record. Place signal conditioning and galvanic isolation where needed. Then write a data dictionary with units, range, update rate, and the result expected if a sensor wire breaks. A temperature sample is not a decision; a limit is a policy; an output is an electrical command rather than a guarantee of mechanical motion.''',
'prediction':'Predict which of these events requires the shorter response: a one-second temperature trend update, a mechanical limit switch, and a report requested from an operator console. Give an explicit deadline for the hypothetical system and distinguish your engineering choice from a historical DEC specification.',
'procedure':('Draw a process diagram showing physical plant, transducers, interfaces, CPU, outputs, and an independent observer.','Mark where conversion from engineering units to machine representations occurs.','Specify three faults: stuck-high input, stuck-low input, and a disconnected actuator.','Write an alarm and a separate fail-safe requirement that do not depend on the display workstation.','Label which pieces of this system could be emulated on the MSP430 laboratory bench and which require an industrial design beyond the course.'),
'questions':('What would an oscilloscope prove that a printed telemetry line cannot?','Which components continue operating if the host PC powers down?','Why is a watched software loop not the same as an emergency-stop circuit?','What historical advantage did modular DEC interfaces offer plant engineers?'),
'answers':'''The oscilloscope observes the electrical event directly, subject to its own calibration and probe loading. The local controller can keep executing when the PC is absent, but that is a design requirement to be demonstrated. An emergency stop must use suitable independently engineered protective hardware; a loop in a small teaching CPU cannot be assumed to provide the necessary safety function. Modular buses and peripherals supported adaptation to varied instruments and processes.''',
'evidence':'One annotated block diagram; one interface contract table; a priority/deadline table; a fault-response sketch; a signed statement of what was assumed rather than observed.'
},
{
'id':'02','title':'A PDP-11 from the Programmer’s Chair','theme':'Registers, stack, octal notation, and an emulator',
'context':'''The PDP-11 had eight visible 16-bit registers. R6 acted as stack pointer, R7 as program counter, and R0 through R5 were ordinary working registers. That compact and regular model remains one of the most teachable examples of assembly language. The PDP-11 community's use of octal can initially distract learners whose later work is mostly hexadecimal. Explain octal as a historical convention aligned to groups of three bits, not as a magical hardware feature. A value of decimal 15 is octal 17, and the same 16-bit pattern can be written in several bases.''',
'model':'''Trace the loop in code/pdp11/01_register_loop.mac before running it. Initially R0=5 and R1=0. The ADD instruction adds the current count to the accumulator; SOB decrements the count and branches when the new result is nonzero. Record each iteration and the instruction that changes R0. The expected final arithmetic total is decimal 15. A halted simulator is evidence of instruction execution only when the program has actually been assembled, loaded, and inspected.''',
'prediction':'Write the values of R0 and R1 after every execution of SOB, before opening any simulator. State whether the last iteration adds 1 or 0 and justify the order of operations.',
'procedure':('Inspect the MACRO-11-style source file and underline register operands and immediate values.','Use a PDP-11 simulator with documented CPU and loader configuration; select an appropriate assembler or a verified binary input.','Load the program and stop it at entry. Record PC, SP, R0 and R1.','Step ADD and SOB separately for the first two iterations; note PC changes when the branch is taken.','After HALT, inspect accumulator state, compare with paper arithmetic, and record the exact emulator command sequence.'),
'questions':('How do the register aliases SP and PC affect ordinary arithmetic instructions?','Why might a programmable machine provide a single decrement-and-branch instruction?','What is gained by using an emulator first, and what does the emulator not prove?','What changes in the trace if R0 is initialized to 1?'),
'answers':'''A programmer may address registers directly, but R6 and R7 have important execution roles and should not be treated as scratch storage casually. SOB reduces instruction count for a common loop pattern. Simulation proves behavior of the configured emulation and the loaded binary; it does not prove real peripheral timing or the electrical behavior of a 1970s machine.''',
'evidence':'Source listing, a five-row trace table, final register dump, simulator command record, and an explanation of octal versus decimal representation.'
},
{
'id':'03','title':'Two Instruction Sets in Conversation','theme':'PDP-11/MSP430 addressing-mode comparison',
'context':'''The comparison becomes strongest when it moves beyond mnemonic resemblance. The PDP-11 uses three-bit register fields and three-bit mode fields to specify source and destination for many two-operand instructions. The MSP430 allocates four bits per register to expose sixteen architectural registers; its source receives more addressing-mode flexibility than its destination. The compact fixed word requires architectural compromises. The MSP430 R2 and R3 encodings recover useful constants and special forms without requiring a new memory word for every such value. That is a useful design tradeoff to examine without claiming that either chip was derived directly from the other.''',
'model':'''Use a three-column translation table: programmer intent, PDP-11 expression, MSP430 expression. For example, add a value held in one register to another, access an indexed memory element, and walk a word array with post-increment. Then assemble at least two MSP430 examples and record each full instruction word and any extension words. Compare the binary cost of MOV.W #1,R5 with ADD.W #1,R5 in the chosen assembler. Do not infer actual encoding from the printed mnemonic alone.''',
'prediction':'Predict which instruction forms could need extension words, and why a commonly used immediate constant could sometimes avoid them.',
'procedure':('Draw the PDP-11’s eight registers and the MSP430’s sixteen; label PC, SP, SR, and constant-generator roles.','Annotate MOV, ADD, and an indexed memory read in both syntaxes.','Take one instruction and manually mark opcode, source-register, addressing-mode, and destination fields according to the TI guide.','Build the MSP430 fragment under the installed assembler and save the map or listing.','Compare each prediction with the machine words and annotate all discrepancies.'),
'questions':('Why is autoincrement in a source operand attractive for reading arrays?','Why is a destination-mode restriction a reasonable cost of having more registers?','What does an assembler pseudo-instruction conceal?','What evidence would be needed to claim a direct historical design influence?'),
'answers':'''Autoincrement combines a fetch and a pointer update. A fixed-size instruction encoding has limited bit positions, and expanding register selection consumes some of them. Emulated instructions can hide one or more underlying machine instructions. Similarity supports architectural comparison but not an assertion about specific design-team decisions without documentary evidence.''',
'evidence':'Paired code listings, encoding sketches, a hardware-specific assembler build log, and an explicit description of architectural differences.'
},
{
'id':'04','title':'A Thousand Hertz Is a Claim to Test','theme':'Timer_A, calibrated DCO, independent Pico measurements',
'context':'''The first laboratory on the real MSP430 builds a deliberately simple 1 kHz output on P1.6. A nominal 1 MHz SMCLK clocks Timer_A. Up mode counts from 0 to CCR0, inclusive. CCR0=499 means 500 timer ticks. When output mode 4 toggles TA0.1 once for each timer period, a complete square-wave cycle requires two toggles: the ideal frequency is 1,000,000/(2 × 500), or 1000 Hz. The hardware timer changes the pin while the CPU can remain in an idle loop. This distinction is essential: a timer-driven waveform is not a bit-banged software loop.''',
'model':'''The frequency meter is a second system with its own timebase. Even if the target is nominally set to 1 MHz, actual drift and temperature can change the signal. The Pico counts rising edges during a measured gate. Capture both pulse count and elapsed duration, not only a formatted hertz number. A one-second gate gives roughly one-hertz count resolution before clock and gate errors are considered; apparent extra decimal digits do not establish matching accuracy. The duty cycle may depend on compare timing and output mode. Measure that separately when a pulse-width tool is available.''',
'prediction':'Derive the expected frequency for CCR0 values 499, 999, and 249 before changing the program. Explain why CCR0=999 does not mean 999 timer ticks.',
'procedure':('Verify physical 3.3 V target power, proper pin mapping, debugger isolation, and shared signal ground.','Build the known Day One assembly example and preserve build/verification output.','On the Pico set generator OFF, input GP3, one sample, and a 1000 ms gate; read back STATUS?.','Record five separate captures at CCR0=499, including pulse count and actual elapsed microseconds.','Change only CCR0 to 999; rebuild and reflash. Collect a second dataset and compare with the prior prediction.'),
'questions':('Why does the CPU’s main loop not set the edge spacing?','Could a 1000.000 reading be wrong?','What measurement would establish duty cycle?','How would you distinguish target clock error from meter clock error?'),
'answers':'''Timer_A determines edge intervals after being configured, independent of repeated CPU instructions. Display formatting cannot certify accuracy. An edge-timestamp or logic-analyzer trace can establish high/low time. Independent calibrated references or a common timebase characterization are required to attribute absolute frequency error to one clock rather than the other.''',
'evidence':'Photograph or wiring sketch, instrument STATUS? transcript, program checksum, five actual frequency captures for each setting, and a table of predicted versus observed results.'
},
{
'id':'05','title':'One Behavior, Two Programming Languages','theme':'Assembly, C, generated code, and compiler discipline',
'context':'''A C statement that writes a timer register does not execute the same instructions in every toolchain. The compiler may use different instruction forms, initialize the stack, insert startup code, and choose an optimizer strategy. Yet the peripheral can still receive the same configuration and produce the same external signal. That is the right criterion for a controlled comparison: equivalent hardware state and observable behavior, not an identical count of assembly lines.''',
'model':'''Place the original assembly Timer_A initialization beside code/msp430/01_timer_1khz.c. Identify the clock calibration constants, pin-function selection, CCR0, CCR1, output mode, and timer-start register. A key issue is whether an instruction is executed once during setup or repeatedly during output generation. A code-generation difference in setup may not change a hardware timer’s steady-state frequency, while a difference in software-delay implementation can alter a bit-banged waveform dramatically.''',
'prediction':'Before compiling the C version, predict which C statements will require memory writes and which may be optimized away. Explain why the `volatile` hardware register definitions matter.',
'procedure':('Capture the assembly baseline under an unchanged clock and meter configuration.','Compile the C candidate using a documented TI or msp430 GCC environment; save all warnings and linker output.','Review the reset vector, startup, register writes, and generated disassembly.','Flash only after checking target supply and pin compatibility; capture five new Pico gates.','Compare measured frequency, firmware source, toolchain version, and register-state equivalence.'),
'questions':('Is a shorter assembly listing necessarily faster at the pin?','Why might a compiler initialize RAM before main?','What would change if the output were controlled by a delay loop instead of Timer_A?','Which differences constitute an invalid comparison?'),
'answers':'''For a hardware-generated signal, setup instruction count need not affect steady-state output frequency. C runtime startup is an implementation requirement, not a defect. A delay loop’s timing is dependent on instruction sequences and the clock, and therefore is much more sensitive to code generation. Changes in power, clock source, pin loading, or meter configuration confound a language comparison.''',
'evidence':'Build log, assembler and C source hashes, selected disassembly, hardware timer state, paired capture sheets, and an interpretation limited to the measured properties.'
},
{
'id':'06','title':'A Bit Reaches the Outside World','theme':'Memory-mapped I/O, polarity, and switch input',
'context':'''Memory-mapped I/O is the concrete bridge between the PDP-11 and the MSP430. A memory address can represent a physical interface register, not merely ordinary RAM. Writing a one to a GPIO direction register changes a pin into an output; clearing the corresponding bit changes it back into an input. Writing to an output latch may not light an LED if the signal is inverted by the board wiring, a transistor, or an active-low circuit. Engineering begins by checking the schematic and the pin voltage.''',
'model':'''Use the code/msp430/02_gpio_switch.c example. Configure P1.0 as an output and P2.0 as an input with a pull-up. A button connected to ground makes a pressed state read as logic zero. Students must draw both the physical circuit and the binary value in the input register; the false intuition that pressed always means one should be explicitly challenged. On an unverified custom board, a safe logic analyzer or voltmeter comes before assumptions about the indicator lamp.''',
'prediction':'For a P2.0 switch that shorts the line to ground when pressed, predict P2IN & BIT0 in the pressed and released states. Write the binary mask and show how P1DIR changes.',
'procedure':('Confirm P1.0 LED polarity and P2.0 button-to-ground connection on the actual board.','Compile and flash the GPIO candidate source without combining it with the Timer_A experiment.','Measure P2.0 idle voltage and pressed voltage, and record both digital input states.','Observe the LED or measured P1.0 output under each button condition.','Disconnect power; describe what additional protection would be needed for a real industrial switch input.'),
'questions':('What does `P1OUT |= BIT0` preserve?','Why can contact bounce matter even if the LED looks steady?','Why is an internal pull-up not a general solution for industrial field wiring?','What can a measured 3.3 V pin tell you, and what can it not tell you?'),
'answers':'''The OR assignment changes the selected bit while preserving other latch bits. Mechanical contacts bounce on short time scales. Industrial signals may require filtering, isolation, surge handling, and appropriate voltage/current interfaces. A measured voltage demonstrates an electrical state at a specific moment, not correct software behavior across all scenarios.''',
'evidence':'Switch truth table with measured volts, GPIO-register snapshot or code trace, LED/pin results, and a note on wiring-dependent polarity.'
},
{
'id':'07','title':'When Time Becomes a Requirement','theme':'Interrupts, polling, jitter, and scheduling',
'context':'''An industrial control system cares about deadlines, not just average execution speed. A 1 ms sensor event may be routine in one process and dangerously late in another. The PDP-11 family used priority interrupts and real-time software environments to manage multiple device demands. On the MSP430 a timer interrupt provides a small, accessible laboratory for understanding the same fundamental problem: the program is asked to suspend ordinary work, save enough state, perform a bounded action, and return.''',
'model':'''Code/msp430/03_interrupt_led.c configures Timer1_A to interrupt on a 100 ms nominal interval. The ISR toggles an LED latch and returns. The waveform is distinct from the hardware Timer_A compare output. Delays from interrupt masking, competing code, or other interrupts can create jitter in a software-driven edge; a hardware output compare can be a better option when edge timing is the essential requirement. An interrupt provides responsiveness but does not magically guarantee a deadline.''',
'prediction':'With a 250 kHz Timer1_A clock and CCR0=24999, calculate the nominal interval between ISR entries. How long is a complete cycle if the ISR toggles once per entry?',
'procedure':('Draw the timeline: timer period, interrupt request, CPU entry, GPIO write, return.','Build the ISR example; confirm actual interrupt vector and CPU/compiler conventions.','Observe P1.0 toggles. If supported, time-stamp edges using a suitable capture tool.','Add a short bounded foreground computation; measure whether observed timing changes.','Discuss a deliberately hypothetical case where ISR code takes longer than its scheduled period.'),
'questions':('What is the difference between interrupt latency and interrupt execution time?','Why should an ISR avoid expensive printing?','When is polling preferable to interrupts?','How might the PDP-11’s priority scheme affect lower-priority industrial tasks?'),
'answers':'''Latency runs from the external request to start of handler execution. Execution time is the handler’s own work. Blocking telemetry in an ISR makes the worst-case response hard to bound. Polling may be simpler for slow or noncritical tasks. Priority can protect urgent work while starving lower-priority work if load and scheduling are not engineered carefully.''',
'evidence':'Clock and deadline calculation, firmware version, GPIO timing trace, source explanation, and bounded assumptions about worst-case response.'
},
{
'id':'08','title':'Teaching a Machine to Report','theme':'UART framing, telemetry, versioned data contracts',
'context':'''An industrial controller requires a way to expose its state to an operator, data historian, or diagnostic computer. A terminal connection on a PDP-11 served one part of this purpose; a small MCU serial port serves the same abstract purpose today. The controller must still function if the connection disappears. Separating the telemetry channel from the real-time decision loop is an important design habit. It also makes the experimental record more trustworthy: students should know which fields were measured, calculated, guessed, or defaulted.''',
'model':'''The MSP430G2553 USCI UART can send bytes from P1.2 at an appropriate baud configuration. At nominal 1 MHz, the candidate example uses a baud divider for approximately 9600 bps. UART data consists of individual frames, typically one start bit, eight data bits, and a stop bit. A UART character can therefore take roughly ten bit times even before software formatting. Recording a transmission on a logic analyzer gives independent evidence of the framing and bit period.''',
'prediction':'Compute the approximate on-wire time of a 30-byte message at 9600 baud in 8N1 format. Decide whether sending that message in a 100-µs critical section would be acceptable.',
'procedure':('Inspect the board J3 header and verify TTL-level 3.3 V signal compatibility.','Connect MCU TX to adapter RX and share ground; do not connect two active power sources.','Compile the UART hello example and capture the literal transmitted bytes in a terminal.','Check baud and framing with an independent tool or two agreeing configurations.','Define a CSV-style record with version, sequence, sensor status, raw temperature, controller state, and error code.'),
'questions':('What information is lost when a message contains only a formatted temperature?','How should a receiver handle a truncated message?','Why is printf size relevant on a microcontroller?','What does the host need to do when a sequence number is missing?'),
'answers':'''Without raw values, units, conversion status, or error flags, a formatted temperature is difficult to audit. A receiver must detect and reject incomplete frames/records instead of interpreting stale fields. Full formatting libraries can consume scarce code and RAM. Missing sequence values should be explicitly reported in the observation record rather than silently interpolated.''',
'evidence':'Actual serial transcript, wiring map, baud assumption and calculation, record schema, and one intentionally malformed-record handling test.'
},
{
'id':'09','title':'The Electrical Grammar of One Wire','theme':'Bus release, timing slots, and sensor presence',
'context':'''The DS18B20 1-Wire protocol is exceptionally educational because the wire is not simply driven to zero or one by one participant. The idle line is high because a pull-up supplies current. The master and devices assert low, then release the bus. A master that actively drives high during a device response can create electrical contention. The simplest correct mental model is therefore not “send one and zero”; it is “pull low and release”, followed by carefully timed sampling. That is exactly the kind of low-level behavior the PDP-11 era taught engineers to examine at hardware interfaces.''',
'model':'''The device data sheet defines reset, presence, write-zero, write-one, and read time slots. A reset begins with a master low interval of at least 480 µs. After release, a sensor may assert a presence pulse in a defined response window. A valid software delay count alone is insufficient evidence: rising edges are influenced by the pull-up resistor, bus capacitance, output-direction switching, and compiler-generated code. At the present 1 MHz DCO stage, source-level cycle delays must be bench-characterized. Work with externally powered three-wire mode rather than parasite power initially.''',
'prediction':'Sketch the reset and presence waveform with ownership labels. Mark the interval in which the master drives low, the interval in which nobody actively drives, and the interval in which the sensor can pull low.',
'procedure':('Verify the DS18B20 package orientation and a single pull-up to the same 3.3 V logic domain.','Confirm the candidate P1.7 net is free from active I²C devices or alternative outputs.','With the sensor absent, measure bus idle-high voltage and the master reset pulse.','Attach one externally powered sensor; measure the presence pulse without interpreting a single low reading as sufficient.','Independently capture write-zero, write-one, and read slots; compare against the manufacturer’s timing table.'),
'questions':('Why does internal GPIO pull-up resistance often require additional review?','Why is 1 kHz frequency measurement not a test of a 6 µs low pulse?','What could produce a false presence detection?','Why should interrupts be bounded or excluded only in critical short slots?'),
'answers':'''Weak or poorly controlled pull-ups and wire capacitance can stretch the rising edge. Frequency and pulse width are distinct measured properties. Noise, stuck-low wiring, or a mistimed sample can impersonate presence. Blocking interrupts too long undermines system response; the critical interval must be small and explicitly justified.''',
'evidence':'Waveform screenshots or time-stamped edges, measured reset and presence widths, power/pull-up measurements, and explicit device-present versus device-absent test outcomes.'
},
{
'id':'10','title':'Nine Bytes Become a Temperature','theme':'1-Wire commands, fixed-point decoding, and CRC',
'context':'''Once a 1-Wire line can transmit bits reliably, the protocol can finally become a sensor instrument. The DS18B20 provides a unique ROM identity and a nine-byte scratchpad. Its first two scratchpad bytes represent signed temperature in units of 1/16 °C at 12-bit resolution. A correct byte value is not necessarily a current conversion, and an accurate display cannot be inferred from the number of fractional bits. This lab should separate the transport problem, the integrity problem, the arithmetic problem, and the actual physical temperature problem.''',
'model':'''For one verified device, send reset/presence, Skip ROM (0xCC), Convert T (0x44), wait until conversion is complete, reset again, Skip ROM, Read Scratchpad (0xBE), then obtain all nine bytes. Calculate CRC over bytes 0..7 and compare with byte 8 before decoding. With raw words 0x01D0 and 0xFF5E, the mathematical values are +29.000 °C and -10.125 °C respectively; these are synthetic examples, not collected observations. A default power-on 85 °C pattern is a reason to check conversion completion rather than automatically publish.''',
'prediction':'Compute Celsius and Fahrenheit for raw values +464 and -162 (sixteenths of a degree). Predict how a flipped scratchpad bit affects CRC acceptance.',
'procedure':('Test the supplied Python CRC and temperature-decoding code with known synthetic cases.','Record a real device ROM where possible; do not assume an arbitrary set of bytes belongs to a sensor.','Use the validated transport routines to run the full conversion/read sequence for one device.','Save raw nine-byte scratchpad transactions, CRC status, power mode, conversion settings, and timing.','Compare measured temperature with an independent thermometer and describe sensor placement and thermal lag.'),
'questions':('Does a valid CRC demonstrate temperature accuracy?','What does 0.0625 °C resolution mean, and what does it not mean?','Why must negative values be decoded as signed 16-bit?','Why is the maximum 12-bit conversion time relevant to scheduling?'),
'answers':'''CRC checks integrity of bytes delivered, not sensor calibration. Representation granularity is not absolute measurement uncertainty. Two’s-complement interpretation is necessary for negative readings. A maximum conversion interval informs when data may legitimately be read and how the controller schedules other tasks.''',
'evidence':'A nine-byte raw transaction, CRC calculation, decoded units, conversion-completion evidence, and an independent physical comparison with limitations.'
},
{
'id':'11','title':'A Temperature Supervisor That Fails Safely','theme':'Hysteresis, state machines, and fault injection',
'context':'''The capstone controller uses the smallest possible control law that still demonstrates memory and state. A cooling-request indicator turns ON at or above 30 °C and turns OFF at or below 28 °C. Between these thresholds it remembers its previous legitimate state. If the input is missing, CRC-invalid, out of date, or otherwise inadmissible, the program enters FAULT and sets a separately defined safe output state. This is an educational output indicator, not a qualified safety controller and not a mains-connected thermostat.''',
'model':'''The controller receives temperature as signed integer sixteenths of a degree, matching the DS18B20 raw scale. `control_step` produces OFF, ON, or FAULT; a separate driver translates state into an output latch. That separation is valuable because the algorithm can be tested on a host PC without invoking an MSP430 header, simulator, or sensor. The software can be wrong even when the sensor bytes are correct, so exercise threshold boundaries and transition history explicitly. A failed sensor read should never be silently substituted by the last good value without showing the age and a defined policy.''',
'prediction':'Starting in OFF, run this sequence: 27.5, 29.0, 30.0, 29.0, 28.0 °C. Predict the resulting state after each sample. Then inject one CRC-invalid sample and predict FAULT.',
'procedure':('Compile and run the platform-independent host tests of the state machine.','Construct a transition table with values just below, equal to, and just above both thresholds.','Inject invalid CRC and stale data as distinct simulated faults; document how the input validity flag is obtained.','Only after host tests pass, integrate with verified sensor acquisition and an LED output.','Demonstrate that disconnecting the host UART has no effect on the local state progression.'),
'questions':('What is the benefit of hysteresis over a single threshold?','Why must the fault output action be defined independently from control state names?','How can the host PC prove the algorithm but not prove the entire controller?','What additional evidence is needed before using a real fan or mechanical actuator?'),
'answers':'''Hysteresis prevents rapid oscillation near a noisy threshold. An enumerated state is not itself a safe physical electrical level; output polarity, failure modes, and actuator behavior must be defined. Host tests isolate algorithmic transitions; they cannot validate GPIO wiring, thermal lag, sensor integrity, or interrupts. Real actuation requires protection, current limits, independent safety behavior, and process validation.''',
'evidence':'Complete transition table, passing host test transcript, one injected fault, a local-output bench demonstration, and a safety limitation statement.'
},
{
'id':'12','title':'The Engineering Notebook as a Public Artifact','theme':'Capture, Analyze, Publish and independent replication',
'context':'''A working demonstration is a beginning, not a finished engineering result. The temptation to report only clean numbers is particularly strong in classrooms, where failures consume time and a beautiful dashboard can look more authoritative than a handwritten record. The CAP method counters that temptation by preserving raw observations, recording the actual instrument configuration, and naming limitations that cannot be removed by formatting. In industrial automation, these habits are close relatives of calibration control, change management, commissioning records, and maintenance logs.''',
'model':'''The report should identify the actual hardware and software versions, a question, an a priori prediction, a clear schematic or annotated wiring photo, raw measurements, calculations, uncertainty discussion, faults encountered, and a falsifiable conclusion. A sample frequency with many decimal places may be repeatable without being accurate. A scratchpad with a correct CRC may be internally consistent while reporting the temperature of a badly mounted sensor rather than the process. The report should make those distinctions visible.''',
'prediction':'Write one claim you expect to be able to defend about the 1 kHz waveform and another claim you cannot defend without a calibrated reference. Put a specific test against each.',
'procedure':('Inventory the source, firmware, board, sensor, Pico, and host tool versions.','Choose one real dataset and preserve the original CSV or raw terminal capture read-only.','Run the Python analyzer, check its output by hand, and add the measurement conditions.','Include the strongest failure or anomaly rather than silently deleting it.','Ask an independent reader to reproduce the calculation and identify one alternative explanation.'),
'questions':('How is a measurement different from a calculated expectation?','What is missing from a report containing only a chart?','What is the minimum proof of a successful 1-Wire transaction?','Which revision-control facts should survive a reboot months later?'),
'answers':'''Measurements depend on instruments and conditions; calculations depend on assumptions and models. Charts without raw data and setup prevent meaningful independent review. Successful 1-Wire requires electrical timing evidence plus valid protocol results, not simply a plausible temperature. Exact source revision, build command, firmware hash, instrument settings, wiring, and test date make the work recoverable.''',
'evidence':'A complete CAP paper, raw data appendix, source hashes, repeatability and uncertainty explanation, feedback from an independent reviewer, and clear status labels.'
},
]
