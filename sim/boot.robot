*** Settings ***
Suite Setup       Setup
Suite Teardown    Teardown
Test Setup        Reset Emulation
Test Teardown     Test Teardown
Resource          ${RENODEKEYWORDS}

*** Variables ***
${ELF}            ${CURDIR}/../build/fw/firmware.elf

*** Keywords ***
Prepare Machine
    Execute Command           $bin=@${ELF}
    Execute Command           include @${CURDIR}/stm32f4.resc
    Create Terminal Tester    sysbus.usart2

*** Test Cases ***
Should Boot And Pass Selftest
    Prepare Machine
    Start Emulation
    Wait For Line On Uart     BOOT OK         timeout=5
    Wait For Line On Uart     SELFTEST PASS   timeout=5
