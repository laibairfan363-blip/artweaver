import heapq

class Queue:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def size(self):
        return len(self.items)

class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, priority):
        # heapq is a min-heap, so specific priority must be negated for max-priority behavior if desired.
        # Here we assume lower number = higher priority for now or just standard heap.
        # User requirement: "Priority Queue (premium writers ki stories top pe)"
        # So Premium = High Priority (e.g., 1), Normal = Low Priority (e.g., 2).
        # Python's heapq is a min-heap, so 1 pops before 2.
        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1

    def pop(self):
        if self._queue:
            return heapq.heappop(self._queue)[-1]
        return None

    def is_empty(self):
        return len(self._queue) == 0
