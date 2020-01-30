struct Object
{

}

struct Reference
{

}

struct Heap
{

}

struct Object * heap_load(struct Reference ref)
{

}

void * heap_alloc(int size)
{

}

void heap_free(void * to_free)
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
        obj = heap_load(heap, roots[i]);
        if obj != NULL && !obj->is_marked
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

void main()
{

}
