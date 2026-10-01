#ifndef APP_H
#define APP_H

#include <stdbool.h>

/* Boot-time self-test: CRC-32 engine against a known-answer vector. */
bool app_selftest(void);

/* Prints boot banner and self-test verdict on the UART. */
void app_run(void);

#endif
