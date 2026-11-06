"""
MODULE 2: Blood Request Processing, FIFO Queue & LIFO Operation Stack.
Implements custom Queue for request arrival processing and Stack for operation history.
"""
from datetime import datetime
from app import config, db

# ==============================================================================
# DATA STRUCTURE 1: FIFO QUEUE (FIRST-IN, FIRST-OUT)
# ==============================================================================

class QueueNode:
    """Represents a node in the linked FIFO Queue."""
    def __init__(self, data):
        self.data = data
        self.next = None

class BloodRequestQueue:
    """
    Linked FIFO Queue for processing blood requests in the exact order of their arrival.
    Demonstrates Enqueue, Dequeue, Peek, and Inspection.
    """
    def __init__(self):
        self.front = None
        self.rear = None
        self._count = 0

    def is_empty(self):
        """Checks if the queue is empty."""
        return self.front is None

    def size(self):
        """Returns the number of elements in the queue."""
        return self._count

    def enqueue(self, request_dict):
        """
        Adds a blood request to the rear of the queue.
        Time Complexity: O(1)
        """
        new_node = QueueNode(request_dict)
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self._count += 1

    def dequeue(self):
        """
        Removes and returns the blood request at the front of the queue.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        temp = self.front
        self.front = temp.next
        if self.front is None:
            self.rear = None
        self._count -= 1
        return temp.data

    def peek(self):
        """
        Returns the blood request at the front without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.front.data

    def to_list(self):
        """
        Returns all queued items in arrival order from front to rear.
        Time Complexity: O(n)
        """
        items = []
        curr = self.front
        while curr:
            items.append(curr.data)
            curr = curr.next
        return items


# ==============================================================================
# DATA STRUCTURE 2: LIFO STACK (LAST-IN, FIRST-OUT)
# ==============================================================================

class StackNode:
    """Represents a node in the LIFO Operation Stack."""
    def __init__(self, operation_dict):
        self.operation = operation_dict
        self.next = None

class OperationStack:
    """
    Linked LIFO Stack for tracking system operations and undo-style history.
    Demonstrates Push, Pop, Peek, and History Inspection.
    """
    def __init__(self, max_size=50):
        self.top = None
        self._count = 0
        self.max_size = max_size

    def is_empty(self):
        """Checks if the stack is empty."""
        return self.top is None

    def size(self):
        """Returns the total number of operations currently on the stack."""
        return self._count

    def push(self, operation_dict):
        """
        Pushes a new operation onto the top of the stack.
        Time Complexity: O(1)
        """
        new_node = StackNode(operation_dict)
        new_node.next = self.top
        self.top = new_node
        self._count += 1

    def pop(self):
        """
        Pops and returns the most recent operation from the top of the stack.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        popped = self.top
        self.top = self.top.next
        self._count -= 1
        return popped.operation

    def peek(self):
        """
        Returns the most recent operation without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.top.operation

    def to_list(self):
        """
        Returns all operations currently on the stack from newest to oldest.
        Time Complexity: O(n)
        """
        ops = []
        curr = self.top
        while curr:
            ops.append(curr.operation)
            curr = curr.next
        return ops


# In-memory global operation stack singleton
_GLOBAL_OPERATION_STACK = OperationStack()

def get_operation_stack():
    """Provides access to the global operation stack."""
    return _GLOBAL_OPERATION_STACK


# ==============================================================================
# BLOOD REQUEST CRUD & WORKFLOW OPERATIONS
# ==============================================================================

def get_all_hospitals():
    """Fetches all registered hospitals for request creation."""
    return db.fetch_all("SELECT hospital_id, hospital_name, city, phone FROM hospitals ORDER BY hospital_name ASC")

def get_all_requests():
    """
    Fetches all blood requests with hospital names.
    Returns: list of dicts
    """
    sql = """
        SELECT r.request_id, r.hospital_id, h.hospital_name, h.city as hospital_city,
               r.blood_group, r.units, r.urgency, r.status, r.requested_at
        FROM blood_requests r
        JOIN hospitals h ON r.hospital_id = h.hospital_id
        ORDER BY r.requested_at DESC
    """
    return db.fetch_all(sql)

def get_pending_request_queue():
    """
    Builds a FIFO Queue of all Pending blood requests ordered by requested_at ASC.
    Arrival order is strictly respected.
    """
    sql = """
        SELECT r.request_id, r.hospital_id, h.hospital_name, h.city as hospital_city,
               r.blood_group, r.units, r.urgency, r.status, r.requested_at
        FROM blood_requests r
        JOIN hospitals h ON r.hospital_id = h.hospital_id
        WHERE r.status = 'Pending'
        ORDER BY r.requested_at ASC
    """
    rows = db.fetch_all(sql)
    queue = BloodRequestQueue()
    for row in rows:
        queue.enqueue(row)
    return queue

def create_blood_request(hospital_id, blood_group, units, urgency="Normal"):
    """
    Creates a new blood request, stores in MySQL, and records operation in Stack.
    """
    if blood_group not in config.BLOOD_GROUPS:
        return False, f"Invalid blood group '{blood_group}'.", None

    try:
        units_int = int(units)
        if units_int <= 0:
            return False, "Units required must be greater than zero.", None
    except (ValueError, TypeError):
        return False, "Units required must be a valid positive integer.", None

    if urgency not in config.URGENCY_LEVELS:
        return False, f"Urgency must be one of: {', '.join(config.URGENCY_LEVELS)}", None

    sql = """
        INSERT INTO blood_requests (hospital_id, blood_group, units, urgency, status, requested_at)
        VALUES (%s, %s, %s, %s, 'Pending', NOW())
    """
    res = db.execute_query(sql, (hospital_id, blood_group, units_int, urgency))
    if res["success"]:
        req_id = res["lastrowid"]
        # Record operation on LIFO stack
        _GLOBAL_OPERATION_STACK.push({
            "action": "CREATE_REQUEST",
            "request_id": req_id,
            "details": f"Created Request #{req_id} ({units_int} units of {blood_group}, Urgency: {urgency})",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return True, f"Blood Request #{req_id} registered successfully!", req_id
    return False, f"Database error: {res['error']}", None

def process_next_pending_request():
    """
    Processes the next pending blood request from the FIFO Queue.
    Checks blood inventory:
    - If units are sufficient, deducts inventory and marks as Completed.
    - If insufficient, changes status to Processing and alerts user.
    """
    queue = get_pending_request_queue()
    if queue.is_empty():
        return False, "No pending blood requests in the FIFO queue.", None

    next_req = queue.dequeue()
    req_id = next_req["request_id"]
    blood_group = next_req["blood_group"]
    units_needed = next_req["units"]
    hosp_name = next_req["hospital_name"]

    # Check inventory
    inv_sql = "SELECT units FROM blood_inventory WHERE blood_group = %s"
    inv_row = db.fetch_one(inv_sql, (blood_group,))
    current_inventory = inv_row["units"] if inv_row else 0

    if current_inventory >= units_needed:
        # Sufficient inventory: Deduct units and mark request Completed
        new_units = current_inventory - units_needed
        db.execute_query("UPDATE blood_inventory SET units = %s WHERE blood_group = %s", (new_units, blood_group))
        db.execute_query("UPDATE blood_requests SET status = 'Completed' WHERE request_id = %s", (req_id,))

        _GLOBAL_OPERATION_STACK.push({
            "action": "PROCESS_REQUEST",
            "request_id": req_id,
            "details": f"Processed Request #{req_id} for {hosp_name}: Dispensed {units_needed} units of {blood_group}. (Remaining stock: {new_units})",
            "previous_status": "Pending",
            "new_status": "Completed",
            "units_deducted": units_needed,
            "blood_group": blood_group,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return True, f"Request #{req_id} for '{hosp_name}' successfully COMPLETED! {units_needed} units of {blood_group} dispensed from inventory (Remaining: {new_units}).", next_req
    else:
        # Insufficient inventory: Mark as Processing
        db.execute_query("UPDATE blood_requests SET status = 'Processing' WHERE request_id = %s", (req_id,))

        _GLOBAL_OPERATION_STACK.push({
            "action": "DEFER_REQUEST",
            "request_id": req_id,
            "details": f"Request #{req_id} status moved to Processing due to shortage (Needed: {units_needed}, Stock: {current_inventory})",
            "previous_status": "Pending",
            "new_status": "Processing",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return False, f"Insufficient inventory for Request #{req_id}! Required: {units_needed} units of {blood_group}, but only {current_inventory} available. Request marked as 'Processing'.", next_req

def update_request_status(request_id, new_status):
    """Updates the status of any blood request."""
    if new_status not in config.REQUEST_STATUSES:
        return False, f"Invalid status '{new_status}'."

    # Fetch old status
    old_row = db.fetch_one("SELECT status FROM blood_requests WHERE request_id = %s", (request_id,))
    if not old_row:
        return False, f"Request #{request_id} not found."

    old_status = old_row["status"]
    sql = "UPDATE blood_requests SET status = %s WHERE request_id = %s"
    res = db.execute_query(sql, (new_status, request_id))
    if res["success"]:
        _GLOBAL_OPERATION_STACK.push({
            "action": "UPDATE_STATUS",
            "request_id": request_id,
            "details": f"Changed Request #{request_id} status from '{old_status}' to '{new_status}'",
            "previous_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return True, f"Request #{request_id} status updated to '{new_status}'."
    return False, f"Database error: {res['error']}"

def undo_last_operation():
    """
    Pops the most recent operation from the LIFO Stack and attempts an undo.
    """
    if _GLOBAL_OPERATION_STACK.is_empty():
        return False, "No operations on the Stack to undo."

    last_op = _GLOBAL_OPERATION_STACK.pop()
    action = last_op.get("action")

    if action == "UPDATE_STATUS":
        req_id = last_op.get("request_id")
        prev_status = last_op.get("previous_status")
        db.execute_query("UPDATE blood_requests SET status = %s WHERE request_id = %s", (prev_status, req_id))
        return True, f"Undone: Restored Request #{req_id} status back to '{prev_status}'."

    elif action == "PROCESS_REQUEST":
        req_id = last_op.get("request_id")
        prev_status = last_op.get("previous_status")
        units = last_op.get("units_deducted")
        bg = last_op.get("blood_group")
        # Restore inventory
        db.execute_query("UPDATE blood_inventory SET units = units + %s WHERE blood_group = %s", (units, bg))
        db.execute_query("UPDATE blood_requests SET status = %s WHERE request_id = %s", (prev_status, req_id))
        return True, f"Undone: Reverted Request #{req_id} processing and restored {units} units of {bg} to inventory."

    elif action == "CREATE_REQUEST":
        req_id = last_op.get("request_id")
        db.execute_query("DELETE FROM blood_requests WHERE request_id = %s", (req_id,))
        return True, f"Undone: Deleted newly created Request #{req_id}."

    return True, f"Popped operation from stack: {last_op.get('details')}"
