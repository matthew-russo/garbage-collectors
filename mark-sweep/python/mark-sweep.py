from typing import List

class Reference:
    def __init__(self, address: int, size: int):
        self.address = address
        self.size = size


class Object:
    def __init__(self, id: str, fields: List[str]):
        self.id = id
        self.fields: Dict[str, Reference] = {f:None for f in fields}
        self.marked = False

    def active_fields(self):
        return filter(lambda x: x is not None, self.fields)

    def set_field(self, field: str, ref: Reference):
        self.fields[field] = ref

    def size(self) -> int:
        return len(self.fields) + 1

    def mark(self):
        self.marked = True

    def unmark(self):
        self.marked = False

    def is_marked(self) -> bool:
        return self.marked


class Heap:
    def __init__(self, size: int, alignment: int):
        if size % alignment != 0:
            msg = 'Heap size needs to be a multiple of given alignment: {}, but was {}'.format(alignment, size)
            raise ValueError(msg)

        self.size = size
        self.contents = [None for _ in range(size)]
        self.objs = {} # obj id to obj

    def load(self, ref: Reference) -> Object:
        obj_id = self.contents[ref.address]
        return self.objs[obj_id]
    
    def store(self, ref: Reference, obj: Object):
        if ref.size != obj.size():
            print('Trying to store object of size: {} in a reference slot of size: {}'.format(obj.size(), ref.size))
            sys.exit(1)

        for i in range(ref.address, ref.address + ref.size):
            self.contents[i] = obj.id
        
        self.objs[obj.id] = obj

    def alloc(self, size: int) -> Reference:
        print('trying to allocate a chunk of size: {} while heap is: {}'.format(size, self.contents))
        
        # need to find the first range of `size` that is all `None`s
        in_a_row = 0
        for n, content in enumerate(self.contents):
            if content is None:
                in_a_row += 1

                if in_a_row == size:
                    starting_address = n - size + 1
                    print('found a valid chunk to allocate starting at address: {}'.format(starting_address))
                    for i in range(starting_address, starting_address + size):
                        self.contents[i] = "__ALLOCATED_BUT_EMPTY__"
                    return Reference(starting_address, size)
            else:
                in_a_row = 0

        return None

    def free(self, ref: Reference):
        obj_id = self.contents[ref.address]
        del self.objs[obj_id]

        for i in range(ref.address, ref.address + ref.size):
            self.contents[i] = None

class Collector:
    def __init__(self, heap: Heap):
        self.heap = heap

    def collect(self, roots: List[Reference]):
        print('beginning collection')
        self.mark_from_roots(roots)
        self.sweep()
        print('collection complete. heap is now: {}'.format(self.heap.contents))

    def mark_from_roots(self, roots: List[Reference]):
        print('marking roots')
        worklist: List[Reference] = []
        for ref in roots:
            obj = self.heap.load(ref)
            print('checking root: {}'.format(obj.id))
            if obj != None and not obj.is_marked():
                obj.mark()
                worklist.append(ref)
                self.mark(worklist)

    def mark(self, worklist):
        print('marking the worklist')
        while worklist:
            ref = worklist.pop()
            obj = self.heap.load(ref)
            for f_name, f_ref in obj.fields.items():
                if f_ref is None:
                    continue

                child_obj = self.heap.load(f_ref)
                if child_obj is None:
                    print('ACTIVE REFERENCE LEADING TO DEAD MEMORY. THIS SHOULD BE IMPOSSIBLE')
                    sys.exit(1)

                if not child_obj.is_marked():
                    child_obj.mark()
                    worklist.append(f_ref)


    def sweep(self):
        print('sweeping the heap')
        curr_ptr = 0

        while curr_ptr < len(self.heap.contents):
            obj_id = self.heap.contents[curr_ptr]

            if obj_id is None:
                curr_ptr += 1
                continue

            if obj_id == "__ALLOCATED_BUT_EMPTY__":
                print('There is probably a bug because we are cleaning up allocated memory that was never filled')
                self.heap.contents[curr_ptr] = None
                curr_ptr += 1
                continue

            obj = self.heap.objs[obj_id]

            if not obj.is_marked():
                print('freeing obj {} of size {}'.format(obj_id, obj.size()))
                self.heap.free(Reference(curr_ptr, obj.size()))

            curr_ptr += obj.size()

class Runtime:
    def __init__(self, heap_size: int, heap_alignment: int):
        self.roots = []
        self.heap = Heap(size = heap_size, alignment = heap_alignment)
        self.collector = Collector(self.heap)

    # Mutator methods
    def new(self, obj: Object) -> Reference:
        print("attempting to allocate new object of size {}, with id: {}".format(obj.size(), obj.id))

        ref = self.heap.alloc(obj.size())

        if ref == None:
            self.collector.collect(self.roots)
            ref = self.heap.alloc(obj.size())
            if ref == None:
                raise Exception("out of memory")
  
        self.write(ref, obj)
        return ref
    
    def read(self, ref: Reference) -> Object:
        return self.heap.load(ref)
    
    def write(self, ref: Reference, obj: Object):
        self.heap.store(ref, obj)

    def add_root(self, ref: Reference):
        self.roots.append(ref)

    def dereference(self, ref: Reference) -> Object:
        return self.heap.load(ref)

    def collect(self, interactive = False):
        self.collector.collect(self.roots)

def main():
    runtime = Runtime(heap_size = 100, heap_alignment = 1)
    build_object_graph(runtime) 
    runtime.collect(interactive = True)

# builds the following object graph
#
#               ROOT (r1)
#              /         \
#             a1         a2
#            /  \
#           b1   b2       
#                          c <- this should get collected
def build_object_graph(runtime: Runtime):
    r1 = runtime.new(Object('r1', ['a1', 'a2']))

    a1 = runtime.new(Object('a1', ['b1', 'b2']))
    a2 = runtime.new(Object('a2', []))
    
    b1 = runtime.new(Object('b1', []))
    b2 = runtime.new(Object('b2', []))
    
    # this should get collected
    c = runtime.new(Object("TO_BE_COLLECTED", []))

    runtime.dereference(r1).set_field('a1', a1)
    runtime.dereference(r1).set_field('a2', a2)

    runtime.dereference(a1).set_field('b1', b1)
    runtime.dereference(a1).set_field('b2', b2)

    runtime.add_root(r1)


if __name__ == "__main__":
    main()
