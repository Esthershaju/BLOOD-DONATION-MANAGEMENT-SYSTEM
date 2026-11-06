"""
MODULE 5: Sorting Algorithm - Manual Insertion Sort.
Implements Insertion Sort for donor records by Name, Blood Group, City, or Donor ID.
"""

def insertion_sort(donors_list, sort_field="name", ascending=True):
    """
    Manual Insertion Sort implementation.
    Builds the sorted array one element at a time by repeatedly shifting larger
    elements to make room for the current key element.
    
    Time Complexity:
        Worst Case: O(n²) (Reverse sorted)
        Average Case: O(n²)
        Best Case: O(n) (Already sorted)
    Space Complexity: O(1) auxiliary (in-place on copy)
    
    Args:
        donors_list (list): List of donor dictionaries.
        sort_field (str): Field to sort by ('name', 'blood_group', 'city', 'donor_id').
        ascending (bool): True for ascending, False for descending.
        
    Returns:
        sorted_list: new sorted list of donor dictionaries
        metrics: dict with comparisons, shifts, passes, execution stats
        step_logs: list of step explanation strings
    """
    # Create a shallow copy to prevent mutating the original input list
    arr = [dict(d) for d in donors_list]
    n = len(arr)
    
    comparisons = 0
    shifts = 0
    step_logs = []
    
    step_logs.append(f"Starting Insertion Sort on {n} records by '{sort_field}' (Order: {'Ascending' if ascending else 'Descending'}).")
    
    for i in range(1, n):
        key_item = arr[i]
        key_val = key_item.get(sort_field)
        
        # Prepare value for comparison (case-insensitive for strings)
        key_comp = str(key_val).lower() if isinstance(key_val, str) else key_val
        
        j = i - 1
        pass_shifted = 0
        step_logs.append(f"Pass {i}: Key element is Donor #{key_item.get('donor_id')} ('{key_item.get(sort_field)}') at index {i}.")
        
        while j >= 0:
            comparisons += 1
            curr_val = arr[j].get(sort_field)
            curr_comp = str(curr_val).lower() if isinstance(curr_val, str) else curr_val
            
            # Comparison condition based on ascending/descending
            condition = (curr_comp > key_comp) if ascending else (curr_comp < key_comp)
            
            if condition:
                arr[j + 1] = arr[j]
                shifts += 1
                pass_shifted += 1
                j -= 1
            else:
                break
                
        arr[j + 1] = key_item
        if pass_shifted > 0:
            step_logs.append(f"  ↳ Shifted {pass_shifted} element(s) right. Inserted key at index {j + 1}.")
        else:
            step_logs.append(f"  ↳ Key already in correct relative position at index {j + 1} (No shifts).")

    metrics = {
        "total_records": n,
        "total_comparisons": comparisons,
        "total_shifts": shifts,
        "sort_field": sort_field,
        "order": "Ascending" if ascending else "Descending"
    }
    
    step_logs.append(f"Insertion Sort Completed: {comparisons} comparisons, {shifts} shifts.")
    return arr, metrics, step_logs
