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
    struct reference * ref;
    struct root * next;
};

struct root * root_init(struct reference * ref)
{
    struct root * root = malloc(sizeof(struct root));
    root->ref = ref;
    root->next = NULL;
    return root;
}

struct runtime
{
    struct heap * heap;
    struct root * roots;
    struct map * env;
};

struct runtime * runtime_init(struct heap * heap)
{
    struct runtime * runtime = malloc(sizeof(struct runtime));
    runtime->heap = heap;
    runtime->roots = NULL;
    runtime->env = map_init(DEFAULT_HEAP_SIZE);
    return runtime;
};

void runtime_instantiate(struct runtime * runtime, struct object * object)
{
    uintptr_t addr = heap_alloc(runtime->heap, object->header.size);
    
    printf("allocating obj %s at addr: %lu\n", object->id, addr);

    heap_store(runtime->heap, addr, object);

    struct reference * ref = malloc(sizeof(struct reference));
    ref->address = addr;
    ref->size = sizeof(struct object);
    map_insert(runtime->env, object->id, ref);
}

void runtime_add_root(struct runtime * runtime, char * id)
{
    struct reference * ref = (struct reference *)map_get(runtime->env, id);

    printf("referece for id: %s is at addr: %lu\n", id, ref->address);

    if (runtime->roots == NULL)
    {
        runtime->roots = root_init(ref);
        return;
    }

    struct root * current = runtime->roots;
    while (current->next != NULL)
    {
        current = current->next;
    }

    current->next = root_init(ref);
}

void runtime_assign_field(struct runtime * runtime, char * src_id, char * src_f_name, char * dst_id)
{
    struct reference * src_ref = (struct reference *)map_get(runtime->env, src_id);
    struct object * src_obj = heap_load(runtime->heap, *src_ref);
    struct reference * dst_ref = (struct reference *)map_get(runtime->env, dst_id);
    map_insert(src_obj->fields, src_f_name, dst_ref);
    printf("set field %s of obj %s at %p to reference of %s\n", src_f_name, src_id, src_obj, dst_id);
}

void runtime_mark_worklist(struct runtime * runtime, struct queue * worklist)
{
    printf("marking worklist \n");
    fflush(stdout);
    while (!queue_is_empty(worklist))
    {
        struct object * obj = (struct object *)queue_dequeue(worklist);
        for (struct map_iterator obj_field_iter = map_iter(obj->fields);
            !map_iter_is_done(&obj_field_iter);
            map_iter_next(&obj_field_iter))
        {
            struct map_node * f_node = map_iter_current_node(&obj_field_iter);

            if (f_node->value == NULL)
            {
                printf("field: %s of obj: %s at %p is null, skipping\n", f_node->key, obj->id, obj);
                continue;
            }

            struct reference * f_ref = (struct reference *)f_node->value;
            struct object * child = heap_load(runtime->heap, *f_ref);
            if (child == NULL)
            {
                printf("ACTIVE REFERENCE LEADING TO DEAD MEMORY. THIS SHOULD BE IMPOSSIBLE\n");
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
    printf("marking from roots \n");
    fflush(stdout);
    struct queue * worklist = queue_init(DEFAULT_HEAP_SIZE);
    struct root * current_root = runtime->roots;
    while (current_root != NULL)
    {
        printf("fetching obj at current_root->ref->addr: %lu\n", current_root->ref->address);
        fflush(stdout);
        struct object * obj = heap_load(runtime->heap, *current_root->ref);

        if (obj != NULL && !obj->header.is_marked)
        {
            printf("visiting root: %s, marking header now\n", obj->id);
            fflush(stdout);
            obj->header.is_marked = true;
            queue_enqueue(worklist, obj);
            runtime_mark_worklist(runtime, worklist);
        }
        current_root = current_root->next;
    }
}

void runtime_compute_locations(struct runtime * runtime)
{
    uint32_t free_ptr = 0;
    for (struct heap_iterator heap_iter = heap_iterator_init(runtime->heap);
        !heap_iter_is_done(&heap_iter);
        heap_iter_next(&heap_iter))
    {
        struct object * obj = heap_iter_current_object(&heap_iter);
        if (obj->header.is_marked)
        {
            obj->header.forwarding_address = free_ptr;
            free_ptr += sizeof(struct object);
        }
    }
}

void runtime_update_object_references(struct runtime * runtime, struct object * obj)
{
    for (struct map_iterator obj_field_iter = map_iter(obj->fields);
        !map_iter_is_done(&obj_field_iter);
        map_iter_next(&obj_field_iter))
    {
        struct map_node * f_node = map_iter_current_node(&obj_field_iter);
        if (f_node->value == NULL)
        {
            printf("field: %s of obj: %s at %p is null, skipping\n", f_node->key, obj->id, obj);
            continue;
        }

        struct reference * f_ref = (struct reference *)f_node->value;
        struct object * child = heap_load(runtime->heap, *f_ref);
        struct reference * new_ref = (struct reference *)malloc(sizeof(struct reference));
        new_ref->address = child->header.forwarding_address;
        new_ref->size = sizeof(struct object);
        f_node->value = new_ref;
    }
}

void runtime_update_references(struct runtime * runtime)
{
    struct root * current_root = runtime->roots;
    while (current_root != NULL)
    {
        printf("fetching obj at current_root->ref->addr: %lu\n", current_root->ref->address);
        fflush(stdout);
        struct object * obj = heap_load(runtime->heap, *current_root->ref);
        runtime_update_object_references(runtime, obj);
        current_root = current_root->next;
    }

    for (struct heap_iterator heap_iter = heap_iterator_init(runtime->heap);
        !heap_iter_is_done(&heap_iter);
        heap_iter_next(&heap_iter))
    {
        struct object * obj = heap_iter_current_object(&heap_iter);
        if (obj->header.is_marked)
        {
            runtime_update_object_references(runtime, obj);
        }
    }
}

void runtime_relocate(struct runtime * runtime)
{
    for (struct heap_iterator heap_iter = heap_iterator_init(runtime->heap);
        !heap_iter_is_done(&heap_iter);
        heap_iter_next(&heap_iter))
    {
        struct object * obj = heap_iter_current_object(&heap_iter);
        if (obj->header.is_marked)
        {
            heap_store(runtime->heap, obj->header.forwarding_address, obj);
        }
        else
        {
            heap_free(runtime->heap, obj);
        }
    }
}

void runtime_compact(struct runtime * runtime)
{
    printf("compacting \n");
    fflush(stdout);

    runtime_compute_locations(runtime);
    runtime_update_references(runtime);
    runtime_relocate(runtime);
}

void runtime_collect(struct runtime * runtime)
{
    runtime_mark_from_roots(runtime);
    runtime_compact(runtime);
}

int main()
{
    struct heap * heap = heap_init(DEFAULT_HEAP_SIZE /*, alignment */);
    struct runtime * runtime = runtime_init(heap);

    struct map * r1_fields = map_init(10);
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

    struct map * a1_fields = map_init(10);
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

    struct object a2 = {
        .header = {
            .is_marked = false,
            .size = sizeof(struct object),
        },
        .id = "a2",
        .fields = map_init(0),
    };
    runtime_instantiate(runtime, &a2);

    struct object b1 = {
        .header = {
            .is_marked = false,
            .size = sizeof(struct object),
        },
        .id = "b1",
        .fields = map_init(0),
    };
    runtime_instantiate(runtime, &b1);

    struct object b2 = {
        .header = {
            .is_marked = false,
            .size = sizeof(struct object),
        },
        .id = "b2",
        .fields = map_init(0),
    };
    runtime_instantiate(runtime, &b2);

    struct object c = {
        .header = {
            .is_marked = false,
            .size = sizeof(struct object),
        },
        .id = "c",
        .fields = map_init(0),
    };
    runtime_instantiate(runtime, &c);

    runtime_add_root(runtime, "r1");

    runtime_assign_field(runtime, "r1", "a1", "a1");
    runtime_assign_field(runtime, "r1", "a2", "a2");
    
    runtime_assign_field(runtime, "a1", "b1", "b1");
    runtime_assign_field(runtime, "a1", "b2", "b2");

    runtime_collect(runtime);

    free(runtime);
    free(heap);
}
