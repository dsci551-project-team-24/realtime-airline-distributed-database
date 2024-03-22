class consistent_hashing:
    def __init__(self, server_nodes: list):
        self.s_nodes = server_nodes
        self.hashed_dict = {}
        for node in self.s_nodes:
            hash_val = hash(node)
            self.hashed_dict[hash_val] = node

    def find_hash_val(self, node_to_find: str):
        for ind,val in self.hashed_dict.items():
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
        except:
            min_val = min(self.hashed_dict.keys())
        return self.hashed_dict[min_val]
    
# def test():
#     nodes = ['server_one', 'pizzaapplegate', 'trying to test']
#     hasher = consistent_hashing(nodes)
#     print(hasher.hashed_dict)
#     hasher.add_node('somethingnew')
#     print(hasher.hashed_dict)
#     hasher.add_node('server_one')
#     print(hasher.hashed_dict)
#
#     print('-------------')
#
#     hasher.remove_node('server_one')
#     print(hasher.hashed_dict)
#     hasher.remove_node('server_one')
#     print(hasher.hashed_dict)
#
#     print('---------')
#     print(hasher.get_server('UA3255'))
#     print(hasher.get_server('SW465'))
#     print(hasher.get_server('AS87'))
#     print(hasher.get_server('UA3258'))
#     print(hasher.get_server('SW464'))
#     print(hasher.get_server('AS876'))
#     print(hasher.hashed_dict)
#
#
# if __name__ == '__main__':
#     test()