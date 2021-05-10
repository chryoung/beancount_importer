class Node:
    def __init__(self, value, parent=None):
        self.value = value
        self.children: list = []
        self.parent: Node = parent

    def add_child_node(self, child):
        self.children.append(child)

    def add_child(self, value):
        self.children.append(Node(value, self))

    def remove_child(self, value):
        self.children = [child for child in self.children if child.value != value]

    def has_child(self, value):
        return any([child.value == value for child in self.children])

    def get_child(self, value):
        for child in self.children:
            if child.value == value:
                return child

        return None

    def is_leaf(self):
        return not self.children

def print_tree_dfs(root: Node, level=0):
    print(' ' * level + root.value)
    for child in root.children:
        print_tree_dfs(child, level + 1)
