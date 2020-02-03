#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "object.h"
#include "heap.h"
#include "map.h"
#include "queue.h"

#define DEFAULT_HEAP_SIZE 100

struct root {
    struct object * obj;
    struct root * next;
};

struct runtime
{
    struct heap * heap;
    struct root * roots;
};

struct runtime * runtime_init(struct heap * heap)
{
    struct runtime * runtime = malloc(sizeof(struct runtime));
    runtime->heap = heap;
    return runtime;
};

void runtime_instantiate(struct runtime * runtime,struct object * object)
{
    uintptr_t addr = heap_alloc(runtime->heap, object->header.size);
    heap_store(runtime->heap, addr, object);
}

void runtime_add_root(struct runtime * runtime, struct object object)
{
    printf("unimplemented runtime_add_root");
    exit(1);
}

void runtime_mark_worklist(struct runtime * runtime, struct queue * worklist)
{
    while (!queue_is_empty(worklist))
    {
        struct object * obj = (struct object *)queue_dequeue(worklist);
        struct map_iterator obj_field_iter = map_iter(obj->fields);
        for (struct reference * f_ref = (struct reference *)map_iter_current_value(&obj_field_iter);
            !map_iter_is_done(&obj_field_iter);
            map_iter_next(&obj_field_iter))
        {
            if (f_ref == NULL)
            {
                continue;
            }

            struct object * child = heap_load(runtime->heap, *f_ref);
            if (child == NULL)
            {
                printf("ACTIVE REFERENCE LEADING TO DEAD MEMORY. THIS SHOULD BE IMPOSSIBLE");
                exit(1);
            }

            if (!child->header.is_marked)
            {
                child->header.is_marked = true;
                queue_enqueue(worklist, child);
            }
        }
    }
}

void runtime_mark_from_roots(struct runtime * runtime)
{
    struct queue * worklist = queue_init(DEFAULT_HEAP_SIZE);
 
    struct root * current_root = runtime->roots;
    while (current_root != NULL)
    {
        struct object * obj = current_root->obj;
        current_root = current_root->next;
        if (obj != NULL && !obj->header.is_marked)
        {
            obj->header.is_marked = true;
            queue_enqueue(worklist, obj);
            runtime_mark_worklist(runtime, worklist);
        }
    }
}

void runtime_sweep(struct runtime * runtime)
{
    struct heap_iterator heap_iter = heap_iterator_init(runtime->heap);

    for (struct object * obj = heap_iter_current_object(&heap_iter);
        !heap_iter_is_done(&heap_iter);
        heap_iter_next(&heap_iter))
    {
        uint32_t size = obj->header.size;
        if (obj->header.is_marked)
        {
            heap_free(runtime->heap, obj);
        }
    }
}

void runtime_collect(runtime)
{
    runtime_mark_from_roots(runtime);
    runtime_sweep(runtime);
}

int main()
{
    struct heap * heap = heap_init(DEFAULT_HEAP_SIZE /*, alignment */);
    struct runtime * runtime = runtime_init(heap);

    struct map * r1_fields = map_init(2);
    map_insert(r1_fields, "a1", NULL);
    map_insert(r1_fields, "a2", NULL);
    struct object r1 = {
        .header = {
            .is_marked = false,
            .size = sizeof(struct object),
        },
        .id = "r1",
        .fields = r1_fields,
    };
    runtime_instantiate(runtime, &r1);
    printf("intantiated r1");

    struct map * a1_fields = map_init(2);
    map_insert(a1_fields, "b1", NULL);
    map_insert(a1_fields, "b2", NULL);
    struct object a1 = {
        .header = {
            .is_marked = false,
            .size = sizeof(struct object),
        },
        .id = "a1",
        .fields = a1_fields,
    };
    runtime_instantiate(runtime, &a1);
    printf("intantiated a1");

    struct object a2 = {
        .header = {
            .is_marked = false,
            .size = sizeof(struct object),
        },
        .id = "a2",
        .fields = map_init(0),
    };
    runtime_instantiate(runtime, &a2);
    printf("intantiated a2");

    struct object b1 = {
        .header = {
            .is_marked = false,
            .size = sizeof(struct object),
        },
        .id = "b1",
        .fields = map_init(0),
    };
    runtime_instantiate(runtime, &b1);
    printf("intantiated b1");

    struct object b2 = {
        .header = {
            .is_marked = false,
            .size = sizeof(struct object),
        },
        .id = "b2",
        .fields = map_init(0),
    };
    runtime_instantiate(runtime, &b2);
    printf("intantiated b2");

    struct object c = {
        .header = {
            .is_marked = false,
            .size = sizeof(struct object),
        },
        .id = "c",
        .fields = map_init(0),
    };
    runtime_instantiate(runtime, &c);
    printf("intantiated c");

    runtime_add_root(runtime, r1);
    printf("added root r1");
    runtime_collect(runtime);
    printf("rutime collected");

    free(runtime);
    free(heap);
}
