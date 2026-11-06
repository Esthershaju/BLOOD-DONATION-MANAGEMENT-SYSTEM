"""
MODULE 6: Algorithmic Problem Solving.
Implements:
1. Greedy Algorithm: Optimal Donor Matching for Blood Emergency.
2. Dynamic Programming: 0/1 Knapsack Request Urgency Optimization with full DP Table.
3. Backtracking: Exact Unit Combination Selection with Pruning.
"""
from datetime import datetime, date
from app import config

# ==============================================================================
# 1. GREEDY ALGORITHM: OPTIMAL DONOR MATCHING
# ==============================================================================

def greedy_donor_matching(donors_list, recipient_blood_group, units_needed=1):
    """
    Greedy Algorithm Demonstration:
    At each step, greedily selects the most suitable available donor.
    
    Greedy Criteria:
    1. Compatibility: Donor must be biologically compatible with recipient.
    2. Availability: Donor must be currently marked as Available (1).
    3. Exact Match Preference: Exact blood type match gets top priority (+50 pts).
    4. Readiness Score: Higher days since last donation gets preference (+days pts).
    
    Returns:
        selected_donors: list of selected donor dicts
        metrics: dict of selection statistics
        logs: step-by-step decision log
    """
    logs = []
    logs.append(f"Initiating Greedy Donor Selection for Recipient Blood Group: '{recipient_blood_group}' (Units needed: {units_needed}).")
    
    compatible_groups = config.BLOOD_COMPATIBILITY.get(recipient_blood_group, [recipient_blood_group])
    logs.append(f"Biologically Compatible Blood Groups: {', '.join(compatible_groups)}")

    # Filter eligible candidates
    eligible_candidates = []
    for d in donors_list:
        if not d.get("available"):
            continue
        if d.get("blood_group") not in compatible_groups:
            continue
            
        # Calculate greedy score
        score = 0
        # 1. Exact match bonus
        if d.get("blood_group") == recipient_blood_group:
            score += 50
        else:
            score += 20 # Compatible alternative (e.g. O- universal)
            
        # 2. Recency / Recovery bonus
        last_date = d.get("last_donation_date")
        days_since = 90 # default assumption if none recorded
        if last_date:
            try:
                if isinstance(last_date, str):
                    d_obj = datetime.strptime(last_date, "%Y-%m-%d").date()
                else:
                    d_obj = last_date
                days_since = max(0, (date.today() - d_obj).days)
            except Exception:
                days_since = 90
        score += min(days_since, 100) # Cap recovery bonus

        candidate = dict(d)
        candidate["greedy_score"] = score
        candidate["days_since_donation"] = days_since
        eligible_candidates.append(candidate)

    logs.append(f"Identified {len(eligible_candidates)} available & compatible candidate(s).")
    
    # Sort greedily by highest score (manual sorting or lambda for priority queue)
    # Using manual insertion sort by score descending:
    for i in range(1, len(eligible_candidates)):
        key_item = eligible_candidates[i]
        j = i - 1
        while j >= 0 and eligible_candidates[j]["greedy_score"] < key_item["greedy_score"]:
            eligible_candidates[j + 1] = eligible_candidates[j]
            j -= 1
        eligible_candidates[j + 1] = key_item

    # Greedily select top N candidates
    selected_donors = []
    for rank, candidate in enumerate(eligible_candidates, 1):
        if len(selected_donors) >= units_needed:
            break
        selected_donors.append(candidate)
        logs.append(
            f"Selection #{rank} [GREEDY CHOICE]: Picked Donor #{candidate['donor_id']} "
            f"'{candidate['name']}' ({candidate['blood_group']}) with Greedy Score: {candidate['greedy_score']} "
            f"(Match: {'Exact' if candidate['blood_group'] == recipient_blood_group else 'Universal/Compatible'}, "
            f"Days Rested: {candidate['days_since_donation']} days)."
        )

    if len(selected_donors) < units_needed:
        logs.append(f"Shortage Warning: Needed {units_needed} donors, but only found {len(selected_donors)} eligible donors.")

    metrics = {
        "needed": units_needed,
        "selected_count": len(selected_donors),
        "total_eligible": len(eligible_candidates),
        "fulfilled": len(selected_donors) >= units_needed
    }
    return selected_donors, metrics, logs


# ==============================================================================
# 2. DYNAMIC PROGRAMMING: 0/1 KNAPSACK BLOOD ALLOCATION
# ==============================================================================

def dp_blood_request_optimization(requests_list, blood_capacity):
    """
    Dynamic Programming Demonstration:
    0/1 Knapsack problem applied to emergency blood allocation.
    
    Problem Formulation:
    - Input: Available blood inventory units W (Capacity), and N pending requests.
             Each request i has weight w_i (units needed) and value v_i (urgency score).
    - Urgency Values: Critical = 10, Urgent = 5, Normal = 2.
    - State: dp[i][w] = Maximum urgency score achievable using a subset of the first i requests with capacity w.
    - Transition:
        If w_i > w:
            dp[i][w] = dp[i-1][w]   (Cannot include request i)
        Else:
            dp[i][w] = max(dp[i-1][w], dp[i-1][w - w_i] + v_i)  (Exclude vs Include)
    - Result: dp[N][W] contains the optimal max score. Backtracking yields selected requests.
    
    Returns:
        optimal_requests: list of selected request dicts
        max_score: int
        total_units_used: int
        dp_table: 2D list (matrix of size (N+1) x (W+1))
        logs: explanation and state transition logs
    """
    logs = []
    W = int(blood_capacity)
    items = []
    
    for r in requests_list:
        urgency = r.get("urgency", "Normal")
        score = config.URGENCY_WEIGHTS.get(urgency, 2)
        units = int(r.get("units", 1))
        items.append({
            "request_id": r.get("request_id"),
            "hospital_name": r.get("hospital_name", f"Hospital #{r.get('hospital_id', '')}"),
            "blood_group": r.get("blood_group"),
            "units": units,
            "urgency": urgency,
            "score": score
        })

    N = len(items)
    logs.append(f"DP Initialization: Blood Capacity = {W} units, Total Pending Requests = {N}.")
    
    # Initialize (N+1) x (W+1) table with 0
    dp = [[0 for _ in range(W + 1)] for _ in range(N + 1)]

    # Fill DP table iteratively
    for i in range(1, N + 1):
        curr_item = items[i - 1]
        w_i = curr_item["units"]
        v_i = curr_item["score"]
        
        for w in range(W + 1):
            if w_i > w:
                # Cannot include current item
                dp[i][w] = dp[i - 1][w]
            else:
                # Max of (Exclude, Include)
                exclude_val = dp[i - 1][w]
                include_val = dp[i - 1][w - w_i] + v_i
                dp[i][w] = max(exclude_val, include_val)

    max_score = dp[N][W]
    logs.append(f"DP Table computation completed. Maximum achievable Urgency Score = {max_score}.")

    # Backtracking to reconstruct the optimal set of requests
    selected_requests = []
    curr_w = W
    for i in range(N, 0, -1):
        if dp[i][curr_w] != dp[i - 1][curr_w]:
            # This item was included!
            chosen_item = items[i - 1]
            selected_requests.append(chosen_item)
            curr_w -= chosen_item["units"]
            logs.append(
                f"Backtrack Step: Included Request #{chosen_item['request_id']} "
                f"({chosen_item['hospital_name']}, {chosen_item['units']} units, "
                f"Urgency: {chosen_item['urgency']}, Score: {chosen_item['score']}). Remaining capacity: {curr_w}."
            )

    selected_requests.reverse()
    total_units_used = sum(r["units"] for r in selected_requests)

    return selected_requests, max_score, total_units_used, dp, items, logs


# ==============================================================================
# 3. BACKTRACKING: COMBINATION SELECTION FOR BLOOD REQUIREMENT
# ==============================================================================

def backtracking_exact_units(donors_with_units, target_units, max_combinations=None):
    """
    Backtracking Demonstration:
    Finds all unique combinations of donor blood unit pledges that sum exactly to target_units.
    
    Backtracking Mechanism:
    - Explores the state-space tree recursively.
    - Choice: Include or Exclude current donor's units.
    - Goal: When running_sum == target_units, capture valid subset combination.
    - Pruning / Bounding Condition: If running_sum > target_units, prune this branch immediately.
    - Backtrack: Undo the choice to explore alternative branches.
    
    Args:
        donors_with_units: list of dicts with 'name', 'units', 'donor_id'
        target_units: int target blood volume
        max_combinations: optional limit for the number of solutions to return
        
    Returns:
        all_combinations: list of valid donor combinations
        step_logs: detailed tree exploration log
        stats: execution metrics
    """
    target = int(target_units)
    all_combinations = []
    step_logs = []
    nodes_explored = [0]
    branches_pruned = [0]
    search_limited = [False]

    step_logs.append(f"Starting Backtracking Search to achieve EXACT target of {target} blood unit(s).")
    if max_combinations is not None and (
        isinstance(max_combinations, bool)
        or not isinstance(max_combinations, int)
        or max_combinations < 1
    ):
        raise ValueError("max_combinations must be a positive integer or None.")
    pledge_labels = [f"{d['name']} ({d['units']}u)" for d in donors_with_units]
    step_logs.append(f"Available Donor Pledges: {pledge_labels}")

    def backtrack(index, current_combo, current_sum):
        if search_limited[0]:
            return
        nodes_explored[0] += 1
        
        # 1. Base Goal Check
        if current_sum == target:
            all_combinations.append(list(current_combo))
            combo_names = " + ".join([f"{d['name']} ({d['units']}u)" for d in current_combo])
            step_logs.append(f"➔ [SOLUTION FOUND!]: [{combo_names}] = {target} units.")
            if max_combinations is not None and len(all_combinations) >= max_combinations:
                search_limited[0] = True
            return

        # 2. Pruning Condition (Bounding)
        if current_sum > target:
            branches_pruned[0] += 1
            step_logs.append(f"  ↳ [PRUNED]: Sum {current_sum} exceeds target {target}. Backtracking...")
            return

        # 3. End of items reached
        if index >= len(donors_with_units):
            return

        # Recursive Exploration:
        for i in range(index, len(donors_with_units)):
            donor = donors_with_units[i]
            
            # Action: Make decision (Include donor)
            current_combo.append(donor)
            step_logs.append(f"Depth {len(current_combo)}: Chose {donor['name']} ({donor['units']}u). Running sum: {current_sum + donor['units']}.")
            
            # Recurse with next index (each donor used at most once)
            backtrack(i + 1, current_combo, current_sum + donor["units"])
            
            # Backtrack: Undo decision
            popped = current_combo.pop()
            step_logs.append(f"  ↳ Backtracked: Removed {popped['name']}. Restored sum: {current_sum}.")

    backtrack(0, [], 0)

    stats = {
        "target": target,
        "total_combinations_found": len(all_combinations),
        "nodes_explored": nodes_explored[0],
        "branches_pruned": branches_pruned[0],
        "search_limited": search_limited[0]
    }
    step_logs.append(f"Backtracking completed: Explored {nodes_explored[0]} states, pruned {branches_pruned[0]} branches, found {len(all_combinations)} solution(s).")
    return all_combinations, step_logs, stats
