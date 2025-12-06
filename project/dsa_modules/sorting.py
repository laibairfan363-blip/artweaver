def count_sort_stories_by_length(stories):
    # stories is a list of dicts, each having 'content'
    if not stories:
        return []
    
    max_len = 0
    for s in stories:
        l = len(s.get('content', ''))
        if l > max_len:
            max_len = l
            
    # Simple bucket approach for demonstration if range is small, 
    # but for length, standard sorting with key is more practical in Python.
    # implementing basic count sort logic for "length" category if we bin them.
    # Let's assume we sort by "length count" directly? 
    # Or actually implement a generic sort?
    # Requirement: "Use your own algorithms (NOT built-in)"
    # Let's do a simple count sort on "id" or small integer property?
    # Or just Bubble Sort for simplicity if "own algorithm" is the key.
    # But user asked for Count, Radix, Heap, Bucket.
    
    # Bucket Sort for story length
    if len(stories) == 0:
        return []

    # 1. Create empty buckets
    bucket_count = 10
    buckets = [[] for _ in range(bucket_count)]
    
    # 2. Put elements into buckets
    # Normalizing length to 0-9 roughly? or just ranges
    for s in stories:
        l = len(s.get('content', ''))
        index = min(l // 100, bucket_count - 1) # simple hashing
        buckets[index].append(s)
        
    # 3. Sort individual buckets (using insertion sort for "own algo")
    sorted_stories = []
    for bucket in buckets:
        insertion_sort(bucket, key=lambda x: len(x.get('content', '')))
        sorted_stories.extend(bucket)
        
    return sorted_stories

def insertion_sort(arr, key=lambda x: x):
    for i in range(1, len(arr)):
        key_item = arr[i]
        j = i - 1
        while j >= 0 and key(arr[j]) > key(key_item):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key_item

def heap_sort(arr, key=lambda x: x):
    # Standard heap sort
    n = len(arr)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i, key)
        
    # Extract elements
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0, key)

def heapify(arr, n, i, key):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2
    
    if l < n and key(arr[l]) > key(arr[largest]):
        largest = l
        
    if r < n and key(arr[r]) > key(arr[largest]):
        largest = r
        
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest, key)

