from typing import List

class Reference:
    def __init__(self, address: int):
        self.address = address


class Object:
    def __init__(self, size: int, id: str):
        self.size = size
        self.id = id
        self.fields = []
        self.marked = False

    def active_fields(self):
        return filter(lambda x: x is not None, self.fields)

    def add_field(self, ref: Reference):
        self.fields.append(ref)

    def mark(self):
        self.marked = True

    def unmark(self):
        self.marked = False

    def is_marked(self):
        return self.marked


class Heap:
    def __init__(self, size: int):
        self.size = size
        self.contents = [None for i in range(size)]

    def __iter__(self):
        self.iter_pos = 0;
        return self

    def __next__(self):
        if self.iter_pos < self.size:
            pos = self.iter_pos
            self.iter_pos += 1
            return Reference(pos), self.contents[pos]
        else:
            raise StopIteration

    def load(self, ref: Reference) -> Object:
        return self.contents[ref.address]
    
    def store(self, ref: Reference, obj: Object):
        self.contents[ref.address] = obj

    def free(self, ref: Reference):
        self.contents[ref.address] = None


class Allocator:
    def __init__(self, heap: Heap):
        self.heap = heap

    def allocate(self, size: int):
        # TODO -> take size in to account
        # TODO -> this only deals with a size of 1
        for ref, content in iter(self.heap):
            if content is None:
                return ref

        return None


class Collector:
    def __init__(self, heap: Heap):
        self.heap = heap

    def collect(self, roots: List[Reference]):
        print('beginning collection')
        self.mark_from_roots(roots)
        self.sweep()

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
            for field_ref in iter(obj.active_fields()):
                child_obj = self.heap.load(field_ref)
                if child_obj != None and not child_obj.is_marked():
                    child_obj.mark()
                    worklist.append(field_ref)

    def sweep(self):
        print('sweeping the heap')
        for address, obj in iter(self.heap):
            if obj is None:
                continue

            if obj.is_marked():
                obj.unmark()
            else:
                print('freeing unmarked obj: {}'.format(obj.id))
                self.heap.free(address)

class Runtime:
    def __init__(self, size: int):
        self.roots = []
        self.heap = Heap(size)
        self.allocator = Allocator(self.heap)
        self.collector = Collector(self.heap)

    # Mutator methods
    def new(self, size: int, id: str) -> Reference:
        print("attempting to allocate new object of size {}, with id: {}".format(size, id))

        ref = self.allocator.allocate(size)

        if ref == None:
            self.collector.collect(self.roots)
            ref = self.allocator.allocate(size)
            if ref == None:
                raise Exception("out of memory")
  
        self.write(ref, Object(size, id))
        return ref
    
    def read(self, ref: Reference) -> Object:
        return self.heap.load(ref)
    
    def write(self, ref: Reference, obj: Object):
        self.heap.store(ref, obj)

    def add_root(self, ref: Reference):
        self.roots.append(ref)

    def dereference(self, ref: Reference) -> Object:
        return self.heap.load(ref)

    def collect(self):
        self.collector.collect(self.roots)

def main():
    runtime = Runtime(10)
    build_object_graph(runtime) 
    runtime.collect()

# builds the following object graph
#
#               ROOT (r1)
#              /         \
#             a1         a2
#            /  \
#           b1   b2       
#                          c <- this should get collected
def build_object_graph(runtime: Runtime):
    r1 = runtime.new(1, "r1")
    runtime.add_root(r1)

    a1 = runtime.new(1, "a1")
    a2 = runtime.new(1, "a2")
    runtime.dereference(r1).add_field(a1)
    runtime.dereference(r1).add_field(a2)

    b1 = runtime.new(1, "b1")
    b2 = runtime.new(1, "b2")
    runtime.dereference(a1).add_field(b1)
    runtime.dereference(a1).add_field(b2)

    # this should get collected
    c = runtime.new(1, "TO_BE_COLLECTED")


if __name__ == "__main__":
    main()
