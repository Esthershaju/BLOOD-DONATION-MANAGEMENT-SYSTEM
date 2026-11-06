"""
MODULE 3: Hierarchical Data Management - Binary Search Tree (BST).
Uses Donor ID as the BST key, demonstrating Insert, Search, and Traversals (Inorder, Preorder, Postorder).
"""
from app import db

# ==============================================================================
# DATA STRUCTURE: BINARY SEARCH TREE (BST)
# ==============================================================================

class BSTNode:
    """Represents an individual node in the Donor Binary Search Tree."""
    def __init__(self, key, data=None):
        self.key = int(key)       # Donor ID (unique numeric key)
        self.data = data or {}     # Donor record details
        self.left = None           # Pointer to left child (keys < self.key)
        self.right = None          # Pointer to right child (keys > self.key)

    def to_dict(self):
        return {
            "key": self.key,
            "name": self.data.get("name", ""),
            "blood_group": self.data.get("blood_group", ""),
            "city": self.data.get("city", "")
        }

class DonorBST:
    """
    Binary Search Tree data structure keyed on Donor ID.
    Supports Insertion, Search with path tracing, and recursive Tree Traversals.
    """
    def __init__(self):
        self.root = None
        self._count = 0

    def is_empty(self):
        return self.root is None

    def insert(self, key, data=None):
        """
        Inserts a donor into the BST based on key (Donor ID).
        Time Complexity: O(log n) average, O(n) worst-case.
        """
        key = int(key)
        new_node = BSTNode(key, data)
        if self.root is None:
            self.root = new_node
            self._count += 1
            return True

        curr = self.root
        while True:
            if key < curr.key:
                if curr.left is None:
                    curr.left = new_node
                    self._count += 1
                    return True
                curr = curr.left
            elif key > curr.key:
                if curr.right is None:
                    curr.right = new_node
                    self._count += 1
                    return True
                curr = curr.right
            else:
                # Key already exists: update data
                curr.data = data or {}
                return False

    def search(self, key):
        """
        Searches for a donor by key in the BST.
        Tracks the decision path taken (e.g. ROOT -> RIGHT -> LEFT).
        Returns: (node, path: list of str, comparisons: int)
        Time Complexity: O(log n) average, O(n) worst-case.
        """
        key = int(key)
        curr = self.root
        path = []
        comparisons = 0

        while curr:
            comparisons += 1
            path.append(f"Node ID #{curr.key} ({curr.data.get('name', 'N/A')})")
            if key == curr.key:
                return curr, path, comparisons
            elif key < curr.key:
                path.append(f"  ↳ [{key} < {curr.key}] ➔ Move Left")
                curr = curr.left
            else:
                path.append(f"  ↳ [{key} > {curr.key}] ➔ Move Right")
                curr = curr.right

        return None, path, comparisons

    def inorder_traversal(self):
        """
        Inorder Traversal: Left -> Root -> Right
        Visits nodes in ascending order of keys (Donor IDs).
        Returns: list of dicts
        """
        result = []
        def _inorder(node):
            if node:
                _inorder(node.left)
                result.append({"key": node.key, **node.data})
                _inorder(node.right)
        _inorder(self.root)
        return result

    def preorder_traversal(self):
        """
        Preorder Traversal: Root -> Left -> Right
        Used to copy or serialize tree structures.
        Returns: list of dicts
        """
        result = []
        def _preorder(node):
            if node:
                result.append({"key": node.key, **node.data})
                _preorder(node.left)
                _preorder(node.right)
        _preorder(self.root)
        return result

    def postorder_traversal(self):
        """
        Postorder Traversal: Left -> Right -> Root
        Used in bottom-up deletion or subtree calculations.
        Returns: list of dicts
        """
        result = []
        def _postorder(node):
            if node:
                _postorder(node.left)
                _postorder(node.right)
                result.append({"key": node.key, **node.data})
        _postorder(self.root)
        return result

    def get_height(self):
        """Calculates maximum depth/height of the tree."""
        def _height(node):
            if not node:
                return 0
            return 1 + max(_height(node.left), _height(node.right))
        return _height(self.root)

    def size(self):
        """Returns total number of nodes in the BST."""
        return self._count

    def generate_dot_graph(self):
        """
        Generates Graphviz DOT syntax string for visual rendering of the BST.
        """
        if not self.root:
            return None
        lines = ["digraph BST {", '  node [shape=record, style="filled,rounded", fillcolor="#fee2e2", color="#dc2626", fontname="Helvetica"];', '  edge [color="#475569", fontname="Helvetica"];']
        
        def _build_dot(node):
            if not node:
                return
            label = f"ID #{node.key} | {node.data.get('name', '')} | {node.data.get('blood_group', '')}"
            lines.append(f'  node_{node.key} [label="{label}"];')
            
            if node.left:
                lines.append(f'  node_{node.key} -> node_{node.left.key} [label="L"];')
                _build_dot(node.left)
            if node.right:
                lines.append(f'  node_{node.key} -> node_{node.right.key} [label="R"];')
                _build_dot(node.right)

        _build_dot(self.root)
        lines.append("}")
        return "\n".join(lines)


def build_bst_from_database():
    """
    Fetches all donors from MySQL and builds a DonorBST.
    Returns: DonorBST instance
    """
    rows = db.fetch_all("SELECT * FROM donors ORDER BY donor_id ASC")
    bst = DonorBST()
    for row in rows:
        bst.insert(row["donor_id"], row)
    return bst
