#ifndef UART_H
#define UART_H

/* Hardware abstraction boundary: the application only sees this interface.
 * Target implementation: src/port/stm32f4/uart_stm32f4.c
 * Host test double:      tests/uart_fake.c                                  */

void uart_init(void);
void uart_write(const char *s);

#endif
