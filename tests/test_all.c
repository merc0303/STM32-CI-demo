#include <string.h>

#include "app.h"
#include "crc32.h"
#include "unity.h"
#include "uart_fake.h"

void setUp(void) { uart_fake_reset(); }
void tearDown(void) {}

static void test_crc32_known_answer(void)
{
    const char *v = "123456789";
    TEST_ASSERT_EQUAL_HEX32(0xCBF43926u,
                            crc32_compute((const uint8_t *)v, strlen(v)));
}

static void test_crc32_empty_input(void)
{
    TEST_ASSERT_EQUAL_HEX32(0x00000000u, crc32_compute((const uint8_t *)"", 0u));
}

static void test_selftest_passes(void)
{
    TEST_ASSERT_TRUE(app_selftest());
}

static void test_app_run_prints_banner_and_verdict(void)
{
    app_run();
    TEST_ASSERT_EQUAL_STRING("BOOT OK\r\nSELFTEST PASS\r\n", uart_fake_output());
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_crc32_known_answer);
    RUN_TEST(test_crc32_empty_input);
    RUN_TEST(test_selftest_passes);
    RUN_TEST(test_app_run_prints_banner_and_verdict);
    return UNITY_END();
}
