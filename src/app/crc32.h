#ifndef CRC32_H
#define CRC32_H

#include <stddef.h>
#include <stdint.h>

/* CRC-32 (IEEE 802.3, reflected, poly 0xEDB88320). Check value for
 * "123456789" is 0xCBF43926. */
uint32_t crc32_compute(const uint8_t *data, size_t len);

#endif
