
def count_sort(arr, key_func):
    """Count sort for stories by length (or small integer keys)."""
    if not arr:
        return []
    
    # Extract keys
    keys = [key_func(x) for x in arr]
    if not keys:
         return arr
         
    max_val = max(keys)
    min_val = min(keys)
    range_val = max_val - min_val + 1
    
    count = [0] * range_val
    output = [None] * len(arr)
    
    # Store count of each character
    for k in keys:
        count[k - min_val] += 1
    
    # Change count[i] so that count[i] now contains actual
    # position of this character in output array
    for i in range(1, len(count)):
        count[i] += count[i-1]
    
    # Build the output character array
    for i in range(len(arr) - 1, -1, -1):
        item = arr[i]
        k = key_func(item)
        output[count[k - min_val] - 1] = item
        count[k - min_val] -= 1
        
    return output

def bucket_sort(arr, key_func, bucket_count=10):
    """Bucket sort for grouping items."""
    if not arr:
        return []
    
    buckets = [[] for _ in range(bucket_count)]
    
    # Assume keys are normalized 0-1 or we mod them?
    # Let's say we sort by rating 1-5 or 1-10.
    # We'll just mod by bucket_count for this demo.
    for item in arr:
        k = int(key_func(item))
        index = k % bucket_count
        buckets[index].append(item)
        
    # Sort individual buckets and concatenate
    sorted_arr = []
    for bucket in buckets:
        # We can use any sort here, let's use python's timsort for the sub-buckets for simplicity
        bucket.sort(key=key_func)
        sorted_arr.extend(bucket)
        
    return sorted_arr

def heap_sort(arr, key_func):
    """Heap Sort."""
    n = len(arr)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i, key_func)
        
    # One by one extract elements
    for i in range(n-1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i] # swap
        heapify(arr, i, 0, key_func)
        
    return arr

def heapify(arr, n, i, key_func):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2
    
    if l < n and key_func(arr[l]) > key_func(arr[largest]):
        largest = l
        
    if r < n and key_func(arr[r]) > key_func(arr[largest]):
        largest = r
        
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest, key_func)
