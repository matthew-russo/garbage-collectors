from typing import List
from object import Object, Reference
from heap import Heap

class Collector:
    def __init__(self, heap: Heap):
        self.heap = heap

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
                obj.fields[f_name] = new_ref

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
                    obj.fields[f_name] = new_ref
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

    def set_field(self, src: Reference, field: str, target: Reference):
        src_object = self.heap.load(src)

        if field not in src_object.fields:
            raise ValueError('unknown field: {} on obj: {}'.format(field, self.id))

        src_object.fields[field] = target

    def add_root(self, ref: Reference):
        self.roots.append(ref)

    def collect(self):
        self.collector.collect(self.roots)

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
    c = runtime.new(Object("TO_BE_COLLECTED", []))

    runtime.set_field(r1, 'a1', a1)
    runtime.set_field(r1, 'a2', a2)

    runtime.set_field(a1, 'b1', b1)
    runtime.set_field(a1, 'b2', b2)

    runtime.add_root(r1)


if __name__ == "__main__":
    main()
