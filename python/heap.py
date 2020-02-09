from typing import List
from object import Object, Reference


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


