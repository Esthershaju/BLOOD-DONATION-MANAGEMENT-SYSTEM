"""
MODULE 4: Graph Processing - Hospital Transit & Supply Network.
Implements custom Graph using Adjacency List, with BFS (Queue) and DFS (Stack/Recursion) traversals.
"""
from collections import deque
from app import db

class HospitalGraph:
    """
    Graph data structure representing interconnected hospitals and blood distribution hubs.
    Vertices = Hospitals
    Edges = Transit routes with distance in kilometers.
    """
    def __init__(self):
        # adj_list: {hospital_id: [(neighbor_id, distance_km), ...]}
        self.adj_list = {}
        # hospital_details: {hospital_id: {name, city, phone}}
        self.hospital_details = {}

    def add_hospital(self, hospital_id, name, city, phone=""):
        """Adds a hospital vertex to the graph."""
        h_id = int(hospital_id)
        if h_id not in self.adj_list:
            self.adj_list[h_id] = []
        self.hospital_details[h_id] = {
            "hospital_id": h_id,
            "name": name,
            "city": city,
            "phone": phone
        }

    def add_route(self, h1_id, h2_id, distance_km=10, bidirectional=True):
        """Adds an undirected or directed weighted transit route between two hospitals."""
        h1 = int(h1_id)
        h2 = int(h2_id)
        if h1 not in self.adj_list:
            self.add_hospital(h1, f"Hospital #{h1}", "")
        if h2 not in self.adj_list:
            self.add_hospital(h2, f"Hospital #{h2}", "")

        # Check existing to avoid duplicates
        if not any(neigh == h2 for neigh, _ in self.adj_list[h1]):
            self.adj_list[h1].append((h2, distance_km))
        if bidirectional and not any(neigh == h1 for neigh, _ in self.adj_list[h2]):
            self.adj_list[h2].append((h1, distance_km))

    def get_neighbors(self, hospital_id):
        """Returns list of (neighbor_id, distance_km) for a given hospital."""
        return self.adj_list.get(int(hospital_id), [])

    def bfs(self, start_id):
        """
        Breadth-First Search (BFS) starting from start_id.
        Explores vertices layer-by-layer using a FIFO Queue.
        Returns:
            traversal_order: list of dicts
            steps_log: list of step explanation strings
        """
        start_id = int(start_id)
        if start_id not in self.adj_list:
            return [], [f"Start hospital #{start_id} not found in graph."]

        visited = set()
        queue = deque([start_id])
        visited.add(start_id)

        traversal_order = []
        steps_log = []
        step_num = 1

        steps_log.append(f"Initialized BFS with FIFO Queue. Enqueued Start Hospital #{start_id} ({self.hospital_details.get(start_id, {}).get('name', '')}).")

        while queue:
            current = queue.popleft()
            hosp_info = self.hospital_details.get(current, {"name": f"Hospital #{current}", "city": ""})
            traversal_order.append({"step": step_num, "hospital_id": current, **hosp_info})

            queue_state = [f"#{qid}" for qid in queue]
            steps_log.append(
                f"Step {step_num}: Dequeued #{current} ({hosp_info.get('name')}). "
                f"Examining connected neighbors..."
            )

            # Sort neighbors for deterministic traversal
            neighbors = sorted(self.adj_list.get(current, []), key=lambda x: x[0])
            discovered = []
            for neighbor, dist in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    discovered.append(f"#{neighbor} ({dist} km)")

            if discovered:
                steps_log.append(f"   ↳ Discovered & Enqueued: {', '.join(discovered)}")
            else:
                steps_log.append("   ↳ No unvisited neighbors.")

            step_num += 1

        return traversal_order, steps_log

    def dfs(self, start_id):
        """
        Depth-First Search (DFS) starting from start_id.
        Explores as deep as possible along each branch before backtracking using a LIFO Stack / Recursion.
        Returns:
            traversal_order: list of dicts
            steps_log: list of step explanation strings
        """
        start_id = int(start_id)
        if start_id not in self.adj_list:
            return [], [f"Start hospital #{start_id} not found in graph."]

        visited = set()
        traversal_order = []
        steps_log = []
        step_counter = [1]

        def _dfs_recursive(current, depth):
            visited.add(current)
            hosp_info = self.hospital_details.get(current, {"name": f"Hospital #{current}", "city": ""})
            traversal_order.append({"step": step_counter[0], "hospital_id": current, "depth": depth, **hosp_info})

            indent = "  " * depth
            steps_log.append(f"{indent}Step {step_counter[0]} [Depth {depth}]: Visiting #{current} ({hosp_info.get('name')}).")
            step_counter[0] += 1

            neighbors = sorted(self.adj_list.get(current, []), key=lambda x: x[0])
            for neighbor, dist in neighbors:
                if neighbor not in visited:
                    steps_log.append(f"{indent}   ↳ Descending along route to #{neighbor} ({dist} km)...")
                    _dfs_recursive(neighbor, depth + 1)

        _dfs_recursive(start_id, 0)
        return traversal_order, steps_log

    def generate_dot_graph(self, highlighted_path=None):
        """
        Generates Graphviz DOT syntax string to render network layout.
        Optionally highlights traversal path.
        """
        lines = [
            "graph HospitalNetwork {",
            '  layout=neato;',
            '  node [shape=box, style="filled,rounded", fillcolor="#e0f2fe", color="#0284c7", fontname="Helvetica"];',
            '  edge [color="#64748b", fontname="Helvetica", fontsize=10];'
        ]

        # Add nodes
        for h_id, details in self.hospital_details.items():
            label = f"{details['name']}\\n[{details.get('city', '')}]"
            lines.append(f'  hosp_{h_id} [label="{label}"];')

        # Add edges (undirected, so avoid duplicates)
        added_edges = set()
        for h1, neighbors in self.adj_list.items():
            for h2, dist in neighbors:
                edge_key = tuple(sorted([h1, h2]))
                if edge_key not in added_edges:
                    added_edges.add(edge_key)
                    lines.append(f'  hosp_{h1} -- hosp_{h2} [label="{dist} km"];')

        lines.append("}")
        return "\n".join(lines)


def build_hospital_graph_from_db():
    """
    Constructs and seeds the Hospital transit network using registered hospitals and route links.
    """
    graph = HospitalGraph()
    rows = db.fetch_all("SELECT hospital_id, hospital_name, city, phone FROM hospitals")
    for r in rows:
        graph.add_hospital(r["hospital_id"], r["hospital_name"], r["city"], r["phone"])

    # Default realistic transit network connecting the hospitals
    # Hospital IDs: 1 (City General), 2 (Apex Trauma), 3 (Metropolitan), 4 (LifeLine), 5 (Global Heart), 6 (St. Jude)
    routes = [
        (1, 3, 8),   # City General <-> Metropolitan Blood Center (8 km)
        (1, 4, 15),  # City General <-> LifeLine Specialty (15 km)
        (1, 5, 22),  # City General <-> Global Heart (22 km)
        (3, 4, 12),  # Metropolitan <-> LifeLine (12 km)
        (2, 6, 10),  # Apex Trauma <-> St. Jude Pune (10 km)
        (4, 5, 14),  # LifeLine <-> Global Heart (14 km)
        (5, 2, 35),  # Global Heart Thane <-> Apex Trauma Pune Express Corridor (35 km)
        (3, 6, 40)   # Metropolitan <-> St. Jude Pune Corridor (40 km)
    ]

    for h1, h2, dist in routes:
        # Check if both hospitals exist in database
        if h1 in graph.hospital_details and h2 in graph.hospital_details:
            graph.add_route(h1, h2, dist)

    return graph
