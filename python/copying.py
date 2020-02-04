from typing import List

class Reference:
    def __init__(self, address: int, size: int):
        self.address = address
        self.size = size


class Object:
    def __init__(self, id: str, fields: List[str]):
        self.id = id
        self.fields: Dict[str, Reference] = {f:None for f in fields}
        self.forwarding_address = None

    def active_fields(self):
        return filter(lambda x: x is not None, self.fields)

    def set_field(self, field: str, ref: Reference):
        if field not in self.fields:
            raise ValueError('unknown field: {} on obj: {}'.format(field, self.id))

        self.fields[field] = ref

    def size(self) -> int:
        return len(self.fields) + 1

    def set_forwarding_address(self, forwarding_addr: int):
        self.forwarding_address = forwarding_addr

    def forwarding_address() -> int:
        return self.forwarding_address


class Heap:
    def __init__(self, size: int, alignment: int):
        if size % alignment != 0:
            msg = 'Heap size needs to be a multiple of given alignment: {}, but was {}'.format(alignment, size)
            raise ValueError(msg)
        actual_size = size // 2
        self.size: int                   = actual_size
        self.current: List[Reference] = [None for _ in range(actual_size)]
        self.copy_space: List[Reference]   = [None for _ in range(actual_size)]
        self.copy_ptr = 0
        self.objs: Dict[str, Object]     = {} # obj id to obj

    def load(self, ref: Reference) -> Object:
        obj_id = self.current[ref.address]
        return self.objs[obj_id]
    
    def store(self, ref: Reference, obj: Object, is_copy=False):
        memory_space: List[Reference] = self.current

        if is_copy:
            memory_space = self.copy_space

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

    def alloc_from_copy(self, size: int) -> Reference:
        to_return: int = self.copy_ptr
        self.copy_ptr += size
        return to_return

    def flip(self):
        self.current = self.copy_space
        self.copy_space = [None for _ in range(len(self.current))]
        self.copy_ptr = 0

    def free(self, ref: Reference):
        obj_id = self.current[ref.address]
        del self.objs[obj_id]

        for i in range(ref.address, ref.address + ref.size):
            self.current[i] = None

class Collector:
    def __init__(self, heap: Heap):
        self.heap: Heap = heap
        self.worklist: List[Reference] = []

    def collect(self, roots: List[Reference]):
        self.worlist: List[Reference] = []
        for root in roots:
            root.address = self.process(root)
        while self.worklist:
            ref = self.worklist.pop()
            self.scan(ref)
        self.heap.flip()

    def scan(self, ref: Reference):
        obj = self.heap.load(ref)
        for f_name, f_ref in obj.fields.items():
            obj.fields[f_name].address = self.process(f_ref)

    def process(self, ref: Reference) -> int:
        obj: Object = self.heap.load(ref)
        if obj is not None:
            return self.forward(obj)

    def forward(self, obj: Object) -> int:
        to_addr: int = obj.forwarding_address
        if to_addr is None:
            to_addr = self.copy(obj)
        return to_addr
    
    def copy(self, obj: Object):
        to_addr: int = self.heap.alloc_from_copy(obj.size())
        self.heap.store(Reference(address=to_addr, size=obj.size()), obj, is_copy=True)
        obj.forwarding_address = to_addr
        self.worklist.append(Reference(address=to_addr, size=obj.size()))
        return to_addr

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
