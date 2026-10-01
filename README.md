# stm32-ci-demo

Hardware-free STM32F407 firmware with a CI pipeline: containerised cross-build,
static analysis, host unit tests with a coverage gate, and a Renode boot
simulation on every push.

## Build and test without hardware

    docker build -t stm32-ci-toolchain .
    docker run --rm -it -v "$PWD":/work stm32-ci-toolchain bash

    # host unit tests
    cmake -S . -B build/host -G Ninja -DBUILD_TESTS=ON && cmake --build build/host
    ctest --test-dir build/host --output-on-failure

    # firmware
    cmake -S . -B build/fw -G Ninja -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi.cmake
    cmake --build build/fw

    # simulation (needs Renode installed on the host)
    renode-test sim/boot.robot

## Layout

    src/app/            portable logic (CRC-32, boot self-test), no hardware access
    src/hal/            interface the app depends on (uart.h)
    src/port/stm32f4/   startup, linker script, register-level UART driver
    tests/              Unity tests + UART test double
    sim/                Renode platform script and Robot Framework test

## Limits of the simulation

Renode checks functional behaviour (boot, peripherals, UART output), not exact
timing, clock tree configuration, or electrical behaviour.

## Roadmap

SBOM (CycloneDX), vulnerability scan, signed releases with provenance,
clang-tidy and MISRA checks, FreeRTOS tasks, threat model.
