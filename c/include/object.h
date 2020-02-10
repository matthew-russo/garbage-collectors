#ifndef _UTILS_OBJECT_H
#define _UTILS_OBJECT_H

#include <stdbool.h>
#include <stdint.h>

struct object_header
{
    bool is_marked;
    uintptr_t forwarding_address;
    uint32_t rc;
    uint32_t size;
};

struct object
{
    struct object_header header;
    char * id;
    struct map * fields; // val is char *
};

#endif
