#include "app.h"

#include <string.h>

#include "crc32.h"
#include "uart.h"

#define SELFTEST_VECTOR   "123456789"
#define SELFTEST_EXPECTED 0xCBF43926u

bool app_selftest(void)
{
    const uint32_t crc = crc32_compute((const uint8_t *)SELFTEST_VECTOR,
                                       strlen(SELFTEST_VECTOR));
    return crc == SELFTEST_EXPECTED;
}

void app_run(void)
{
    uart_write("BOOT OK\r\n");
    uart_write(app_selftest() ? "SELFTEST PASS\r\n" : "SELFTEST FAIL\r\n");
}
