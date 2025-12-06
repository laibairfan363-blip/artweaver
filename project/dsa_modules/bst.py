class Node:
    def __init__(self, key, data):
        self.left = None
        self.right = None
        self.val = key
        self.data = data

class BST:
    def __init__(self):
        self.root = None

    def insert(self, key, data):
        if self.root is None:
            self.root = Node(key, data)
        else:
            self._insert(self.root, key, data)

    def _insert(self, root, key, data):
        if key < root.val:
            if root.left is None:
                root.left = Node(key, data)
            else:
                self._insert(root.left, key, data)
        else:
            if root.right is None:
                root.right = Node(key, data)
            else:
                self._insert(root.right, key, data)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, root, key):
        if root is None or root.val == key:
            return root
        if root.val < key:
            return self._search(root.right, key)
        return self._search(root.left, key)

    def inorder(self):
        res = []
        self._inorder(self.root, res)
        return res

    def _inorder(self, root, res):
        if root:
            self._inorder(root.left, res)
            res.append(root.data)
            self._inorder(root.right, res)
