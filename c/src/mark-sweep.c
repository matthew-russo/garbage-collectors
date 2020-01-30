#include <stdio.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

struct object
{
    bool marked;
    char * id;
    struct map * fields; // val is char *
};

struct reference
{
    uintptr_t address;
    uint32_t size;
};

struct heap
{
    uint8_t * bitmap;
    uintptr_t arena;
};

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

uintptr_t heap_alloc(int size)
{

}

void heap_free(struct reference to_free)
{

}

//

void mark_worklist(worklist)
{
    
}

void mark_from_roots(roots)
{
    size_t roots_length = sizeof(roots) / sizeof(roots[0]);
    for (int i = 0 ; i < roots_length; i++)
    {
        struct object * obj = heap_load(heap, roots[i]);
        if (obj != NULL && !obj->is_marked)
        {
            obj->is_marked = true;
            worklist[worklist_ptr++] = ref;
            mark_worklist(worklist);
        }
    }
}

void sweep()
{

}

void collect(roots)
{
    mark_from_roots(roots);
    sweep();
}

//

int main()
{
    struct heap * heap = heap_init(size, alignment);
    struct runtime * runtime = runtime_init(heap);

    struct object r1 = {
        .marked = false,
        .id = "r1",
        .fields = r1_fields,
    };
    runtime->new(r1);

    struct object a1 = {
        .marked = false,
        .id = "a1",
        .fields = a1_fields,
    };
    runtime->new(a1);

    struct object a2 = {
        .marked = false,
        .id = "a2",
        .fields = a2_fields,
    };
    runtime->new(a2);

    struct object b1 = {
        .marked = false,
        .id = "b1",
        .fields = b1_fields,
    };
    runtime->new(b1);

    struct object b2 = {
        .marked = false,
        .id = "b2",
        .fields = b2_fields,
    };
    runtime->new(b2);

    struct object c = {
        .marked = false,
        .id = "c",
        .fields = c_fields,
    };
    runtime->new(c);

    free(runtime);
    free(heap);
}
