import heapq

class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, val):
        heapq.heappush(self.heap, val)

    def pop(self):
        if self.heap:
            return heapq.heappop(self.heap)
        return None

    def peek(self):
        if self.heap:
            return self.heap[0]
        return None

class MaxHeap:
    def __init__(self):
        self.heap = []

    def push(self, val):
        # Invert value to simulate max heap with min heap
        heapq.heappush(self.heap, -val)

    def pop(self):
        if self.heap:
            return -heapq.heappop(self.heap)
        return None
    
    def peek(self):
        if self.heap:
            return -self.heap[0]
        return None
