#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "object.h"
#include "heap.h"

struct heap * heap_init(uint32_t size)
{
    struct heap * heap = malloc(sizeof(struct heap));
    heap->size = size;
    heap->bitmap = malloc(sizeof(uint8_t) * size);
    for (int i = 0 ; i < size; i++)
    {
        heap->bitmap[i] = 0;
    }
    heap->arena = (uintptr_t)malloc(sizeof(struct object) * size);
    return heap;
}

struct object * heap_load(struct heap * heap, struct reference ref)
{
    uintptr_t actual_address = heap->arena + ref.size;
    struct object ** obj_ptr = (struct object **) actual_address;
    return *obj_ptr;
}

struct reference heap_store(struct heap * heap, uintptr_t address, struct object * obj)
{
    uintptr_t actual_address = heap->arena + address;
    memcpy((void *) actual_address, obj, sizeof(struct object));
    struct reference ref = {
        .address = actual_address,
        .size = sizeof(struct object),
    };
    return ref;
}

bool heap_mem_allocated(struct heap * heap, uintptr_t address)
{
    uintptr_t offset = address - heap->arena;
    uintptr_t index = offset / sizeof(struct object);
    return heap->bitmap[index] != 0;
}

uintptr_t heap_alloc(struct heap * heap, uint32_t size)
{
    for (int i = 0; i < heap->size; i++)
    {
        if (heap->bitmap[i] == 0)
        {
            heap->bitmap[i] = 1;
            uintptr_t offset = (uintptr_t) (sizeof(struct object) * i);
            return heap->arena + offset;
        }
    }

    return 0;
}

void heap_free(struct heap * heap, struct object * to_free)
{
    printf("unimplemented heap_free");
    exit(1);
}

struct heap_iterator heap_iterator_init(struct heap * heap)
{
    struct object * first_obj;
    uint32_t bitmap_index;
    for (bitmap_index = 0; bitmap_index < heap->size; bitmap_index++)
    {
        if (heap->bitmap[bitmap_index] != 0)
        {
            uintptr_t offset = (uintptr_t) (sizeof(struct object) * bitmap_index);
            uintptr_t actual_address =  heap->arena + offset;
            struct object ** obj_ptr = (struct object **) actual_address;
            first_obj = *obj_ptr;
            break;
        }
    }

    struct heap_iterator iter;
    iter.heap = heap;
    iter.current = first_obj;
    iter.curr_bitmap_index = bitmap_index;
    return iter;
}

void heap_iter_restart(struct heap_iterator * iter)
{
    struct object * first_obj;
    uint32_t bitmap_index;
    for (bitmap_index = 0; bitmap_index < iter->heap->size; bitmap_index++)
    {
        if (iter->heap->bitmap[bitmap_index] != 0)
        {
            uintptr_t offset = (uintptr_t) (sizeof(struct object) * bitmap_index);
            uintptr_t actual_address =  iter->heap->arena + offset;
            struct object ** obj_ptr = (struct object **) actual_address;
            first_obj = *obj_ptr;
            break;
        }
    }
    iter->current = first_obj;
    iter->curr_bitmap_index = bitmap_index;
}

void heap_iter_next(struct heap_iterator * iter)
{
    iter->curr_bitmap_index = iter->curr_bitmap_index + 1;
    for (uint32_t i = iter->curr_bitmap_index; i < iter->heap->size; i++)
    {
        if (iter->heap->bitmap[i] != 0)
        {
            struct reference ref;
            uintptr_t offset = iter->heap->arena + ((uintptr_t) i * sizeof(struct object));
            ref.address = offset;
            ref.size = sizeof(struct object);
            iter->current = heap_load(iter->heap, ref);
            return;
        } 
    }
}

bool heap_iter_is_done(struct heap_iterator * iter)
{
    return iter->curr_bitmap_index >= (iter->heap->size - 1);
}

struct object * heap_iter_current_object(struct heap_iterator * iter)
{
    return iter->current;
}



