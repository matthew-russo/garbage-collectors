from typing import List
import shutil
from functools import reduce
from object import Object, Reference


class Heap:
    def __init__(self, size: int, alignment: int):
        if size % alignment != 0:
            msg = 'Heap size needs to be a multiple of given alignment: {}, but was {}'.format(alignment, size)
            raise ValueError(msg)

        self.size = size
        self.contents = [None for _ in range(size)]
        self.objs = {} # obj id to obj
        self.visualizer = HeapVisualizer(self)

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
        print('trying to allocate a chunk of size: {}'.format(size))

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

    def clear(self):
        self.contents = [None for _ in range(self.size)]
        self.objs = {} # obj id to obj

    def visualize(self):
        self.visualizer.visualize()


class HeapVisualizerCell:
    def __init__(self, cell_id: str):
        self.cell_top_bottom = '+{}+'.format('-' * (len(cell_id) + 2))
        self.cell_middle = '| {} |'.format(cell_id)


class HeapVisualizer:
    def __init__(self, heap: Heap):
        self.heap: Heap = heap
        terminal_size = shutil.get_terminal_size((80, 20))
        self.columns = terminal_size.columns

    def visualize(self):
        cells: [] = []
        for item in self.heap.contents:
            cell_id = item
            if item is None:
                cell_id = ' '

            cells.append(HeapVisualizerCell(cell_id))

        return self.megacell(cells)

    def megacell(self, cells: List[HeapVisualizerCell]):
        tops = map(lambda c: c.cell_top_bottom, cells)
        middles = map(lambda c: c.cell_middle, cells)
        bottoms = map(lambda c: c.cell_top_bottom, cells)
        
        megatop = reduce(lambda a, b: a + b, tops)
        megamiddle = reduce(lambda a, b: a + b, middles)
        megabottom = reduce(lambda a, b: a + b, bottoms)

        split_tops    = list(divide_chunks(megatop,    self.columns))
        split_middles = list(divide_chunks(megamiddle, self.columns))
        split_bottoms = list(divide_chunks(megabottom, self.columns))

        for i in range(0, len(split_tops)):
            print(split_tops[i])
            print(split_middles[i])
            print(split_bottoms[i])

def divide_chunks(l, n): 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 
 

