class Graph:
    """Adjacency List Graph for User Relationships."""
    def __init__(self):
        self.adj_list = {} # {user_id: [connected_user_ids]}

    def add_node(self, user_id):
        if user_id not in self.adj_list:
            self.adj_list[user_id] = []

    def add_edge(self, u, v):
        """Adds a directed edge from u to v. 
        For visualization: Writer -> Artist.
        """
        if u not in self.adj_list:
            self.add_node(u)
        if v not in self.adj_list:
            self.add_node(v)
        
        if v not in self.adj_list[u]:
            self.adj_list[u].append(v)

    def get_connections(self, user_id):
        return self.adj_list.get(user_id, [])

    def bfs(self, start_node):
        visited = set()
        queue = [start_node]
        visited.add(start_node)
        result = []

        while queue:
            vertex = queue.pop(0)
            result.append(vertex)

            for neighbor in self.adj_list.get(vertex, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return result

    def get_all_users(self):
        return list(self.adj_list.keys())
