from pathlib import Path
import runpy, os, re, shutil, subprocess, sys, zipfile, hashlib, textwrap, copy, tempfile
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_BREAK,WD_LINE_SPACING
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_COLOR_INDEX
from PIL import Image
import fitz

ctx=runpy.run_path(str(Path(__file__).resolve().parent/'make_figures_and_labs.py'))
LABS=ctx['LABS']; OUT=Path(__file__).resolve().parents[1]
OUT.mkdir(exist_ok=True)
COVER=OUT/'figures/cover.png'
MANUSCRIPT=(OUT/'CORE_MANUSCRIPT.md').read_text(encoding='utf-8')
# The editable core manuscript is already included in CORE_MANUSCRIPT.md.
BLUE=RGBColor(12,36,55); TEAL=RGBColor(22,124,108); GRAY=RGBColor(79,90,96); LIGHT=RGBColor(232,240,238)

exec((OUT/'editorial/augment_snippet.py').read_text(encoding='utf-8'))
exec((OUT/'editorial/extension_snippet.py').read_text(encoding='utf-8'))

CHAP_SUM={
1:('A working machine, not an isolated CPU','Industrial process, transducer, I/O interface, control path, evidence path'),
2:('A program is a controlled change of machine state','Octal, registers, program counter, stack pointer, SOB, status flags'),
3:('The machine must answer while the plant keeps moving','RT-11, RSX-11M, interrupt, response time, deadline, worst case'),
4:('Architectural resemblance reveals engineering tradeoffs','Addressing mode, instruction encoding, source/destination, constant generator'),
5:('A predicted waveform becomes a measured event','DCO, SMCLK, Timer_A, compare, toggle, frequency counter, gate'),
6:('One addressed bit changes a physical voltage','P1DIR, P1OUT, switch input, pull-up, GPIO polarity, volatile'),
7:('Deadlines matter more than average speed','Latency, interrupt service routine, jitter, timer, masking'),
8:('The controller explains itself through a serial link','UART, framing, baud, protocol, parsing, error status'),
9:('An electrical bus is a timed conversation','1-Wire, release, pull-up, reset, presence, slot, rise time'),
10:('A useful reading requires more than correct arithmetic','Scratchpad, two’s complement, CRC-8, resolution, accuracy'),
11:('Control must define what happens when information fails','State machine, hysteresis, stale sample, safe output, fault'),
12:('Evidence turns an experiment into shareable engineering','Traceability, raw data, uncertainty, reproducibility, provenance'),
13:('The operator and instructor have different responsibilities','Readiness gate, formative assessment, operator checklist'),
14:('Continuity of ideas, not identity of hardware','Architecture, modularity, real time, instrumentation, deployment')}

SUPPLEMENTS={
1:[('Case study: an imagined rolling-mill inspection station', '''Suppose a continuously moving steel strip passes a thermal inspection station. A pyrometer produces a temperature signal, a length encoder tracks the strip position, and an alarm must be associated with the correct section of material. A computer can help associate a particular sample with a position, apply the inspection rule, and make a record. That does not imply the computer itself should directly energize heavy machinery. A physically independent protective circuit is a separate engineering obligation.\n\nFor the course, reduce the plant to a harmless model. A learner presses a switch to represent the arriving strip; a timer counts intervals; a temperature reading is captured; an LED signifies that a limit has been exceeded. The value of the exercise is preserving the full information chain, including time and uncertainty, while stripping away hazardous actuation.\n\nThe important historical contribution of the PDP-11 was not a particular factory algorithm. It was an adaptable and maintainable combination of CPU, I/O, storage, software, and application engineering. The computer could be reprogrammed to solve a different instrumentation problem without redesigning the entire decision apparatus.''')],
2:[('Worked trace: five additions and a branch', '''A trace is more instructive than an unexplained correct total. Begin with R0 holding 5 and R1 holding 0. After the first ADD, R1 becomes 5. SOB then decrements R0 to 4 and branches to the loop. The sequence of accumulator values is 5, 9, 12, 14, 15. The sequence of loop-counter values after SOB is 4, 3, 2, 1, 0. On the final SOB, the zero count suppresses the branch.\n\nWhy is the instruction sequence teachable? The loop counter resides in a register, arithmetic writes another register, and the PC changes according to a branch condition. Nothing here is mystical. The useful skill is accounting for each state transition. Trace the MSP430 counterpart with DEC R0 renamed to MSP430 R4; do not assume the PC, SP, or assembler syntax are interchangeable.\n\nAn emulator is especially useful when a real PDP-11 is unavailable. It lets the learner inspect registers at single-instruction resolution. However, a software emulation of register transitions does not establish the electrical latency of a physical PDP-11 peripheral interface.''')],
3:[('A scheduling example: observation, control, and reporting', '''Consider three hypothetical activities: a protection-related limit input, a 10 ms measurement update, and a one-second operator report. Rank their response requirements before proposing CPU utilization. Average instruction throughput alone does not answer whether a limit event can be serviced on time. The latency distribution, critical sections, interrupt masking, and competing peripheral operations matter.\n\nThe PDP-11 era made this distinction visible because real-time operating systems had to coordinate devices with deadlines while still supporting conventional programs. Today the MSP430 can demonstrate the same basic separation without hosting RSX-11M: a timer interrupt provides an event, the foreground loop performs low-urgency work, and an external observer measures the resulting timing.\n\nDo not turn this into a blanket assertion that interrupts are always better than polling. Polling may provide simple, bounded behavior in a small controller. The choice depends on event rate, acceptable latency, interrupt interference, verification effort, and the work that must be done at each event.''')],
4:[('Why four more register-select bits change the design', '''An instruction format is a physical budget. A sixteen-bit instruction word cannot simultaneously allocate unlimited opcode bits, register bits, mode bits, and size control. The PDP-11’s three-bit register identifier selects one of eight registers; the MSP430’s four-bit field selects one of sixteen. Two named operands can therefore consume more of the fixed instruction word on the MSP430.\n\nThe MSP430 preserves many elegant source forms while restricting destination addressing. R2 and R3 encodings offer selected constants and special addressing operations. These are not inelegant afterthoughts to be memorized; they are clues to the design pressure imposed by an economical instruction representation.\n\nA learner should prove one encoding with the assembler listing instead of trusting this paragraph. Compile an immediate constant, an indexed operation, and a register-register ADD. Record the instruction words and extension words for each. Compare the source length with the stored machine-code length. That is a reproducible way to discuss code density without asserting that one architecture is universally superior.''')],
5:[('Worked computation: count period is not square-wave period', '''Assume SMCLK is nominally 1 MHz and Timer_A counts through the sequence 0 to 499. That is 500 clocks per counting interval. If the selected output mode toggles the output once each interval, the time between toggles is 500 microseconds. The time between matching rising edges is two intervals, or 1,000 microseconds. The nominal frequency is therefore 1 kHz.\n\nNow change CCR0 to 999 while keeping the same timer source. Each interval becomes 1,000 clocks; two intervals make an output cycle, and the expected output becomes 500 Hz. This controlled intervention is more informative than repeating the same measurement. It tests whether the observed circuit responds in the predicted direction and magnitude.\n\nNever substitute nominal clock assumptions for evidence. If the Pico gate depends on its own uncharacterized crystal, a frequency disagreement can arise in either instrument. The first experiment is about generating and comparing a waveform. Calibrating either timebase is a different experiment and must be described separately.''')],
6:[('Binary view of an active-low switch', '''An ordinary button can introduce three essential ideas at once: voltage is not a Boolean value, a register contains multiple independent bits, and physical polarity is a circuit property. With P2.0 configured as input and an enabled pull-up, an open switch typically reads as one. Closing the switch to ground pulls the pin low and makes the sampled bit zero.\n\nThe program may convert that raw bit to the semantic state “pressed.” The latter is an interpretation, not a voltage level. The statement `pressed = ((P2IN & BIT0) == 0);` is an explicit contract translating electrical behavior into a meaningful variable.\n\nThe motor-control analog is straightforward. A field input might be active low, normally closed, or isolated through an optocoupler. A developer who mistakes raw signal polarity for application meaning could reverse an alarm condition. Students should draw a truth table before claiming that an LED proves their software was correct.''')],
7:[('Jitter: compare two ways to move the same pin', '''Create one signal with a hardware timer compare output and another with an interrupt service routine that toggles a GPIO bit. Both may have similar average frequency. They are not equivalent instruments for precise edge placement. The hardware output-compare edge is tied to timer hardware; the software edge is delayed by interrupt recognition, entry, other interrupts, and the instructions preceding the port write.\n\nCapture many edges with a timing-capable instrument. For each adjacent pair, compute the interval. Report the minimum, maximum, and range as well as the mean. If the measurement resolution is coarse, say so. An attractive average cannot conceal unstable edges.\n\nThis is also a practical bridge back to RSX-11M. The software problem of selecting a task and the electrical problem of meeting a deadline are related, but not identical. Priority helps organize response, while measurement demonstrates whether a particular built system meets its declared timing budget.''')],
8:[('From characters to records', '''Start with one known character. A terminal that displays “A” demonstrates a useful first end-to-end path: an MCU loaded a transmit register, a serial peripheral framed the bits, an electrical link carried them, and a receiving tool decoded them under matching baud and parity settings. It does not show that every possible message or every power-up sequence is reliable.\n\nAdd a small structured record with explicit field names. A record such as `TEMP_C,25.0625,VALID,seq=17` is human readable, but its formal contract should also specify newline termination, units, allowed ranges, checksum policy if needed, and how missing records are detected. A sequence number exposes dropouts; timestamps require a defined clock source.\n\nThe telemetry path must not own the safety-related control decision. The MSP430 should remain capable of selecting its own safe output when the PC is detached. This separation is a modern miniature of the industrial distinction between a real-time control processor and a remote operator terminal.''')],
9:[('Why the 1-Wire signal is not ordinary serial data', '''A 1-Wire device and its master cooperate electrically on one pulled-up data conductor. A normal idle is high because a resistor supplies current, not because every participant drives the wire high. To start a low pulse, the master configures an output that sinks current. To release the line, the master stops driving it low, and the pull-up returns it high.\n\nThis electrical convention matters to firmware: a line that remains actively driven high cannot safely coexist with a device attempting to signal low. The driver must separate “drive low” from “release.” A reset/presence exchange is consequently a time sequence of ownership changes, not simply a UART byte.\n\nMeasure the reset-low interval, the sensor response window, and representative write-one, write-zero, and read slots at the physical pin. Do not infer microsecond validity from observing a successful high-level temperature conversion. A 1 kHz frequency counter is useful elsewhere, but an edge-time capture or scope is necessary for the 1-Wire timing claim.''')],
10:[('Decode a negative temperature without magic', '''The DS18B20’s two low scratchpad bytes form a signed sixteen-bit integer representing sixteenths of a degree Celsius at 12-bit resolution. For example, the synthetic bytes 0x5E 0xFF make 0xFF5E. Interpreted as an unsigned integer this is 65374; interpreted as signed two’s complement it is −162. Dividing by 16 gives −10.125 °C.\n\nThis is an ideal boundary between embedded C and Python. The MCU should validate the bytes and publish a signed raw value with a validity flag. Python can present the temperature, graph a series, and perform further calculations. Neither language makes a reading accurate simply because it prints more digits.\n\nSeparate four claims: transmission integrity (CRC), computation correctness (fixed-point arithmetic), conversion completion (the device did finish taking a new reading), and measurement quality (the sensor accurately represents the physical object under test). Each claim requires a different type of evidence.''')],
11:[('A fail-safe policy is a separate specification', '''A threshold controller with hysteresis remembers a state. A cooler is commanded ON at or above 30 °C and OFF at or below 28 °C. Inside that interval, the prior valid command persists. This prevents needless rapid switching when temperature fluctuates near a single trip point.\n\nNow suppose the sensor disappears. Is “last command forever” acceptable? Usually not without a designed and justified policy. For a classroom indicator, the safe state can be LED OFF plus a separate fault LED ON. A real industrial system may require a different protective outcome, depending on what the actuator does and which hazards dominate. The safe state must be defined by the process requirements and then implemented and tested.\n\nThe algorithm can be tested on a normal PC using integer temperature data and synthetic faults. That is an economical method for verifying transitions before any wire is connected. The tests are important evidence about the algorithm, but not about sensor wiring, electrical noise, or the response of a physical fan.''')],
12:[('The strongest report contains an anomaly', '''A laboratory report is not merely a success announcement. If the 1 kHz meter reports 998 Hz during one trial, record that value and the test conditions. Repeat the measurement, check the gate configuration, and change one controllable variable. A result outside expectation is potentially more informative than a perfect-looking output, especially when it exposes a hidden assumption about the oscillator, loading, or gate timing.\n\nPreserve raw bytes and counts, not just interpreted temperatures and finished charts. Save the source version, compiler invocation, target part, wiring, meter settings, and date. This makes the work recoverable after a reboot, a device replacement, or a long interval between lessons.\n\nThe student’s final assertion should be no stronger than the evidence. “This board produced five readings near 1 kHz with the stated settings” is defensible after those captures. “This chip has an absolute clock accuracy of one part per million” would require a separate reference and uncertainty analysis.''')],
}

CODE_MAP={2:['pdp11/01_register_loop.mac'],4:['msp430/08_compare_register_loop.asm'],5:['msp430/01_timer_1khz.c'],6:['msp430/02_gpio_switch.c'],7:['msp430/03_interrupt_led.c'],8:['msp430/04_uart_hello.c'],9:['msp430/09_onewire_transport_CANDIDATE.c'],10:['msp430/06_ds18b20_decode.c'],11:['msp430/05_thermostat_logic.h'],12:['python/cap_analyze.py']}
exec((OUT/'editorial/final_expansions.py').read_text(encoding='utf-8'))
FIG_MAP={1:'industrial_loop.png',3:'roles.png',5:'timer_timing.png',9:'supervisor.png',11:'supervisor.png',12:'data.png'}
CHAPTER_LABELS=[]; PART_LABELS=[]; TOC_ITEMS=[]

# utilities

def shade(p, color='F0F4F2'):
    pr=p._p.get_or_add_pPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),color); pr.append(sh)
def border_bottom(p,color='D9E5E2'):
    pr=p._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); bt=OxmlElement('w:bottom'); bt.set(qn('w:val'),'single');bt.set(qn('w:sz'),'8');bt.set(qn('w:color'),color);pb.append(bt);pr.append(pb)
def keep(p): p.paragraph_format.keep_with_next=True

def fmt(p,s):
    # minimal inline markdown formatting
    patt=re.compile(r'(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)')
    for item in patt.split(s.replace('\\_','_')):
        if not item:continue
        if item.startswith('**') and item.endswith('**'):
            r=p.add_run(item[2:-2]);r.bold=True
        elif item.startswith('`') and item.endswith('`'):
            r=p.add_run(item[1:-1]);r.font.name='DejaVu Sans Mono';r.font.size=Pt(8.1);r.font.color.rgb=TEAL
        elif item.startswith('*') and item.endswith('*'):
            r=p.add_run(item[1:-1]);r.italic=True
        else:p.add_run(item)


def set_cell(cell, val, bold=False):
    cell.text='';p=cell.paragraphs[0];r=p.add_run(val.strip());r.bold=bold;r.font.size=Pt(8.5)
    cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER

def add_label(d,txt):
    p=d.add_paragraph(style='Eyebrow');p.add_run(txt.upper()); return p

def add_body(d,text):
    p=d.add_paragraph(style='Normal');fmt(p,text.strip()); return p

def add_heading(d,text,lvl=2):
    p=d.add_paragraph(style=f'Heading {lvl}');fmt(p,text);return p

def add_code(d,filename, maxlines=None):
    path=OUT/'code'/filename
    if not path.exists():return
    p=d.add_paragraph(style='Listing Label');p.add_run('LISTING  ·  '+filename).bold=True
    contents=path.read_text(errors='replace').splitlines()
    for i,line in enumerate(contents[:maxlines] if maxlines else contents):
        para=d.add_paragraph(style='Source Code')
        para.add_run(f'{i+1:>3}   {line.rstrip()}')
    if maxlines and len(contents)>maxlines:
        add_body(d,f'The complete file contains {len(contents)} lines and is included in the source archive. The excerpt is intended for code inspection, not as a separate compilable file.')
    cap=d.add_paragraph(style='Caption');cap.add_run('Code status: target source candidate unless independently compiled, flashed, and measured. See validation notes.')

def add_figure(d,name,cap):
    img=OUT/'figures'/name
    if not img.exists():return
    p=d.add_paragraph(style='Figure');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(img),width=Inches(6.9))
    q=d.add_paragraph(style='Caption');q.add_run(cap)

def add_field(p,f):
    r=p.add_run();start=OxmlElement('w:fldChar');start.set(qn('w:fldCharType'),'begin');r._r.append(start)
    r=p.add_run();instr=OxmlElement('w:instrText');instr.set(qn('xml:space'),'preserve');instr.text=f;r._r.append(instr)
    r=p.add_run();sep=OxmlElement('w:fldChar');sep.set(qn('w:fldCharType'),'separate');r._r.append(sep)
    r=p.add_run('1')
    r=p.add_run();end=OxmlElement('w:fldChar');end.set(qn('w:fldCharType'),'end');r._r.append(end)

def page_break(d):
    d.add_page_break()

def add_workbook(d,lab):
    n=lab['id']; add_heading(d,f'Field laboratory {n}: {lab["title"]}',2)
    p=d.add_paragraph(style='Subtitle Note');fmt(p,lab['theme'])
    for title,key in [('Industrial or historical context','context'),('Model and technical reasoning','model'),('Prediction before measurement','prediction')]:
        add_heading(d,title,3)
        for s in lab[key].split('\n\n'):add_body(d,s)
    add_heading(d,'Procedure and evidence gates',3)
    for i,item in enumerate(lab['procedure'],1):
        p=d.add_paragraph(style='Procedure');fmt(p,f'{i}. {item}')
    add_heading(d,'Interpretation questions',3)
    for i,item in enumerate(lab['questions'],1):
        p=d.add_paragraph(style='Question');fmt(p,f'{i}. {item}')
    p=d.add_paragraph(style='Evidence Brief');fmt(p,'**Required submission:** '+lab['evidence'])
    # one independently usable print worksheet page for each lab
    page_break(d)
    add_label(d,f'WORKSHEET {n}  /  REPRODUCIBLE LAB RECORD')
    add_heading(d,lab['title'],2)
    add_body(d,'Name / team: __________________________________  Date: _________________')
    add_body(d,'Target board and revision: __________________________  Instrument: __________________')
    add_body(d,'Firmware or simulation revision: ______________________  Clock / settings: ______________')
    add_heading(d,'Question, prediction, and test conditions',3)
    for _ in range(3):
        p=d.add_paragraph('________________________________________________________________________',style='Worksheet')
    add_heading(d,'Actual observations — never substitute predicted numbers',3)
    tab=d.add_table(rows=6,cols=4,style='Table Grid')
    for j,h in enumerate(['Trial / state','Observed result','Units / settings','Note / anomaly']):set_cell(tab.cell(0,j),h,True)
    for i in range(1,6):
        set_cell(tab.cell(i,0),str(i));
        for j in range(1,4):set_cell(tab.cell(i,j),' ')
    add_heading(d,'Analysis and limitations',3)
    for s in ['Calculated comparison:','What changed, and why?','What can these observations NOT establish?','Next controlled experiment:']:
        p=d.add_paragraph(style='Worksheet');p.add_run(s)
        p=d.add_paragraph('________________________________________________________________________',style='Worksheet')

def add_problem_set(d,n):
    qs=EXERCISES.get(n,[])
    if not qs:return
    add_heading(d,'Review and applied problems',2)
    p=d.add_paragraph(style='Subtitle Note');fmt(p,'These problems assess interpretation and engineering judgment, not vocabulary recall alone. Work before reading the instructor key.')
    for i,q in enumerate(qs,1):
        p=d.add_paragraph(style='Question');fmt(p,f'{n}.{i}  {q}')
    p=d.add_paragraph(style='Evidence Brief');fmt(p,'**End-of-chapter challenge:** Write a one-paragraph explanation that links one historical architectural choice with one measurable effect on your MSP430 bench.')

def add_review_record(d,lab):
    n=lab['id']
    page_break(d)
    add_label(d,f'FIELD RECORD {n}  /  ANALYSIS, FAULTS, AND REPLICATION')
    add_heading(d,'The evidence behind the result',2)
    add_body(d,lab['title']+'  •  Complete only after collecting real data or recording a documented failed attempt.')
    add_heading(d,'Equipment and exact reproducibility information',3)
    for labline in ['Board / part / revision:', 'Firmware source path, version, and build command:', 'Instrument, reference and live configuration:', 'Wiring diagram, power, clock and signal conditions:']:
        add_body(d,labline+'  __________________________________________________')
    add_heading(d,'Explain your observation',3)
    for q in lab['questions'][:3]:
        add_body(d,'**Prompt:** '+q)
        for _ in range(2):d.add_paragraph('_____________________________________________________________________',style='Worksheet')
    add_heading(d,'Failure and uncertainty log',3)
    tab=d.add_table(rows=4,cols=3,style='Table Grid')
    for i,h in enumerate(['Observed anomaly','Alternative explanation','Next discriminating test']):set_cell(tab.cell(0,i),h,True)
    for i in range(1,4):
        for j in range(3):set_cell(tab.cell(i,j),' ')
    add_heading(d,'Publication decision',3)
    add_body(d,'Claim supported by the record: __________________________________________')
    add_body(d,'Claim not yet supported: __________________________________________________')
    add_body(d,'Instructor / reviewer sign-off: _______________________  Date: _______________')

def add_extension(d,n):
    title,brief,submission=EXTENSIONS[n]
    page_break(d)
    add_label(d,f'ADVANCED FIELD INVESTIGATION {n:02d}  /  DESIGN AND REASONING')
    add_heading(d,title,1)
    add_body(d,brief)
    add_heading(d,'Design worksheet',2)
    for textline in ['Question and independent variable:','Controlled conditions and the alternative hypothesis:','Prediction and expected order of magnitude:']:
        add_body(d,'**'+textline+'**')
        for _ in range(2):d.add_paragraph('_____________________________________________________________________',style='Worksheet')
    add_heading(d,'Capture table',2)
    tab=d.add_table(rows=5,cols=4,style='Table Grid')
    for j,t in enumerate(['Trial / condition','Expected','Observed','Uncertainty / note']):set_cell(tab.cell(0,j),t,True)
    for i in range(1,5):
        for j in range(4):set_cell(tab.cell(i,j),' ')
    add_heading(d,'Deliverable',2)
    add_body(d,submission)
    add_body(d,'**Verification note:** Record failed or absent observations explicitly. Do not replace evidence with an ideal mathematical example.')

def add_chapter_tail(d,n):
    if n in SUPPLEMENTS:
        for sub,body in SUPPLEMENTS[n]:
            add_heading(d,sub,2)
            for s in body.split('\n\n'):add_body(d,s)
    add_problem_set(d,n)
    if n in CODE_MAP:
        add_heading(d,'Worked source listing',2)
        add_body(d,'Examine the source before changing it. Explain each register, constant, and externally observable effect; compile for the specified target and save all diagnostics. Code included here is educational candidate material, not a bench certification.')
        for fn in CODE_MAP[n]:add_code(d,fn)
    if n in FIG_MAP:add_figure(d,FIG_MAP[n],f'Figure {n}.1 — Conceptual illustration for Chapter {n}; not a verified wiring diagram.')
    if 1<=n<=12:
        page_break(d)
        add_workbook(d,LABS[n-1])
        add_review_record(d,LABS[n-1])
        add_extension(d,n)
    elif n==13:
        add_heading(d,'Field-operation rubric',2)
        for item in ('Safety and pin-map preflight must pass before energizing the board.','Every practical experiment includes one pre-registered prediction and a measured result.','A failed bench run remains a valid documented investigation, never an invented successful measurement.','Instructor notes are placed in the end matter, away from student worksheets.'):
            p=d.add_paragraph(style='Bullet');fmt(p,item)

# create docx

def make_doc(toc_map=None):
    doc=Document();sec=doc.sections[0]
    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=Inches(.35);sec.bottom_margin=Inches(.35);sec.left_margin=Inches(.35);sec.right_margin=Inches(.35)
    sec.header_distance=Inches(.27);sec.footer_distance=Inches(.28)
    styles=doc.styles
    base=styles['Normal'];base.font.name='Liberation Serif';base.font.size=Pt(10.8);base.font.color.rgb=BLUE
    base.paragraph_format.space_after=Pt(6);base.paragraph_format.line_spacing=1.15
    for style,size,color,top,bottom in [('Heading 1',20,BLUE,12,10),('Heading 2',13.5,BLUE,12,5),('Heading 3',11,TEAL,9,3)]:
        s=styles[style];s.font.name='Liberation Sans';s.font.size=Pt(size);s.font.bold=True;s.font.color.rgb=color
        s.paragraph_format.space_before=Pt(top);s.paragraph_format.space_after=Pt(bottom);s.paragraph_format.keep_with_next=True
    special={
      'Eyebrow':('Liberation Sans',8,TEAL,True,11,4),
      'Chapter Title':('Liberation Sans',24,BLUE,True,5,10),
      'Part Title':('Liberation Sans',34,BLUE,True,15,24),
      'Subtitle Note':('Liberation Sans',9.5,GRAY,False,3,8),
      'Source Code':('DejaVu Sans Mono',7.2,BLUE,False,0,0),
      'Listing Label':('Liberation Sans',8,TEAL,True,8,5),
      'Caption':('Liberation Sans',8.4,GRAY,False,4,11),
      'Figure':('Liberation Sans',8,GRAY,False,5,0),
      'Procedure':('Liberation Serif',10.3,BLUE,False,1,4),
      'Question':('Liberation Serif',10.4,BLUE,False,2,5),
      'Evidence Brief':('Liberation Sans',9.3,TEAL,False,9,7),
      'Worksheet':('Liberation Serif',10.3,GRAY,False,2,7),
      'Bullet':('Liberation Serif',10.8,BLUE,False,0,5)
    }
    for name,(fam,size,color,bold,before,after) in special.items():
        if name not in styles:styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
        s=styles[name];s.font.name=fam;s.font.size=Pt(size);s.font.color.rgb=color;s.font.bold=bold
        s.paragraph_format.space_before=Pt(before);s.paragraph_format.space_after=Pt(after)
        if name=='Source Code':s.paragraph_format.line_spacing=1.06
        if name=='Eyebrow':s.paragraph_format.keep_with_next=True
    # cover
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(0)
    p.add_run().add_picture(str(COVER),width=Inches(7.8),height=Inches(10.2))
    # front matter new section
    fs=doc.add_section(WD_SECTION_START.NEW_PAGE)
    fs.page_width=Inches(8.5);fs.page_height=Inches(11)
    fs.top_margin=Inches(.9);fs.bottom_margin=Inches(.8);fs.left_margin=Inches(.83);fs.right_margin=Inches(.73)
    fs.header_distance=Inches(.43);fs.footer_distance=Inches(.5)
    fs.different_first_page_header_footer=True
    # half title + title page
    add_label(doc,'Technical laboratory series')
    p=doc.add_paragraph();p.paragraph_format.space_before=Pt(110);r=p.add_run('FROM THE PDP-11\nTO THE MSP430');r.font.name='Liberation Sans';r.font.size=Pt(29);r.font.bold=True;r.font.color.rgb=BLUE
    p=doc.add_paragraph();p.paragraph_format.space_before=Pt(22);r=p.add_run('The Industrial Computer, Reimagined');r.font.size=Pt(20);r.font.italic=True
    p=doc.add_paragraph();p.paragraph_format.space_before=Pt(30);fmt(p,'**Hardware • Software • Industrial Automation • Measurement**')
    p=doc.add_paragraph();p.paragraph_format.space_before=Pt(120);fmt(p,'Final editorial textbook edition  ·  October 2026')
    add_body(doc,'An independent educational textbook and instructor laboratory companion.')
    page_break(doc)
    add_heading(doc,'Publication and technical notice',1)
    add_body(doc,'Final editorial textbook edition, October 2026. Prepared for independent study and laboratory instruction. No ISBN or external publisher is asserted. The PDP-11 and DEC operating systems are discussed historically; DEC, TI, Raspberry Pi, and their products are identified solely to describe the technology.')
    add_body(doc,'Examples labeled CANDIDATE are educational firmware and require target compilation and on-bench electrical verification before they are used. The included Python examples and host-side controller logic may be tested without the physical board, but host testing does not establish timing or electrical behavior on the MSP430.')
    add_body(doc,'This course uses 3.3 V logic, a safe LED output, and low-voltage signals. It does not qualify any design for industrial safety or mains-voltage actuation. Inspect the physical board, power source, and signal mappings prior to any connection.')
    add_heading(doc,'How to use this textbook',2)
    add_body(doc,'Each chapter begins with a guiding question and essential vocabulary, develops the theory using physical or historical examples, offers a source listing where appropriate, and ends with a field laboratory. The lab has a prediction stage, a bounded procedure, an evidence gate, and a reproducible worksheet. Instructor keys are collected in the back of the book rather than interleaved with student work.')
    add_body(doc,'The laboratory sequence is deliberately staged. A successful 1 kHz frequency measurement does not validate 1-Wire microsecond timing. A correct CRC does not prove temperature accuracy. A working software state machine is not a certified industrial controller.')
    page_break(doc)
    add_heading(doc,'Learning pathways and prerequisites',1)
    add_body(doc,'The course is designed for an instructor-led introductory embedded-systems class, a self-directed electronics bench, or an advanced historical-computing seminar. The same evidence standard applies to all three pathways, but the order of presentation may change.')
    for ttl,desc in [('Architecture pathway','Read Chapters 1–4 first, then simulate the PDP-11 loop and interpret actual MSP430 assembly encodings before wiring a board.'),('Physical-computing pathway','Begin with the safely verified 1 kHz apparatus in Chapter 5. Return to the historical architecture chapters as the significance of addressing and interrupts becomes evident.'),('Instructor/operator pathway','Use Chapter 13, the laboratory evidence sheets, and Appendix F before the first class. Assign the physical experiment only after the operator readiness gate has passed.')]:
        add_heading(doc,ttl,2);add_body(doc,desc)
    add_heading(doc,'Core hardware and software',2)
    for txt in ['Target: MSP430G2553, custom lab board or independently verified compatible LaunchPad arrangement, and a known-good debugger.', 'Instrument: Raspberry Pi Pico/Pico W with suitable frequency-counting firmware and, for 1-Wire, a separate verified pulse-capture capability.', 'Host: development toolchain, a text editor, a compatible UART interface, and Python for analysis.', 'Optional: PDP-11 emulation with correctly matched assembler and simulator documentation.', 'Sensor: verified externally powered DS18B20 package, safe 3.3 V wiring, suitable pull-up, and independent thermometer.']:
        add_body(doc,'• '+txt)
    add_heading(doc,'Evidence maturity labels',2)
    for txt in ['REFERENCE — documented historical or manufacturer specification.', 'PAPER MODEL — computation or simulation, not an observation of physical hardware.', 'CANDIDATE — code requiring compiler, wiring, and timing validation.', 'HOST-TESTED — software logic tested on a computer, not on the target.', 'BENCH-VERIFIED — an actual captured result with recorded setup and conditions.']:
        add_body(doc,'• '+txt)
    page_break(doc)
    add_heading(doc,'Contents',1)
    add_body(doc,'Front matter  •  Preface  •  How to use the book  •  Chapter and laboratory sequence  •  Instructor keys  •  Appendices')
    contents=doc.add_table(rows=0,cols=2)
    contents.autofit=False;contents.columns[0].width=Inches(6.0);contents.columns[1].width=Inches(.65)
    outlines=[('Introduction — An engineering history that can be measured','chapter')]
    for part in ['Part I — The industrial computer and its architecture','Part II — The MSP430 becomes a physical experiment','Part III — Teacher’s and operator’s companion']:
        outlines.append((part,'part'))
        n0,n1=(1,4) if part.startswith('Part I —') else ((5,12) if part.startswith('Part II —') else (13,14))
        for n in range(n0,n1+1):
            for line in MANUSCRIPT.splitlines():
                if line.startswith(f'# Chapter {n} —'):
                    outlines.append((line[2:].strip(),'chapter'));break
    outlines.append(('Appendices','part'))
    for letter,title in [('A','Register comparison'),('B','Safe bench'),('C','CAP worksheet'),('D','References and provenance'),('E','Source inventory'),('F','Instructor answer key'),('G','Glossary and chapter locator'),('H','Engineering reference atlas')]: outlines.append((f'Appendix {letter} — {title}','appendix'))
    for label,kind in outlines:
        row=contents.add_row();c0,c1=row.cells
        p=c0.paragraphs[0];p.style='Normal';p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(5 if kind=='part' else 0)
        r=p.add_run(('   ' if kind!='part' else '')+label);r.font.name='Liberation Sans';r.font.size=Pt(9.2 if kind!='part' else 9.8);r.bold=(kind=='part');r.font.color.rgb=TEAL if kind=='part' else BLUE
        p2=c1.paragraphs[0];p2.alignment=WD_ALIGN_PARAGRAPH.RIGHT;p2.paragraph_format.space_after=Pt(3)
        r=p2.add_run(str(toc_map.get(label,'—')) if toc_map else '—');r.font.size=Pt(9);r.font.color.rgb=GRAY
    # Start main text as new section with Arabic folio
    main=doc.add_section(WD_SECTION_START.NEW_PAGE)
    main.page_width=Inches(8.5);main.page_height=Inches(11)
    main.top_margin=Inches(.79);main.bottom_margin=Inches(.78);main.left_margin=Inches(.9);main.right_margin=Inches(.75)
    main.header_distance=Inches(.38);main.footer_distance=Inches(.42)
    main.different_first_page_header_footer=False
    main.header.is_linked_to_previous=False;main.footer.is_linked_to_previous=False
    h=main.header.paragraphs[0];h.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    r=h.add_run('FROM THE PDP-11 TO THE MSP430');r.font.name='Liberation Sans';r.font.size=Pt(7.5);r.font.color.rgb=GRAY
    border_bottom(h)
    foot=main.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rr=foot.add_run('INDUSTRIAL COMPUTING  •  ');rr.font.name='Liberation Sans';rr.font.size=Pt(7);rr.font.color.rgb=GRAY
    add_field(foot,'PAGE')
    # Reset page to 1
    sectPr=main._sectPr;pg=OxmlElement('w:pgNumType');pg.set(qn('w:start'),'1');pg.set(qn('w:fmt'),'decimal');sectPr.append(pg)
    # content parse
    lines=MANUSCRIPT.splitlines(); start=next(i for i,l in enumerate(lines) if l.startswith('# Preface'));lines=lines[start:]
    para=[]; code=[]; table=[]; in_code=False; curr_n=None; ended_chaps=set()
    def flush_para():
        nonlocal para
        if para:
            t=' '.join(x.strip() for x in para)
            if t.startswith('> '):
                p=doc.add_paragraph(style='Evidence Brief');fmt(p,t[2:]);shade(p,'EFF6F4')
            elif re.match(r'^[-*] ',t):
                p=doc.add_paragraph(style='Bullet');fmt(p,'• '+t[2:])
            else:add_body(doc,t)
            para=[]
    def flush_table():
        nonlocal table
        if not table:return
        rows=[list(map(str.strip,r.strip('|').split('|'))) for r in table]
        if len(rows)>1 and set(''.join(rows[1]))<=set('-: '):rows.pop(1)
        if rows:
            nc=max(map(len,rows));tbl=doc.add_table(rows=len(rows),cols=nc,style='Table Grid')
            for i,row in enumerate(rows):
                for j in range(nc):set_cell(tbl.cell(i,j),row[j] if j<len(row) else '',i==0)
        table=[]
    def flush_code():
        nonlocal code
        if code:
            lab=doc.add_paragraph(style='Listing Label');lab.add_run('CODE EXAMPLE  ·  in-text excerpt')
            for l in code:
                p=doc.add_paragraph(style='Source Code');p.add_run(l)
            code=[]
    def end_chapter():
        nonlocal curr_n
        if curr_n and curr_n not in ended_chaps:
            add_chapter_tail(doc,curr_n);ended_chaps.add(curr_n)
    for l in lines:
        if l.startswith('```'):
            flush_para();flush_table()
            if in_code:flush_code();in_code=False
            else:in_code=True
            continue
        if in_code:code.append(l);continue
        if l.startswith('|'):
            flush_para();table.append(l);continue
        if table:flush_table()
        if not l.strip():flush_para();continue
        if l.strip()=='---':flush_para();continue
        if l.startswith('# '):
            flush_para();end_chapter()
            h=l[2:].strip()
            if h.startswith('Preface'):
                add_label(doc,'PREFACE / WHY THIS BOOK EXISTS');add_heading(doc,h,1)
            elif h.startswith('Part ') or h=='Appendices':
                page_break(doc)
                add_label(doc,'INDUSTRIAL COMPUTING / FOUNDATIONS AND PRACTICE')
                p=doc.add_paragraph(style='Part Title');p.add_run(h)
                p=doc.add_paragraph();p.add_run('HISTORY  •  ARCHITECTURE  •  MEASUREMENT  •  CONTROL').italic=True
                doc.add_paragraph(' ')
            elif h.startswith('Chapter '):
                m=re.match(r'Chapter (\d+)\s*[—-]\s*(.*)',h)
                if m:
                    curr_n=int(m.group(1));page_break(doc)
                    add_label(doc,f'CHAPTER {curr_n:02d}  /  CORE READING')
                    p=doc.add_paragraph(style='Chapter Title');fmt(p,m.group(2))
                    q,keys=CHAP_SUM.get(curr_n,('Learn through evidence',''))
                    p=doc.add_paragraph(style='Subtitle Note');fmt(p,'**Guiding question:** '+q)
                    p=doc.add_paragraph(style='Evidence Brief');fmt(p,'**Key vocabulary:** '+keys)
            else:add_heading(doc,h,1)
        elif l.startswith('## '):flush_para();add_heading(doc,l[3:].strip(),2)
        elif l.startswith('### '):flush_para();add_heading(doc,l[4:].strip(),3)
        else:para.append(l)
    flush_para();flush_table();flush_code();end_chapter()
    # instructor keys and glossary, new appendix in main folio
    page_break(doc);add_label(doc,'APPENDIX F  /  INSTRUCTOR EDITION');add_heading(doc,'Answer key and common misconceptions',1)
    add_body(doc,'The following responses are instructional models, not evidence of a completed physical experiment. A correct conceptual answer does not replace a board measurement or a toolchain log. The teacher may accept technically equivalent explanations that account for all observed states and units.')
    for lab in LABS:
        page_break(doc)
        add_label(doc,f'INSTRUCTOR LAB {lab["id"]}  /  INSTRUCTION AND ASSESSMENT')
        add_heading(doc,f'Field laboratory {lab["id"]} — Teacher notes',2)
        for ptext in lab['answers'].split('\n\n'):add_body(doc,ptext)
        add_body(doc,'**Before sign-off:** '+lab['evidence'])
        add_heading(doc,'Before the class begins',3)
        for x in ('Establish a controlled starting condition and a safe power/wiring configuration.', 'Check the required toolchain or simulator in advance; retain the version and source files used.', 'Decide what measured record will count as evidence and what observation will trigger a stop.'):add_body(doc,'• '+x)
        add_heading(doc,'Ask rather than tell',3)
        for q in lab['questions']:add_body(doc,'• '+q)
        add_heading(doc,'Evidence to assess',3)
        add_body(doc,'Look for a numerical or state prediction before the test; direct observations instead of claims about intent; a separate limitation; and a clear next discriminating test.')
        add_heading(doc,'What changes for the next lesson?',3)
        add_body(doc,'Carry forward the actual measured constraints and unresolved problems. A successful record is one that another learner could reproduce; it need not have matched the initial prediction.')
    page_break(doc);add_label(doc,'APPENDIX G  /  REFERENCE');add_heading(doc,'Working glossary and chapter locator',1)
    terms=[('Addressing mode','Rule for locating operand data'),('Autoincrement','Update pointer after accessing pointed-to data'),('Bit mask','Selected bits changed or tested without altering neighbors'),('Control loop','Rules for observing a process and choosing actions'),('CRC','Check for corruption of transmitted bytes'),('DCO','Digitally controlled oscillator in the MSP430'),('Direct memory access','Peripheral data transfer without CPU handling every word'),('Hysteresis','Different thresholds for turning ON and OFF'),('Interrupt','Event that diverts the current instruction sequence'),('Jitter','Variation of event timing relative to its nominal schedule'),('Memory-mapped I/O','Hardware control registers represented in an address space'),('PIO','Programmable I/O state machines of RP2040'),('Program counter','Register identifying instruction sequencing'),('RSX-11M','DEC real-time multitasking operating system'),('RT-11','DEC real-time operating system for the PDP-11'),('Scratchpad','DS18B20 register bank containing temperature and status'),('Timebase','Clock reference used to measure elapsed time'),('Traceability','Recorded chain from a claim back to raw data and standards'),('UNIBUS','DEC modular bus architecture'),('UART','Asynchronous serial transmitter/receiver'),('Volatile','C qualifier for objects whose value may change outside ordinary program flow'),('1-Wire','Single-data-wire timed bus protocol')]
    for k,v in terms:
        p=doc.add_paragraph(style='Normal');r=p.add_run(k+'  —  ');r.bold=True;fmt(p,v)
    add_heading(doc,'Cross-reference map',2)
    add_body(doc,'PDP-11 hardware and industrial control: Chapters 1–3. Registers and addressing modes: Chapters 2, 4. MSP430 instruction and register effects: Chapters 4–6. Time, timer, interrupt: Chapters 5, 7. Communication and sensor protocol: Chapters 8–10. Sensor validity and safety decisions: Chapters 10–11. Evidence and publication: Chapter 12 and Appendices B–C. Teacher support: Chapters 13–14 and Appendix F.')
    page_break(doc);add_label(doc,'APPENDIX H  /  REFERENCE TABLES');add_heading(doc,'Engineering reference atlas',1)
    add_body(doc,'The following tables make an operational checklist; they do not replace the authoritative datasheet, wiring inspection, or the timing specifications of a real sensor.')
    for title,items in REFERENCE_PAGES:
        page_break(doc);add_label(doc,'REFERENCE / FIELD USE');add_heading(doc,title,1)
        for k,v in items:
            p=doc.add_paragraph(style='Normal');fmt(p,'**'+k+'**  —  '+v)
        add_heading(doc,'Record your local verification',2)
        for labline in ('Board / instrument revision:','Source or datasheet and exact page:','Bench observation and limitation:'):
            add_body(doc,labline+' _______________________________________________')
    # Final publication QA section: an editorial appendix, not fabricated bench evidence.
    page_break(doc)
    add_label(doc,'TECHNICAL VALIDATION / FINAL EDITION')
    add_heading(doc,'What has been verified — and what has not',1)
    add_body(doc,'The final package separates a documented historical claim, an algorithm verified on a host, a target firmware candidate, and a physical experiment. These categories have different evidentiary value. A tested C function for temperature decoding does not establish correct 1-Wire waveforms or a working external sensor. A correctly printed PDF does not establish correct board wiring.')
    add_heading(doc,'Host software verification',2)
    add_body(doc,'From the top-level archive directory, run `tests/run_host_tests.sh` in a shell with Python 3 and a C11 compiler. The script checks the CSV measurement parser, resolution-aware DS18B20 arithmetic, CRC error handling, a hysteresis state machine, and a small synthetic supervisor demonstration. The captured results are recorded under `validation/HOST_TEST_RESULTS.txt`. These tests require no MSP430 and do not involve sensor acquisition.')
    add_heading(doc,'Target hardware verification gates',2)
    for item in [
      'Gate 1 — Confirm board orientation, 3.3 V supply, GND, Spy-Bi-Wire reset and test connections, and isolation of the LaunchPad debug interface.',
      'Gate 2 — Target-compile the timer assembly and C sample, preserve the compiler command/log/map file, and flash with a verified erase-main-only method.',
      'Gate 3 — Measure five separate 1 kHz gates with live meter status and the generator disabled; preserve raw frequency, count and elapsed time.',
      'Gate 4 — Confirm UART levels and baud, then capture protocol traces; distinguish software command from pin waveform.',
      'Gate 5 — Validate DQ open-drain release, 1-Wire reset/presence, write slots, and read sampling with a timing-capable instrument.',
      'Gate 6 — Demonstrate one freshly completed DS18B20 conversion, full nine-byte scratchpad, CRC, sensor identity, and independent temperature comparison.',
      'Gate 7 — Operate the educational LED supervisor under valid, stale, missing, and erroneous data; document reset and safe-state behavior.'
    ]:
      p=doc.add_paragraph(style='Procedure');fmt(p,item)
    add_heading(doc,'Hardware experiment record',2)
    for line in ['Date/time and operator: _____________________________________________',
                 'Board revision and firmware hash: _____________________________________',
                 'Compiler version and command: _______________________________________',
                 'Measurement firmware and live settings: ______________________________',
                 'Raw data file and checksum: ________________________________________',
                 'Observed failure or uncertainty: _____________________________________']:
        p=doc.add_paragraph(style='Worksheet');p.add_run(line)
    add_body(doc,'A completed log is the prerequisite for changing a target firmware status from CANDIDATE to BENCH-VERIFIED. This edition makes no such upgrade without the required observations.')
    props=doc.core_properties;props.title='From the PDP-11 to the MSP430';props.subject='Industrial computing, embedded systems, measurement, and laboratory curriculum';props.author='Independent educational manuscript';props.keywords='PDP-11, MSP430, RP2040, industrial automation, 1-Wire, DS18B20'
    return doc

# first pass
name='From_the_PDP11_to_the_MSP430_FINAL_Textbook'
doc=make_doc();outdoc=OUT/(name+'.docx');doc.save(outdoc)
print('WROTE',outdoc,'bytes',outdoc.stat().st_size)

# Publisher's pagination pass: use rendered page number shown in the book
pdfdir=OUT/'_pagination';pdfdir.mkdir(exist_ok=True)
def convert_to_pdf(docx):
    subprocess.run(['libreoffice','-env:UserInstallation='+((Path(tempfile.gettempdir())/'lo_pdp_book_pagination').as_uri()),'--headless','--convert-to','pdf','--outdir',str(pdfdir),str(docx)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=200)
    return pdfdir/(docx.stem+'.pdf')

firstpdf=convert_to_pdf(outdoc)
pages=fitz.open(firstpdf)
bookpages=[]
for idx,page in enumerate(pages):
    raw=page.get_text()
    txt=' '.join(raw.split())
    bookpages.append((idx+1,txt,raw))

def findpage(phrase, earliest=6):
    needle=' '.join(phrase.split()).lower()
    for num,txt,raw in bookpages:
        if num>=earliest and needle in txt.lower():return num-5
    return None

toc_map={}
intro_page=findpage('Introduction — An engineering history that can be measured')
if intro_page:toc_map['Introduction — An engineering history that can be measured']=intro_page
parts=['Part I — The industrial computer and its architecture','Part II — The MSP430 becomes a physical experiment','Part III — Teacher’s and operator’s companion']
for i,p in enumerate(parts,1):
    for num,txt,raw in bookpages:
        if num>5 and f'Part {"I"*i}' in txt and 'INDUSTRIAL COMPUTING / FOUNDATIONS' in txt:
            toc_map[p]=num-5;break
for n in range(1,15):
    for line in MANUSCRIPT.splitlines():
        if line.startswith(f'# Chapter {n} —'):
            label=line[2:]
            kicker=f'CHAPTER {n:02d} / CORE READING'
            for num,txt,raw in bookpages:
                if kicker in txt:
                    toc_map[label]=num-5;break
            break
ap=None
for num,txt,raw in bookpages:
    if num>5 and 'Part III' in txt and 'Teacher' in txt:pass
    if num>5 and 'INDUSTRIAL COMPUTING / FOUNDATIONS' in txt and 'Appendices' in txt:ap=num-5;break
if ap:toc_map['Appendices']=ap
for c,title in [('A','Register comparison'),('B','Safe bench'),('C','CAP worksheet'),('D','References and provenance'),('E','Source inventory')]:
    term=f'Appendix {c} —'
    for num,txt,raw in bookpages:
        if num>5 and term in txt:
            toc_map[f'Appendix {c} — {title}']=num-5;break
for c,phrase,title in [('F','Answer key and common misconceptions','Instructor answer key'),('G','Working glossary and chapter locator','Glossary and chapter locator'),('H','Engineering reference atlas','Engineering reference atlas')]:
    page=findpage(phrase)
    if page:toc_map[f'Appendix {c} — {title}']=page
# Correct roman numeral part mapping, avoid part I matching II and III
for i,p in enumerate(parts,1):
    marker=['Part I —','Part II —','Part III —'][i-1]
    for num,txt,raw in bookpages:
        if num>5 and 'INDUSTRIAL COMPUTING / FOUNDATIONS' in txt and marker in txt:
            toc_map[p]=num-5;break
print('pagination toc:',toc_map)

doc=make_doc(toc_map)
doc.save(outdoc)
finalpdf=convert_to_pdf(outdoc)
final=OUT/(name+'.pdf');shutil.copy2(finalpdf,final)
print('FINAL PDF',len(fitz.open(final)),'pages')
# Full running text (appendices and problem sets) as a searchable export
pdf=fitz.open(final)
with open(OUT/'READING_TEXT.txt','w',encoding='utf-8') as f:
    for n,p in enumerate(pdf,1):f.write(f'\n\n=== PRINTED PAGE {n} ===\n'+p.get_text())
# quick programmatic QA
texts=[p.get_text() for p in pdf]
assert 110<=len(pdf)<=240
for n in range(1,15):assert any(f'CHAPTER {n:02d}' in s for s in texts)
assert sum('ADVANCED FIELD INVESTIGATION' in s for s in texts)>=12
assert sum('FIELD RECORD' in s for s in texts)>=12
assert sum('INSTRUCTOR LAB' in s for s in texts)>=12
assert all(v is not None for v in toc_map.values()) and all('—\n' not in pdf[4].get_text().split('Contents',1)[1].split('Appendix H')[0][-170:] for _ in [0])
(OUT/'BUILD_NOTES.txt').write_text(
    'Final editorial textbook edition: 31 October 2026\n'
    + 'PDF pages: '+str(len(pdf))+'\n'
    + 'Host validation: see validation/HOST_TEST_RESULTS.txt.\n'
    + 'MSP430 target compiler unavailable in current environment; no target images asserted.\n'
    + 'Physical board, 1-Wire waveform, GPS calibration: NOT VERIFIED in this edition.\n'
    + 'Source: CORE_MANUSCRIPT.md + editorial/final_expansions.py, generated with editorial/build_final_book.py.\n'
    + 'Citations: see Appendix D and editorial/REFERENCE_AUDIT.md.\n',encoding='utf-8')
print('FINAL BOOK',len(pdf),'PAGES')
