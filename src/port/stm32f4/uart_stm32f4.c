/* Minimal register-level USART2 driver (PA2 = TX, AF7) for STM32F407.
 * Uses the reset-default 16 MHz HSI clock, 115200 baud.                  */
#include <stdint.h>

#include "uart.h"

#define REG32(addr) (*(volatile uint32_t *)(addr))

#define RCC_BASE      0x40023800u
#define RCC_AHB1ENR   REG32(RCC_BASE + 0x30u)
#define RCC_APB1ENR   REG32(RCC_BASE + 0x40u)

#define GPIOA_BASE    0x40020000u
#define GPIOA_MODER   REG32(GPIOA_BASE + 0x00u)
#define GPIOA_AFRL    REG32(GPIOA_BASE + 0x20u)

#define USART2_BASE   0x40004400u
#define USART2_SR     REG32(USART2_BASE + 0x00u)
#define USART2_DR     REG32(USART2_BASE + 0x04u)
#define USART2_BRR    REG32(USART2_BASE + 0x08u)
#define USART2_CR1    REG32(USART2_BASE + 0x0Cu)

#define SR_TXE        (1u << 7)
#define CR1_TE        (1u << 3)
#define CR1_UE        (1u << 13)

void uart_init(void)
{
    RCC_AHB1ENR |= (1u << 0);                   /* GPIOA clock */
    RCC_APB1ENR |= (1u << 17);                  /* USART2 clock */

    GPIOA_MODER = (GPIOA_MODER & ~(3u << 4)) | (2u << 4);   /* PA2: AF */
    GPIOA_AFRL  = (GPIOA_AFRL  & ~(0xFu << 8)) | (7u << 8); /* AF7 */

    USART2_BRR = 0x8Bu;                         /* 16 MHz / 115200 */
    USART2_CR1 = CR1_UE | CR1_TE;
}

void uart_write(const char *s)
{
    while (*s != '\0') {
        while ((USART2_SR & SR_TXE) == 0u) {
        }
        USART2_DR = (uint32_t)(uint8_t)*s;
        s++;
    }
}
