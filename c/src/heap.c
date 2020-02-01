#include "object.h"

struct object * heap_load(struct heap * h, struct reference ref)
{
    uintptr_t actual_address = h->arena + ref.size;
    struct object ** obj_ptr = (struct object **) actual_address;
    return *obj_ptr;
}

struct reference heap_store(struct heap * h, uintptr_t address, struct object * obj)
{
    uintptr_t actual_address = h->arena + address;
    memcpy((void *) actual_address, obj, sizeof(struct object));
    struct reference ref = {
        .address = actual_address,
        .size = sizeof(struct object),
    };
    return ref;
}


