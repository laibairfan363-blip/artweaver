class MaxHeap:
    """Max Heap for Top Artists."""
    def __init__(self):
        self.heap = []

    def insert(self, item):
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def extract_max(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def _heapify_up(self, index):
        parent_index = (index - 1) // 2
        if index > 0 and self.heap[index]['points'] > self.heap[parent_index]['points']:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            self._heapify_up(parent_index)

    def _heapify_down(self, index):
        largest = index
        left_child = 2 * index + 1
        right_child = 2 * index + 2

        if left_child < len(self.heap) and self.heap[left_child]['points'] > self.heap[largest]['points']:
            largest = left_child

        if right_child < len(self.heap) and self.heap[right_child]['points'] > self.heap[largest]['points']:
            largest = right_child

        if largest != index:
            self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
            self._heapify_down(largest)
    
    def get_all_sorted(self):
        # Return all items sorted by points descending without destroying heap
        # Simplest way: Copy heap and extract all
        temp = list(self.heap)
        res = []
        # Sort using python's generic sort for display purposes, 
        # as extracting them one by one is effectively HeapSort logic already implemented in Sorting.py? 
        # But let's just return the intrinsic heap list, which is not strictly sorted, just heap property.
        # So we sort it.
        return sorted(temp, key=lambda x: x['points'], reverse=True)


class MinHeap:
    """Min Heap for Oldest Stories (or other use cases)."""
    def __init__(self):
        self.heap = []

    def insert(self, item):
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def extract_min(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def _heapify_up(self, index):
        parent_index = (index - 1) // 2
        # Assuming item has 'id' or 'timestamp' to compare. Let's assume 'id' for simplicity.
        if index > 0 and self.heap[index]['id'] < self.heap[parent_index]['id']:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            self._heapify_up(parent_index)

    def _heapify_down(self, index):
        smallest = index
        left_child = 2 * index + 1
        right_child = 2 * index + 2

        if left_child < len(self.heap) and self.heap[left_child]['id'] < self.heap[smallest]['id']:
            smallest = left_child

        if right_child < len(self.heap) and self.heap[right_child]['id'] < self.heap[smallest]['id']:
            smallest = right_child

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)
