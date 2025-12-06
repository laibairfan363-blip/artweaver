class Graph:
    def __init__(self):
        self.adj_list = {}

    def add_node(self, node):
        if node not in self.adj_list:
            self.adj_list[node] = []

    def add_edge(self, node1, node2):
        if node1 not in self.adj_list:
            self.add_node(node1)
        if node2 not in self.adj_list:
            self.add_node(node2)
        
        self.adj_list[node1].append(node2)
        # Assuming directed graph for "follows" or "visualized by"
        # If undirected, uncomment:
        # self.adj_list[node2].append(node1)

    def bfs(self, start_node):
        visited = set()
        queue = [start_node]
        visited.add(start_node)
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for neighbor in self.adj_list.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return result
    
    def get_connections(self, node):
        return self.adj_list.get(node, [])
