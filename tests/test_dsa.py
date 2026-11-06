"""
Automated Unit Tests for DSA Modules in Blood Donation Management System.
Verifies Linked List, Queue, Stack, BST, Graph, Searching, Sorting, Greedy, DP, and Backtracking.
"""
import sys
import os

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.donor import DonorLinkedList
from app.requests import BloodRequestQueue, OperationStack
from app.tree import DonorBST
from app.graph import HospitalGraph
from app.searching import linear_search, binary_search
from app.sorting import insertion_sort
from app.algorithms import greedy_donor_matching, dp_blood_request_optimization, backtracking_exact_units

def test_linked_list():
    ll = DonorLinkedList()
    assert ll.is_empty()
    ll.insert_at_end({"donor_id": 1, "name": "Aarav", "blood_group": "O+", "available": 1})
    ll.insert_at_end({"donor_id": 2, "name": "Priya", "blood_group": "A+", "available": 0})
    ll.insert_at_beginning({"donor_id": 3, "name": "Rohan", "blood_group": "B+", "available": 1})
    
    assert ll.size() == 3
    records = ll.to_list()
    assert [r["donor_id"] for r in records] == [3, 1, 2]
    
    node, steps = ll.find_by_id(1)
    assert node is not None and node.name == "Aarav"
    
    deleted, ok = ll.delete_by_id(1)
    assert ok and deleted.donor_id == 1
    assert ll.size() == 2
    assert [r["donor_id"] for r in ll.to_list()] == [3, 2]
    print("[PASS] Linked List tests passed.")

def test_queue_and_stack():
    # Queue (FIFO)
    q = BloodRequestQueue()
    assert q.is_empty()
    q.enqueue({"req_id": 101, "patient": "Alpha"})
    q.enqueue({"req_id": 102, "patient": "Beta"})
    assert q.size() == 2
    assert q.peek()["req_id"] == 101
    dequeued = q.dequeue()
    assert dequeued["req_id"] == 101
    assert q.dequeue()["req_id"] == 102
    assert q.is_empty()
    print("[PASS] FIFO Queue tests passed.")

    # Stack (LIFO)
    stk = OperationStack()
    assert stk.is_empty()
    stk.push({"action": "A"})
    stk.push({"action": "B"})
    assert stk.peek()["action"] == "B"
    assert stk.pop()["action"] == "B"
    assert stk.pop()["action"] == "A"
    assert stk.is_empty()
    print("[PASS] LIFO Stack tests passed.")

def test_bst():
    bst = DonorBST()
    bst.insert(20, {"name": "Root"})
    bst.insert(10, {"name": "Left"})
    bst.insert(30, {"name": "Right"})
    bst.insert(5, {"name": "Left-Left"})
    bst.insert(15, {"name": "Left-Right"})

    # Inorder must be strictly ascending: 5, 10, 15, 20, 30
    inorder_keys = [node["key"] for node in bst.inorder_traversal()]
    assert inorder_keys == [5, 10, 15, 20, 30]

    # Preorder: 20, 10, 5, 15, 30
    preorder_keys = [node["key"] for node in bst.preorder_traversal()]
    assert preorder_keys == [20, 10, 5, 15, 30]

    # Postorder: 5, 15, 10, 30, 20
    postorder_keys = [node["key"] for node in bst.postorder_traversal()]
    assert postorder_keys == [5, 15, 10, 30, 20]

    # Search
    node, path, comparisons = bst.search(15)
    assert node is not None and node.key == 15
    assert comparisons == 3
    print("[PASS] BST tests passed.")

def test_graph():
    g = HospitalGraph()
    g.add_hospital(1, "Hosp A", "City 1")
    g.add_hospital(2, "Hosp B", "City 1")
    g.add_hospital(3, "Hosp C", "City 2")
    g.add_hospital(4, "Hosp D", "City 2")

    g.add_route(1, 2, 10)
    g.add_route(1, 3, 20)
    g.add_route(2, 4, 15)

    bfs_order, bfs_logs = g.bfs(1)
    bfs_ids = [h["hospital_id"] for h in bfs_order]
    assert bfs_ids[0] == 1
    # 2 and 3 should be visited before 4
    assert set(bfs_ids[1:3]) == {2, 3}
    assert bfs_ids[3] == 4

    dfs_order, dfs_logs = g.dfs(1)
    dfs_ids = [h["hospital_id"] for h in dfs_order]
    assert len(dfs_ids) == 4
    print("[PASS] Graph BFS/DFS tests passed.")

def test_searching_and_sorting():
    sample_donors = [
        {"donor_id": 4, "name": "Vikram", "blood_group": "AB+", "city": "Pune"},
        {"donor_id": 1, "name": "Aarav", "blood_group": "O+", "city": "Mumbai"},
        {"donor_id": 3, "name": "Rohan", "blood_group": "B+", "city": "Mumbai"},
        {"donor_id": 2, "name": "Priya", "blood_group": "A+", "city": "Pune"}
    ]

    # Linear Search
    matches, logs, comps = linear_search(sample_donors, "city", "Mumbai")
    assert len(matches) == 2
    assert comps == 4

    # Insertion Sort by Donor ID
    sorted_by_id, metrics, _ = insertion_sort(sample_donors, sort_field="donor_id", ascending=True)
    assert [d["donor_id"] for d in sorted_by_id] == [1, 2, 3, 4]

    # Binary Search on sorted donors
    found, b_logs, b_comps = binary_search(sorted_by_id, 3)
    assert found is not None and found["donor_id"] == 3
    assert b_comps <= 3

    # Insertion Sort by Name
    sorted_by_name, _, _ = insertion_sort(sample_donors, sort_field="name", ascending=True)
    assert [d["name"] for d in sorted_by_name] == ["Aarav", "Priya", "Rohan", "Vikram"]
    print("[PASS] Searching & Sorting tests passed.")

def test_algorithms():
    donors = [
        {"donor_id": 1, "name": "D1", "blood_group": "O-", "available": 1, "last_donation_date": "2023-01-01"},
        {"donor_id": 2, "name": "D2", "blood_group": "A+", "available": 1, "last_donation_date": "2024-01-01"},
        {"donor_id": 3, "name": "D3", "blood_group": "B+", "available": 0, "last_donation_date": "2024-01-01"},
        {"donor_id": 4, "name": "D4", "blood_group": "A+", "available": 1, "last_donation_date": "2023-05-01"}
    ]

    # 1. Greedy
    selected, metrics, logs = greedy_donor_matching(donors, "A+", units_needed=2)
    assert len(selected) == 2
    # Exact matches (D2, D4) or O- (D1) should be chosen over unavailable D3
    assert all(d["available"] == 1 for d in selected)

    # 2. Dynamic Programming
    requests = [
        {"request_id": 1, "hospital_name": "H1", "units": 3, "urgency": "Critical"}, # score = 10
        {"request_id": 2, "hospital_name": "H2", "units": 2, "urgency": "Urgent"},   # score = 5
        {"request_id": 3, "hospital_name": "H3", "units": 4, "urgency": "Normal"},   # score = 2
        {"request_id": 4, "hospital_name": "H4", "units": 1, "urgency": "Urgent"}    # score = 5
    ]
    # With capacity 5: Optimal choice is req 1 (3u, score 10) + req 4 (1u, score 5) or req 2 (2u, score 5) + req 1 (3u, score 10) -> score 15
    selected_dp, max_score, used_units, dp_table, _, _ = dp_blood_request_optimization(requests, blood_capacity=5)
    assert max_score == 15
    assert used_units <= 5

    # 3. Backtracking
    pledges = [
        {"donor_id": 1, "name": "A", "units": 2},
        {"donor_id": 2, "name": "B", "units": 3},
        {"donor_id": 3, "name": "C", "units": 1},
        {"donor_id": 4, "name": "D", "units": 4}
    ]
    # Target = 5: Solutions can be [2, 3] and [1, 4]
    combos, step_logs, stats = backtracking_exact_units(pledges, target_units=5)
    assert len(combos) >= 2
    for c in combos:
        assert sum(d["units"] for d in c) == 5

    limited_combos, _, limited_stats = backtracking_exact_units(
        [{"donor_id": donor_id, "name": f"D{donor_id}", "units": 1} for donor_id in range(1, 6)],
        target_units=2,
        max_combinations=3,
    )
    assert len(limited_combos) == 3
    assert limited_stats["search_limited"]

    print("[PASS] Greedy, Dynamic Programming, and Backtracking tests passed.")

if __name__ == "__main__":
    print("\n--- Running Blood Donation Management System DSA Verification ---")
    test_linked_list()
    test_queue_and_stack()
    test_bst()
    test_graph()
    test_searching_and_sorting()
    test_algorithms()
    print("\n[ALL TESTS PASSED SUCCESSFULLY!]")
