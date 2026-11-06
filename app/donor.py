"""
MODULE 1: Donor Management & Singly Linked List Data Structure.
Implements a custom Linked List for donor records, with validation and CRUD operations.
"""
import re
from datetime import date
from app import config, db

# ==============================================================================
# DATA STRUCTURE: SINGLY LINKED LIST
# ==============================================================================

class DonorNode:
    """
    Represents an individual node in the Donor Linked List.
    Contains donor information and a pointer to the next node.
    """
    def __init__(self, donor_dict):
        self.donor_id = donor_dict.get("donor_id")
        self.name = donor_dict.get("name")
        self.age = donor_dict.get("age")
        self.gender = donor_dict.get("gender")
        self.blood_group = donor_dict.get("blood_group")
        self.phone = donor_dict.get("phone")
        self.email = donor_dict.get("email")
        self.city = donor_dict.get("city")
        self.available = bool(donor_dict.get("available"))
        self.last_donation_date = donor_dict.get("last_donation_date")
        self.next = None  # Pointer to next DonorNode

    def to_dict(self):
        """Converts node attributes to dictionary."""
        return {
            "donor_id": self.donor_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "blood_group": self.blood_group,
            "phone": self.phone,
            "email": self.email,
            "city": self.city,
            "available": 1 if self.available else 0,
            "last_donation_date": str(self.last_donation_date) if self.last_donation_date else None
        }


class DonorLinkedList:
    """
    Singly Linked List implementation for in-memory donor processing.
    Demonstrates practical operations: Insert, Traverse, Search, Delete, Filter.
    """
    def __init__(self):
        self.head = None
        self._size = 0

    def is_empty(self):
        """Checks if the linked list is empty."""
        return self.head is None

    def size(self):
        """Returns the total number of nodes in the linked list."""
        return self._size

    def insert_at_end(self, donor_dict):
        """
        Inserts a new donor node at the end of the linked list.
        Time Complexity: O(n)
        """
        new_node = DonorNode(donor_dict)
        if self.is_empty():
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1

    def insert_at_beginning(self, donor_dict):
        """
        Inserts a new donor node at the beginning (head) of the linked list.
        Time Complexity: O(1)
        """
        new_node = DonorNode(donor_dict)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def to_list(self):
        """
        Traverses the linked list from head to tail and returns records as a Python list.
        Time Complexity: O(n)
        """
        records = []
        current = self.head
        while current:
            records.append(current.to_dict())
            current = current.next
        return records

    def find_by_id(self, donor_id):
        """
        Searches for a donor by donor_id by traversing the linked list.
        Returns (node, steps_taken).
        Time Complexity: O(n)
        """
        current = self.head
        steps = 0
        while current:
            steps += 1
            if current.donor_id == donor_id:
                return current, steps
            current = current.next
        return None, steps

    def delete_by_id(self, donor_id):
        """
        Deletes a donor node matching donor_id by rearranging pointers.
        Returns (deleted_node, success).
        Time Complexity: O(n)
        """
        if self.is_empty():
            return None, False

        # Case 1: Head node is the target
        if self.head.donor_id == donor_id:
            deleted_node = self.head
            self.head = self.head.next
            self._size -= 1
            return deleted_node, True

        # Case 2: Node is in middle or end
        current = self.head
        while current.next and current.next.donor_id != donor_id:
            current = current.next

        if current.next and current.next.donor_id == donor_id:
            deleted_node = current.next
            current.next = current.next.next
            self._size -= 1
            return deleted_node, True

        return None, False

    def filter_available(self):
        """
        Traverses the linked list and returns a new DonorLinkedList containing only available donors.
        Time Complexity: O(n)
        """
        filtered_ll = DonorLinkedList()
        current = self.head
        while current:
            if current.available:
                filtered_ll.insert_at_end(current.to_dict())
            current = current.next
        return filtered_ll

    def filter_by_blood_group(self, blood_group):
        """
        Traverses the linked list and returns donors matching the blood group.
        Time Complexity: O(n)
        """
        results = []
        current = self.head
        while current:
            if current.blood_group == blood_group:
                results.append(current.to_dict())
            current = current.next
        return results

    def get_visual_chain(self, limit=8):
        """
        Returns a text-based ASCII representation of the linked list node chain.
        """
        nodes_repr = []
        current = self.head
        count = 0
        while current and count < limit:
            avail_symbol = "✓" if current.available else "✗"
            nodes_repr.append(f"[#{current.donor_id} {current.name} ({current.blood_group}) {avail_symbol}]")
            current = current.next
            count += 1
        if current:
            nodes_repr.append(f"... (+{self._size - limit} more nodes)")
        nodes_repr.append("NULL")
        return " ➔ ".join(nodes_repr)


# ==============================================================================
# INPUT VALIDATION
# ==============================================================================

def validate_donor(name, age, gender, blood_group, phone, email, city, last_donation_date=None, donor_id=None):
    """
    Validates all donor form fields against clinical and system rules.
    Returns: (is_valid: bool, errors: list[str])
    """
    errors = []

    # 1. Required fields
    if not name or not name.strip():
        errors.append("Donor Name is required.")
    elif len(name.strip()) < 3:
        errors.append("Donor Name must be at least 3 characters long.")

    # 2. Age validation
    try:
        age_int = int(age)
        if age_int < config.MIN_DONOR_AGE or age_int > config.MAX_DONOR_AGE:
            errors.append(f"Donor Age must be between {config.MIN_DONOR_AGE} and {config.MAX_DONOR_AGE} years.")
    except (ValueError, TypeError):
        errors.append("Valid Age is required (must be a number).")

    # 3. Gender validation
    if gender not in config.GENDERS:
        errors.append(f"Gender must be one of: {', '.join(config.GENDERS)}")

    # 4. Blood Group validation
    if blood_group not in config.BLOOD_GROUPS:
        errors.append(f"Blood Group must be one of: {', '.join(config.BLOOD_GROUPS)}")

    # 5. Phone validation (10 digits standard)
    clean_phone = re.sub(r'[\s\-\(\)\+]', '', str(phone or ''))
    if not clean_phone or len(clean_phone) < 10 or not clean_phone.isdigit():
        errors.append("Phone number must contain at least 10 valid digits.")

    # 6. Email validation
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not email or not re.match(email_regex, email.strip()):
        errors.append("A valid email address is required (e.g., donor@example.com).")

    # 7. City validation
    if not city or not city.strip():
        errors.append("City is required.")

    # 8. Uniqueness checks in database (Duplicate phone or email)
    if not errors:
        # Check duplicate phone
        phone_query = "SELECT donor_id FROM donors WHERE phone = %s"
        phone_params = [phone]
        if donor_id:
            phone_query += " AND donor_id != %s"
            phone_params.append(donor_id)
        existing_phone = db.fetch_one(phone_query, tuple(phone_params))
        if existing_phone:
            errors.append(f"A donor with phone number '{phone}' is already registered (Donor ID #{existing_phone['donor_id']}).")

        # Check duplicate email
        email_query = "SELECT donor_id FROM donors WHERE email = %s"
        email_params = [email]
        if donor_id:
            email_query += " AND donor_id != %s"
            email_params.append(donor_id)
        existing_email = db.fetch_one(email_query, tuple(email_params))
        if existing_email:
            errors.append(f"A donor with email '{email}' is already registered (Donor ID #{existing_email['donor_id']}).")

    return (len(errors) == 0), errors


# ==============================================================================
# DATABASE CRUD & LINKED LIST INTEGRATION
# ==============================================================================

def load_donors_to_linked_list():
    """
    Queries all donors from MySQL and builds an in-memory DonorLinkedList.
    Returns: DonorLinkedList instance
    """
    records = db.fetch_all("SELECT * FROM donors ORDER BY donor_id ASC")
    linked_list = DonorLinkedList()
    for row in records:
        linked_list.insert_at_end(row)
    return linked_list

def get_all_donors():
    """Returns list of all donor dictionaries via Linked List traversal."""
    ll = load_donors_to_linked_list()
    return ll.to_list()

def get_donor_by_id(donor_id):
    """Finds donor by ID using Linked List traversal."""
    ll = load_donors_to_linked_list()
    node, steps = ll.find_by_id(donor_id)
    if node:
        donor_dict = node.to_dict()
        donor_dict["search_steps"] = steps
        return donor_dict
    return None

def register_donor(name, age, gender, blood_group, phone, email, city, available=True, last_donation_date=None):
    """
    Registers a new donor: validates, saves to MySQL, and loads into Linked List.
    Returns: (success: bool, message: str, donor_id: int)
    """
    valid, errors = validate_donor(name, age, gender, blood_group, phone, email, city, last_donation_date)
    if not valid:
        return False, " | ".join(errors), None

    sql = """
        INSERT INTO donors (name, age, gender, blood_group, phone, email, city, available, last_donation_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        name.strip(),
        int(age),
        gender,
        blood_group,
        str(phone).strip(),
        email.strip().lower(),
        city.strip(),
        1 if available else 0,
        last_donation_date if last_donation_date else None
    )
    result = db.execute_query(sql, params)
    if result["success"]:
        return True, f"Donor '{name}' registered successfully with ID #{result['lastrowid']}!", result["lastrowid"]
    return False, f"Database error: {result['error']}", None

def update_donor(donor_id, name, age, gender, blood_group, phone, email, city, available, last_donation_date=None):
    """
    Updates an existing donor record in MySQL after validation.
    Returns: (success: bool, message: str)
    """
    valid, errors = validate_donor(name, age, gender, blood_group, phone, email, city, last_donation_date, donor_id=donor_id)
    if not valid:
        return False, " | ".join(errors)

    sql = """
        UPDATE donors 
        SET name = %s, age = %s, gender = %s, blood_group = %s, phone = %s, 
            email = %s, city = %s, available = %s, last_donation_date = %s
        WHERE donor_id = %s
    """
    params = (
        name.strip(),
        int(age),
        gender,
        blood_group,
        str(phone).strip(),
        email.strip().lower(),
        city.strip(),
        1 if available else 0,
        last_donation_date if last_donation_date else None,
        donor_id
    )
    result = db.execute_query(sql, params)
    if result["success"]:
        return True, f"Donor #{donor_id} updated successfully."
    return False, f"Database error: {result['error']}"

def delete_donor(donor_id):
    """
    Deletes a donor by ID from MySQL database.
    Returns: (success: bool, message: str)
    """
    # Also verify node exists in linked list
    ll = load_donors_to_linked_list()
    node, _ = ll.find_by_id(donor_id)
    if not node:
        return False, f"Donor #{donor_id} not found."

    sql = "DELETE FROM donors WHERE donor_id = %s"
    result = db.execute_query(sql, (donor_id,))
    if result["success"]:
        return True, f"Donor #{donor_id} ({node.name}) deleted successfully."
    return False, f"Database error: {result['error']}"

def toggle_availability(donor_id, new_status):
    """Toggles donor availability status."""
    sql = "UPDATE donors SET available = %s WHERE donor_id = %s"
    result = db.execute_query(sql, (1 if new_status else 0, donor_id))
    if result["success"]:
        status_text = "Available" if new_status else "Unavailable"
        return True, f"Donor #{donor_id} marked as {status_text}."
    return False, f"Database error: {result['error']}"
