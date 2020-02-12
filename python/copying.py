from typing import List
import sys
from object import Object, Reference
from heap import Heap


class Collector:
    def __init__(self, from_heap: Heap, to_heap: Heap):
        self.from_heap: Heap = from_heap
        self.to_heap: Heap = to_heap
        self.worklist: List[Reference] = []

    def flip_heaps(self):
        temp = self.from_heap
        self.from_heap = self.to_heap
        self.to_heap = temp
        self.to_heap.clear()

        return self.from_heap, self.to_heap

    def collect(self, roots: List[Reference]):
        self.worlist: List[Reference] = []
        for root in roots:
            root.address = self.forward(root)
        while self.worklist:
            ref = self.worklist.pop()
            obj = self.from_heap.load(ref)
            self.scan(obj)
        return self.flip_heaps()

    def scan(self, obj: Object):
        for f_name, f_ref in obj.fields.items():
            obj.fields[f_name].address = self.forward(f_ref)
        
    def forward(self, ref: Reference) -> int:
        obj: Object = self.from_heap.load(ref)
        if obj is not None:
            to_addr: int = obj.forwarding_address
            if to_addr is None:
                to_ref = self.copy(obj)
                to_addr = to_ref.address
            return to_addr
    
    def copy(self, obj: Object) -> Reference:
        to_ref: Reference = self.to_heap.alloc(obj.size())
        self.to_heap.store(to_ref, obj)
        obj.forwarding_address = to_ref.address
        self.worklist.append(to_ref)
        return to_ref

class Runtime:
    def __init__(self, heap_size: int, heap_alignment: int):
        self.roots: Dict[str, Reference] = {}
        actual_heap_size = heap_size // 2
        self.from_heap = Heap(size = actual_heap_size, alignment = heap_alignment)
        self.to_heap = Heap(size = actual_heap_size, alignment = heap_alignment)
        self.collector = Collector(self.from_heap, self.to_heap)

    # Mutator methods
    def new(self, obj: Object) -> Reference:
        print("attempting to allocate new object of size {}, with id: {}".format(obj.size(), obj.id))

        ref = self.from_heap.alloc(obj.size())

        if ref == None:
            self.collector.collect(self.roots.values())
            ref = self.from_heap.alloc(obj.size())
            if ref == None:
                raise Exception("out of memory")
  
        self.write(ref, obj)
        self.roots[obj.id] = ref
        return ref
    
    def read(self, ref: Reference) -> Object:
        return self.from_heap.load(ref)
    
    def write(self, ref: Reference, obj: Object):
        self.from_heap.store(ref, obj)

    def set_field(self, src: Reference, field: str, target: Reference):
        src_object = self.from_heap.load(src)

        if field not in src_object.fields:
            raise ValueError('unknown field: {} on obj: {}'.format(field, self.id))

        src_object.fields[field] = target

    def drop(self, obj_id: str):
        if obj_id in self.roots:
            del self.roots[obj_id]
        else:
            print("attempting to drop object that doesn't exist: {}".format(obj_id))
            sys.exit(1)

    def collect(self):
        print('heap before collection: ')
        self.from_heap.visualize()
        self.from_heap, self.to_heap = self.collector.collect(self.roots.values())
        print('heap after collection: ')
        self.from_heap.visualize()

def main():
    runtime = Runtime(heap_size = 100, heap_alignment = 1)
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
    r1 = runtime.new(Object('r1', ['a1', 'a2']))

    a1 = runtime.new(Object('a1', ['b1', 'b2']))
    a2 = runtime.new(Object('a2', []))
    
    b1 = runtime.new(Object('b1', []))
    b2 = runtime.new(Object('b2', []))
    
    # this should get collected
    c = runtime.new(Object("c", []))

    runtime.set_field(r1, 'a1', a1)
    runtime.set_field(r1, 'a2', a2)

    runtime.set_field(a1, 'b1', b1)
    runtime.set_field(a1, 'b2', b2)

    runtime.drop('a1')
    runtime.drop('a2')
    runtime.drop('b2')
    runtime.drop('c')


if __name__ == "__main__":
    main()
