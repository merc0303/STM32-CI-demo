cmake_minimum_required(VERSION 3.22)
project(stm32-ci-demo C)

option(BUILD_TESTS "Build host unit tests" OFF)
option(COVERAGE "Instrument host tests for gcov" OFF)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Host-only coverage instrumentation; must precede target creation.
if(COVERAGE AND NOT CMAKE_CROSSCOMPILING)
  add_compile_options(--coverage -O0)
  add_link_options(--coverage)
endif()

# Portable application logic: no hardware access, builds for host and target.
add_library(app STATIC src/app/app.c src/app/crc32.c)
target_include_directories(app PUBLIC src/app src/hal)
target_compile_options(app PRIVATE -Wall -Wextra -Wconversion -Wshadow -Werror)

if(CMAKE_CROSSCOMPILING)
  # ---- Target firmware (STM32F407, Cortex-M4) ----
  add_executable(firmware
    src/main.c
    src/port/stm32f4/startup_stm32f407.c
    src/port/stm32f4/uart_stm32f4.c)
  set_target_properties(firmware PROPERTIES SUFFIX ".elf")

  target_compile_options(app PRIVATE ${MCU_FLAGS} -Os -g3 -ffunction-sections -fdata-sections)
  target_compile_options(firmware PRIVATE ${MCU_FLAGS} -Os -g3 -ffunction-sections -fdata-sections
    -Wall -Wextra -Wconversion -Wshadow -Werror)
  target_link_libraries(firmware PRIVATE app)
  target_link_options(firmware PRIVATE ${MCU_FLAGS}
    -T${CMAKE_SOURCE_DIR}/src/port/stm32f4/STM32F407VG.ld
    -nostartfiles --specs=nano.specs --specs=nosys.specs
    -Wl,--gc-sections -Wl,-Map=firmware.map)
  add_custom_command(TARGET firmware POST_BUILD
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:firmware>)
else()
  if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
  endif()
endif()
