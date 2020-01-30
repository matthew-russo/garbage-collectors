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
        if field not in self.fields:
            raise ValueError('unknown field: {} on obj: {}'.format(field, self.id))

        self.fields[field] = ref

    def size(self) -> int:
        return len(self.fields) + 1

    def mark(self):
        self.marked = True

    def unmark(self):
        self.marked = False

    def is_marked(self) -> bool:
        return self.marked

    def set_forwarding_address(self, forwarding_addr: int):
        self.forwarding_address = forwarding_addr

    def forwarding_address() -> int:
        return self.forwarding_address


class Heap:
    def __init__(self, size: int, alignment: int):
        if size % alignment != 0:
            msg = 'Heap size needs to be a multiple of given alignment: {}, but was {}'.format(alignment, size)
            raise ValueError(msg)
        actual_size = size / 2
        self.size: int                   = actual_size
        self.from_space: List[Reference] = [None for _ in range(actual_size)]
        self.to_space: List[Reference]   = [None for _ in range(actual_size)]
        self.objs: Dict[str, Object]     = {} # obj id to obj

    def load(self, ref: Reference) -> Object:
        obj_id = self.current[ref.address]
        return self.objs[obj_id]
    
    def store(self, ref: Reference, obj: Object):
        if ref.size != obj.size():
            print('Trying to store object of size: {} in a reference slot of size: {}'.format(obj.size(), ref.size))
            sys.exit(1)

        for i in range(ref.address, ref.address + ref.size):
            self.current[i] = obj.id
        
        self.objs[obj.id] = obj

    def alloc(self, size: int) -> Reference:
        print('trying to allocate a chunk of size: {} while heap is: {}'.format(size, self.current))
        
        # need to find the first range of `size` that is all `None`s
        in_a_row = 0
        for n, content in enumerate(self.current):
            if content is None:
                in_a_row += 1

                if in_a_row == size:
                    starting_address = n - size + 1
                    print('found a valid chunk to allocate starting at address: {}'.format(starting_address))
                    for i in range(starting_address, starting_address + size):
                        self.current[i] = "__ALLOCATED_BUT_EMPTY__"
                    return Reference(starting_address, size)
            else:
                in_a_row = 0

        return None

    def free(self, ref: Reference):
        obj_id = self.current[ref.address]
        del self.objs[obj_id]

        for i in range(ref.address, ref.address + ref.size):
            self.current[i] = None

class Collector:
    def __init__(self, heap: Heap):
        self.heap = heap

    def collect():
        flip()
        initialize(worklist)
        for ref in roots:
            process(ref)
        while worklist:
            ref = worklist.pop()
            scan(ref)

    def flip():
        temp = self.heap.to_space
        self.heap.to_space = self.heap.from_space
        self.heap.from_space = temp

    def scan(ref: Reference):
        obj = self.heap.load(ref)
        for f_name, f_ref in obj.fields.items():
            process(f_ref)

    def process(ref: Reference):
        obj = self.heap.load(ref)
        if obj is not None:
            r

    def forward():
    
    def copy():

    def collect(self, roots: List[Reference]):
        print('beginning collection')
        self.mark_from_roots(roots)
        self.compact(roots)
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

    def mark(self, worklist: List[Reference]):
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

    def compact(self, roots: List[Reference]):
        print('beginning compaction')
        self.compute_locations(0, len(self.heap.contents), 0)
        self.update_references(roots, 0, len(self.heap.contents))
        self.relocate(0, len(self.heap.contents))
        print('compaction finished')

    def compute_locations(self, start: int, end: int, to: int):
        curr_ptr = start
        free = to
        while curr_ptr < end:
            obj_id = self.heap.contents[curr_ptr]
            if obj_id is None:
                curr_ptr += 1
                continue

            obj = self.heap.objs[obj_id]
            if obj.is_marked():
                obj.forwarding_address = free
                free += obj.size()
            curr_ptr += obj.size()

    def update_references(self, roots: List[Reference], start: int, end: int):
        for root in roots:
            obj = self.heap.load(root)
            for f_name, f_ref in obj.fields.items():
                child_obj = self.heap.load(f_ref)
                new_ref = Reference(child_obj.forwarding_address, obj.size())
                obj.set_field(f_name, new_ref)

        curr_ptr = start
        while curr_ptr < end:
            obj_id = self.heap.contents[curr_ptr]
            if obj_id is None:
                curr_ptr += 1
                continue

            obj = self.heap.objs[obj_id]
            if obj.is_marked():
                for f_name, f_ref in obj.fields.items():
                    child_obj = self.heap.load(f_ref)
                    new_ref = Reference(child_obj.forwarding_address, obj.size())
                    obj.set_field(f_name, new_ref)
            curr_ptr += obj.size()

    def relocate(self, start: int, end: int):
        curr_ptr = start
        while curr_ptr < end:
            obj_id = self.heap.contents[curr_ptr]
            if obj_id is None:
                curr_ptr += 1
                continue

            obj = self.heap.objs[obj_id]
            if obj.is_marked():
                new_ref = Reference(obj.forwarding_address, obj.size())
                self.heap.store(new_ref, obj)
                obj.unmark()
            else:
                for i in range(curr_ptr, curr_ptr + obj.size()):
                    self.heap.contents[i] = None
                del self.heap.objs[obj.id]
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
    m
