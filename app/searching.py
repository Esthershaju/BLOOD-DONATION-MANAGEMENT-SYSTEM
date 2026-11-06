"""
MODULE 5: Searching Algorithms - Linear Search and Binary Search.
Demonstrates manual implementations with step-by-step trace and complexity analysis.
"""

def linear_search(donors, search_field, target_value):
    """
    Manual Linear Search implementation.
    Searches sequentially through the donors list from index 0 to n-1.
    Time Complexity: O(n) worst/average, O(1) best.
    Space Complexity: O(1).
    
    Returns:
        matches: list of matching donor dicts
        step_logs: list of detailed step strings
        comparisons: int total comparisons made
    """
    matches = []
    step_logs = []
    comparisons = 0
    target_str = str(target_value).strip().lower()

    step_logs.append(f"Starting Linear Search for [{search_field} = '{target_value}'] across {len(donors)} records.")

    for idx, donor in enumerate(donors):
        comparisons += 1
        curr_val = str(donor.get(search_field, "")).strip()
        
        # Compare
        is_match = (curr_val.lower() == target_str)
        status_text = "MATCH FOUND! ✓" if is_match else "No match ✗"
        
        step_logs.append(
            f"Step {comparisons} (Index {idx}): Checking Donor #{donor.get('donor_id')} '{donor.get('name')}' "
            f"[{search_field}: '{curr_val}'] vs Target '{target_value}' ➔ {status_text}"
        )

        if is_match:
            matches.append(donor)

    step_logs.append(f"Linear Search complete: Found {len(matches)} matching record(s) in {comparisons} comparison(s).")
    return matches, step_logs, comparisons


def binary_search(sorted_donors, target_id):
    """
    Manual Binary Search implementation.
    Requires list of donors to be strictly sorted by 'donor_id'.
    Repeatedly halves the search space.
    Time Complexity: O(log n) worst/average, O(1) best.
    Space Complexity: O(1).

    Returns:
        matched_donor: dict or None
        step_logs: list of detailed step strings
        comparisons: int total iterations/comparisons
    """
    step_logs = []
    comparisons = 0
    low = 0
    high = len(sorted_donors) - 1

    try:
        target_int = int(target_id)
    except (ValueError, TypeError):
        return None, ["Invalid target ID: Must be an integer."], 0

    step_logs.append(f"Starting Binary Search for Donor ID #{target_int} in {len(sorted_donors)} sorted records.")

    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        mid_donor = sorted_donors[mid]
        mid_id = mid_donor.get("donor_id")

        step_logs.append(
            f"Iteration {comparisons}: Search window [Index {low} to {high}]. "
            f"Mid Index = {mid} (Donor #{mid_id}, '{mid_donor.get('name')}')."
        )

        if mid_id == target_int:
            step_logs.append(
                f"➔ TARGET FOUND at Index {mid}: Donor #{mid_id} '{mid_donor.get('name')}' "
                f"matches target in {comparisons} step(s)!"
            )
            return mid_donor, step_logs, comparisons

        elif target_int < mid_id:
            step_logs.append(f"  ↳ [{target_int} < {mid_id}] ➔ Discard right half. New High = {mid - 1}.")
            high = mid - 1
        else:
            step_logs.append(f"  ↳ [{target_int} > {mid_id}] ➔ Discard left half. New Low = {mid + 1}.")
            low = mid + 1

    step_logs.append(f"➔ TARGET NOT FOUND: Donor ID #{target_int} is not present. Search completed in {comparisons} iteration(s).")
    return None, step_logs, comparisons
