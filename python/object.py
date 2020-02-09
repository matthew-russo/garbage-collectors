from typing import List
from enum import Enum


class Reference:
    def __init__(self, address: int, size: int):
        self.address = address
        self.size = size


class GarbageColor(Enum):
    PURPLE = 1
    BLACK = 2
    GREY = 3
    WHITE = 4


class Object:
    def __init__(self, id: str, fields: List[str]):
        self.id = id
        self.fields: Dict[str, Reference] = {f:None for f in fields}
        self.marked: bool = False
        self.forwarding_address: Reference = None
        self.rc: int = 0
        self.color: GarbageColor = None

    def active_fields(self):
        return filter(lambda x: x is not None, self.fields)

    def size(self) -> int:
        return len(self.fields) + 1

    def mark(self):
        self.marked = True

    def unmark(self):
        self.marked = False

    def is_marked(self) -> bool:
        return self.marked

