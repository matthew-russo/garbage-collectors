#ifndef _UTILS_HEAP_H
#define _UTILS_HEAP_H

#include <stdint.h>

#include "object.h"

struct reference
{
    uintptr_t address;
    uint32_t size;
};

struct heap
{
    uint8_t * bitmap;
    uintptr_t arena;
    uint32_t  size;
};

struct heap * heap_init(uint32_t size); // TODO -> alignment
struct object * heap_load(struct heap * h, struct reference ref);
struct reference heap_store(struct heap * h, uintptr_t address, struct object * obj);
uintptr_t heap_alloc(int size);
void heap_free(struct reference to_free);

// TODO -> some type of iterator

#endif
