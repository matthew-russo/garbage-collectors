#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "object.h"
#include "heap.h"

void mark_worklist(worklist)
{
    while (!queue_is_empty(worklist))
    {
        ref = queue_dequeue(worklist);
        obj = heap_load(heap, ref);
        // iterate object fields
        // foreach f_name, f_ref in obj.fields.items():
            if (f_ref == NULL)
            {
                continue;
            }

            child = heap_load(heap, f_ref);
            if (child == NULL)
            {
                printf("ACTIVE REFERENCE LEADING TO DEAD MEMORY. THIS SHOULD BE IMPOSSIBLE");
                exit(1);
            }

            if (!child->is_marked)
            {
                child->is_marked = true;
                queue_enqueue(worklist, f_ref);
            }
    }
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
    uintptr_t curr_ptr = heap->start;

    while (curr_ptr < heap->end)
    {
        if (mem_allocated(curr_ptr))
        {
            struct object * obj = (struct object *)(void *) curr_ptr;
            uint32_t size = obj->header.size;
            if (obj->header.is_marked)
            {
                struct reference ref = {
                    .address = curr_ptr;
                    .size = size;
                };
                heap_free(ref);
            }

            curr_ptr += size;
        }
        else
        {
            curr_ptr++;
        }
    }
}

void collect(roots)
{
    mark_from_roots(roots);
    sweep();
}

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
