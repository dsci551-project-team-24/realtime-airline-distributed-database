# File: hashing_module.py

class ConsistentHashing:
    def __init__(self, server_nodes: list):
        self.s_nodes = server_nodes
        self.hashed_dict = {}
        for node in self.s_nodes:
            hash_val = hash(node)
            self.hashed_dict[hash_val] = node

    def find_hash_val(self, node_to_find: str):
        for ind, val in self.hashed_dict.items():
            if val == node_to_find:
                return ind
        return -1

    def add_node(self, node_to_add: str):
        if self.find_hash_val(node_to_add) == -1:
            self.s_nodes.append(node_to_add)
            hash_val = hash(node_to_add)
            self.hashed_dict[hash_val] = node_to_add
            return 1
        else:
            return -1

    def remove_node(self, node_to_remove: str):
        hash_val = self.find_hash_val(node_to_remove)
        if hash_val != -1:
            self.s_nodes.remove(node_to_remove)
            del self.hashed_dict[hash_val]
            return 1
        else:
            return -1

    def get_server(self, data):
        hash_val = hash(data)
        try:
            min_val = min(i for i in self.hashed_dict.keys() if i > hash_val)
        except ValueError:
            min_val = min(self.hashed_dict.keys())
        return self.hashed_dict[min_val]