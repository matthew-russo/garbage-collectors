from typing import List
from object import Object, Reference
from heap import Heap


class Runtime:
    def __init__(self, heap_size: int, heap_alignment: int):
        self.roots = []
        self.heap = Heap(size = heap_size, alignment = heap_alignment)

    # Mutator methods
    def new(self, obj: Object) -> Reference:
        print("attempting to allocate new object of size {}, with id: {}".format(obj.size(), obj.id))

        ref = self.heap.alloc(obj.size())

        if ref == None:
            raise Exception("out of memory")
  
        self.write(ref, obj)
        return ref
    
    def write(self, ref: Reference, obj: Object):
        self.heap.store(ref, obj)

    def add_root(self, ref: Reference):
        self.roots.append(ref)

    def set_field(self, src: Reference, field: str, target: Reference):
        src_object = self.heap.load(src)

        if field not in src_object.fields:
            raise ValueError('unknown field: {} on obj: {}'.format(field, self.id))

        self.add_reference(target)
        self.delete_reference(src_object.fields[field])
        src_object.fields[field] = target

    def add_reference(self, ref: Reference):
        if ref is not None:
            obj = self.heap.load(ref)
            obj.rc = obj.rc + 1

    def delete_reference(self, ref: Reference):
        if ref is not None:
            obj = self.heap.load(ref)
            obj.rc = obj.rc - 1
            if obj.rc == 0:
                for f_name, f_ref in obj.fields:
                    delete_reference(f_ref)
                self.heap.free(ref)

def main():
    runtime = Runtime(heap_size = 100, heap_alignment = 1)
    build_object_graph(runtime) 

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

    runtime.set_field(r1, 'a1', a1)
    runtime.set_field(r1, 'a2', a2)

    runtime.set_field(a1, 'b1', b1)
    runtime.set_field(a1, 'b2', b2)

    runtime.add_root(r1)


if __name__ == "__main__":
    main()

