#ifndef _UTILS_HEAP_H
#define _UTILS_HEAP_H

#include <stdint.h>
#include <stdbool.h>

#include "object.h"

struct reference
{
    uintptr_t address;
    uint32_t size;
};

struct heap
{
    uint8_t * bitmap;
    void* arena;
    uint32_t  size;
};

struct heap * heap_init(uint32_t size); // TODO -> alignment
struct object * heap_load(struct heap * h, struct reference ref);
struct reference heap_store(struct heap * h, uintptr_t address, struct object * obj);
bool heap_mem_allocated(struct heap * h, uintptr_t address);
uintptr_t heap_alloc(struct heap * h, uint32_t size);
void heap_free(struct heap * h, struct object * to_free);
void heap_clear(struct heap * h);

struct heap_iterator
{
    struct heap * heap;
    struct object * current;
    uintptr_t curr_bitmap_index;
};

struct heap_iterator heap_iterator_init(struct heap * heap);
void heap_iter_restart(struct heap_iterator *);
void heap_iter_next(struct heap_iterator *);
bool heap_iter_is_done(struct heap_iterator *);
struct object * heap_iter_current_object(struct heap_iterator *);

#endif
