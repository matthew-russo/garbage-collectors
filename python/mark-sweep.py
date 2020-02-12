from typing import List
import sys
from object import Object, Reference
from heap import Heap


class Collector:
    def __init__(self, heap: Heap):
        self.heap: Heap = heap

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

    def mark(self, worklist: List[Reference]):
        print('marking the worklist')
        while worklist:
            ref: Reference = worklist.pop()
            obj: Object = self.heap.load(ref)
            for f_name, f_ref in obj.fields.items():
                if f_ref is None:
                    continue

                child_obj: Object = self.heap.load(f_ref)
                if child_obj is None:
                    print('ACTIVE REFERENCE LEADING TO DEAD MEMORY. THIS SHOULD BE IMPOSSIBLE')
                    sys.exit(1)

                if not child_obj.is_marked():
                    child_obj.mark()
                    worklist.append(f_ref)


    def sweep(self):
        print('sweeping the heap')
        curr_ptr: int = 0

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
        self.roots: Dict[str, Reference] = {}
        self.heap: Heap = Heap(size = heap_size, alignment = heap_alignment)
        self.collector: Collector = Collector(self.heap)

    # Mutator methods
    def new(self, obj: Object) -> Reference:
        print("attempting to allocate new object of size {}, with id: {}".format(obj.size(), obj.id))

        ref = self.heap.alloc(obj.size())

        if ref == None:
            self.collector.collect(self.roots.values())
            ref = self.heap.alloc(obj.size())
            if ref == None:
                raise Exception("out of memory")
  
        self.write(ref, obj)
        self.roots[obj.id] = ref
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

    def drop(self, obj_id: str):
        if obj_id in self.roots:
            del self.roots[obj_id]
        else:
            print("attempting to drop object that doesn't exist: {}".format(obj_id))
            sys.exit(1)

    def collect(self):
        print('heap before collection: ')
        self.heap.visualize()
        self.collector.collect(self.roots.values())
        print('heap after collection: ')
        self.heap.visualize()

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
#                            c <- this should get collected
#
def build_object_graph(runtime: Runtime):
    r1 = runtime.new(Object('r1', ['a1', 'a2']))
    print('\n\n')

    a1 = runtime.new(Object('a1', ['b1', 'b2']))
    print('\n\n')
    a2 = runtime.new(Object('a2', []))
    print('\n\n')
    
    b1 = runtime.new(Object('b1', []))
    print('\n\n')
    b2 = runtime.new(Object('b2', []))
    print('\n\n')
    
    # this should get collected
    to_be_collected = runtime.new(Object("c", []))

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

