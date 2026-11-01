# Optional edu430 macro comparison

Import this CCS project and build Debug. It is an additional Chapter 6 exercise comparing `SET_BITS`, `CLEAR_BITS` and `BITS_LOW` against `CCS_GPIO_Starter`'s explicit register operations. The example deliberately uses P2.0 for the switch and P1.0 for the LED, matching the book's example, without using the header's P1.3 button alias. This project contains a copy of the prior learning-labs `edu430.h`, not a newly identified `msp430_edu.h`.

The header also defines board helpers and LED aliases: LED_B is P1.6, which is the timer output in this course; the header button is P1.3, unlike the course's P2.0 example. Do not call board-wide initializers blindly when combining experiments. Its `board_clock_1mhz` checks CALBC1 but not CALDCO; the textbook candidates check both. The original header is kept unchanged for provenance. CCS build succeeded; physical testing has not been performed.
