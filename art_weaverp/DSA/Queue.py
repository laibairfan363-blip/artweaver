class Queue:
    """Normal Queue implementation using a list."""
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def peek(self):
        if not self.is_empty():
            return self.items[0]
        return None

    def get_all(self):
        return self.items


class CircularQueue:
    """Circular Queue for Artist Load Balancing."""
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = self.rear = -1

    def enqueue(self, item):
        if (self.rear + 1) % self.capacity == self.front:
            # Queue is full
            return False
        elif self.front == -1:
            self.front = 0
            self.rear = 0
            self.queue[self.rear] = item
        else:
            self.rear = (self.rear + 1) % self.capacity
            self.queue[self.rear] = item
        return True

    def dequeue(self):
        if self.front == -1:
            return None
        
        item = self.queue[self.front]
        if self.front == self.rear:
            self.front = -1
            self.rear = -1
        else:
            self.front = (self.front + 1) % self.capacity
        return item

    def is_empty(self):
        return self.front == -1


class PriorityQueue:
    """Priority Queue for Premium Writers (using a list for simplicity, but behaving as PQ).
    Lower priority number means higher urgency (e.g. 1 is higher than 10).
    Or we can say 'is_premium' boolean flag. Let's use a tuple (priority, item).
    """
    def __init__(self):
        self.items = []

    def enqueue(self, item, priority):
        """Enqueue with priority. Higher priority value means higher importance? 
        The request says 'Priority Queue (premium writers top)'.
        Let's assume priority is integer: 10 = High (Premium), 1 = Low (Normal).
        We insert to keep the list sorted descending by priority.
        """
        entry = {'data': item, 'priority': priority}
        if self.is_empty():
            self.items.append(entry)
        else:
            inserted = False
            for i in range(len(self.items)):
                if priority > self.items[i]['priority']:
                    self.items.insert(i, entry)
                    inserted = True
                    break
            if not inserted:
                self.items.append(entry)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)['data']
        return None

    def is_empty(self):
        return len(self.items) == 0

    def get_all(self):
        return [x['data'] for x in self.items]
