#include "app.h"
#include "uart.h"

int main(void)
{
    uart_init();
    app_run();
    for (;;) {
        /* idle; FreeRTOS tasks replace this loop in a later step */
    }
}
