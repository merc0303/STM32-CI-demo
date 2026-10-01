#include <string.h>

#include "uart.h"
#include "uart_fake.h"

static char buf[256];

void uart_init(void) { uart_fake_reset(); }

void uart_write(const char *s)
{
    strncat(buf, s, sizeof(buf) - strlen(buf) - 1u);
}

void uart_fake_reset(void) { buf[0] = '\0'; }
const char *uart_fake_output(void) { return buf; }
