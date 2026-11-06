# 🩸 Blood Donation Management System (BDMS)
### College Data Structures & Algorithmic Problem Solving Mini-Project

A comprehensive, full-stack responsive web application built with **Python**, **Streamlit**, and **MySQL** (`mysql-connector-python`). It supports desktop and mobile browsers and is engineered for computer science and software engineering academic evaluation, bridging practical healthcare blood bank operations with concrete implementations of classical **Data Structures and Algorithmic Problem Solving techniques**.

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Technology Stack](#-technology-stack)
3. [Architecture & Project Structure](#-architecture--project-structure)
4. [Data Structures & Algorithms Mapping](#-data-structures--algorithms-mapping)
5. [Database Schema & Entity Relationships](#-database-schema--entity-relationships)
6. [Prerequisites & System Requirements](#-prerequisites--system-requirements)
7. [Installation & Setup Instructions](#-installation--setup-instructions)
8. [MySQL Database Setup](#-mysql-database-setup)
9. [Running the Streamlit Application](#-running-the-streamlit-application)
10. [Demo Login Credentials](#-demo-login-credentials)
11. [Module Walkthrough](#-module-walkthrough)
12. [College Viva Examination Guide & FAQs](#-college-viva-examination-guide--faqs)

---

## 🎯 Project Purpose

In healthcare logistics, blood banking is a life-critical domain where timing, donor matching, FIFO triage, and inventory management determine patient survival. This project demonstrates how core Computer Science fundamentals—such as **Linked Lists**, **Queues**, **Stacks**, **Binary Search Trees (BST)**, **Graphs**, **Linear/Binary Search**, **Insertion Sort**, **Greedy Algorithms**, **Dynamic Programming**, and **Backtracking**—can be applied to solve real-world problems in blood donation and hospital distribution.

---

## 💻 Technology Stack

* **Frontend Framework:** [Python Streamlit](https://streamlit.io/) (Fast, reactive Python web UI)
* **Backend Logic:** Python 3.10+ (Standard Library, Data Structures, OOP)
* **Database Engine:** MySQL Server 8.0+
* **Database Driver:** `mysql-connector-python`
* **Graph Visualization:** Built-in Graphviz rendering (`st.graphviz_chart`)
* **Operating System:** Fully optimized for Windows 10/11 (PowerShell & Command Prompt)

> ⚠️ **Strict Academic Requirement:** Does NOT use React, Node.js, PHP, Java, or MongoDB. 100% pure Python and MySQL.

---

## 📁 Architecture & Project Structure

```
BLOOD DONATION MANAGEMENT SYSTEM/
│
├── app/
│   ├── __init__.py         # Package initialisation
│   ├── config.py           # App credentials, DB settings, clinical constants
│   ├── db.py               # MySQL connection layer, CRUD helpers, schema loader
│   ├── donor.py            # MODULE 1: Singly Linked List & Donor Management
│   ├── requests.py         # MODULE 2: FIFO Queue & LIFO Operation Stack
│   ├── tree.py             # MODULE 3: Binary Search Tree (BST) & Tree Traversals
│   ├── graph.py            # MODULE 4: Hospital Transit Graph & BFS / DFS
│   ├── searching.py        # MODULE 5: Manual Linear Search & Binary Search
│   ├── sorting.py          # MODULE 5: Manual Insertion Sort
│   ├── algorithms.py       # MODULE 6: Greedy, 0/1 Knapsack DP, Backtracking
│   └── main.py             # Main Streamlit web application & navigation
│
├── database/
│   └── schema.sql          # MySQL DDL definitions, tables, constraints, seed data
│
├── tests/
│   └── test_dsa.py         # Automated unit test suite verifying all 10 DSA modules
│
├── setup_db.py             # One-click CLI script to initialize MySQL database
├── requirements.txt        # Python package dependencies
└── README.md               # Detailed documentation & Viva preparation guide
```

---

## 🧠 Data Structures & Algorithms Mapping

| Academic Topic | Implemented Module | Concrete Real-World Application in BDMS | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Singly Linked List** | `app/donor.py` | Dynamic in-memory donor chain; constant-time insertion at head; pointer-based node deletion without shifting arrays. | Insert: $O(1)$<br>Search: $O(n)$<br>Delete: $O(n)$ | $O(n)$ |
| **FIFO Queue** | `app/requests.py` | Ethical emergency request triage: blood requests are strictly fulfilled in the exact order of their arrival. | Enqueue: $O(1)$<br>Dequeue: $O(1)$ | $O(n)$ |
| **LIFO Stack** | `app/requests.py` | Administrative undo history and clinical audit trail; pushes every mutation and pops to roll back status or inventory. | Push: $O(1)$<br>Pop: $O(1)$ | $O(n)$ |
| **Binary Search Tree (BST)** | `app/tree.py` | Fast logarithmic donor lookup using numeric `donor_id` key; visualizes Inorder, Preorder, and Postorder traversals. | Search: $O(\log n)$ avg<br>Insert: $O(\log n)$ avg<br>Traversals: $O(n)$ | $O(n)$ |
| **Graph (Adjacency List)** | `app/graph.py` | Regional hospital transit network connecting medical hubs with weighted road distances (km). | Add Edge: $O(1)$<br>Storage: $O(V + E)$ | $O(V + E)$ |
| **Breadth-First Search (BFS)** | `app/graph.py` | Layer-by-layer exploration using a FIFO queue to identify the nearest regional blood supply centers. | $O(V + E)$ | $O(V)$ |
| **Depth-First Search (DFS)** | `app/graph.py` | Deep branch exploration using Recursion/Stack to inspect emergency supply route corridors and connectivity. | $O(V + E)$ | $O(V)$ |
| **Linear Search** | `app/searching.py` | Sequential scanning of unsorted donor registries by Blood Group, City, or Name with step tracking. | Best: $O(1)$<br>Worst/Avg: $O(n)$ | $O(1)$ |
| **Binary Search** | `app/searching.py` | Divide-and-conquer search on sorted donor IDs, halving search space each step with detailed `[low, mid, high]` window. | Best: $O(1)$<br>Worst/Avg: $O(\log n)$ | $O(1)$ |
| **Insertion Sort** | `app/sorting.py` | Manual sorting of donors by Name, Blood Group, City, or Donor ID with comparison and shift metrics. | Best: $O(n)$<br>Worst/Avg: $O(n^2)$ | $O(1)$ |
| **Greedy Algorithm** | `app/algorithms.py` | Emergency compatible donor selection optimizing compatibility (exact match vs universal O-), availability, and rest period. | $O(n \log n)$ | $O(n)$ |
| **Dynamic Programming** | `app/algorithms.py` | 0/1 Knapsack optimization to maximize total urgency score (Critical=10, Urgent=5, Normal=2) within blood inventory capacity $W$. | $O(N \times W)$ | $O(N \times W)$ |
| **Backtracking** | `app/algorithms.py` | State-space tree exploration with pruning (bounding) to find all combinations of donor unit pledges summing to exact target. | $O(2^n)$ pruned | $O(n)$ |

---

## 🗄️ Database Schema & Entity Relationships

The MySQL database is named **`blood_donation_db`** and conforms to 3NF (Third Normal Form) with strict primary and foreign key constraints:

### 1. `donors` Table
Stores donor clinical profiles and availability flags.
* `donor_id`: INT AUTO_INCREMENT **(PRIMARY KEY)**
* `name`: VARCHAR(100) NOT NULL
* `age`: INT NOT NULL (Validated 18–65)
* `gender`: VARCHAR(10) NOT NULL
* `blood_group`: VARCHAR(5) NOT NULL (A+, A-, B+, B-, AB+, AB-, O+, O-)
* `phone`: VARCHAR(20) NOT NULL **(UNIQUE)**
* `email`: VARCHAR(100) NOT NULL
* `city`: VARCHAR(50) NOT NULL
* `available`: BOOLEAN DEFAULT TRUE
* `last_donation_date`: DATE NULL

### 2. `hospitals` Table
Stores accredited healthcare centers and blood reception hubs.
* `hospital_id`: INT AUTO_INCREMENT **(PRIMARY KEY)**
* `hospital_name`: VARCHAR(150) NOT NULL
* `city`: VARCHAR(50) NOT NULL
* `phone`: VARCHAR(20) NOT NULL

### 3. `blood_requests` Table
Tracks patient blood requirements submitted by hospitals.
* `request_id`: INT AUTO_INCREMENT **(PRIMARY KEY)**
* `hospital_id`: INT NOT NULL **(FOREIGN KEY $\to$ `hospitals.hospital_id` ON DELETE CASCADE)**
* `blood_group`: VARCHAR(5) NOT NULL
* `units`: INT NOT NULL ($> 0$)
* `urgency`: ENUM('Normal', 'Urgent', 'Critical') DEFAULT 'Normal'
* `status`: ENUM('Pending', 'Processing', 'Completed', 'Cancelled') DEFAULT 'Pending'
* `requested_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### 4. `blood_inventory` Table
Maintains real-time blood stock counts per group.
* `inventory_id`: INT AUTO_INCREMENT **(PRIMARY KEY)**
* `blood_group`: VARCHAR(5) NOT NULL **(UNIQUE)**
* `units`: INT NOT NULL DEFAULT 0
* `updated_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

---

## ⚙️ Prerequisites & System Requirements

1. **Python 3.10, 3.11, or 3.12** installed and added to PATH.
2. **MySQL Server 8.0+** installed and running (e.g. MySQL Community Server or XAMPP).
3. **VS Code** (Visual Studio Code) on Windows.

---

## 🚀 Installation & Setup Instructions

### Step 1: Open Project in VS Code
Open VS Code, press `Ctrl + O` or choose **File > Open Folder...**, and select:
```
c:\Users\Asus\OneDrive\Documents\BLOOD DONATION MANAGEMENT SYSTEM
```

### Step 2: Open PowerShell Terminal in VS Code
Press `` Ctrl + ` `` to open the integrated terminal.

### Step 3: Install Required Dependencies
Run the following command to install Streamlit, MySQL Connector, and Graphviz:
```powershell
pip install -r requirements.txt
```

---

## 🗄️ MySQL Database Setup

You have two simple ways to set up and initialize the MySQL database:

### Option A: Using the One-Click CLI Script (Recommended)
Run the automated helper script in your terminal:
```powershell
python setup_db.py
```
* It will ask for your MySQL Host (default `localhost`), Port (default `3306`), User (default `root`), and Password.
* It will automatically create `blood_donation_db`, execute `database/schema.sql`, create all tables with constraints, and populate realistic seed data!

### Option B: Directly from the Streamlit UI
If you launch Streamlit without running the CLI script:
1. Open the sidebar in the app.
2. Under **⚙️ Configure MySQL Credentials**, enter your MySQL root password.
3. Click **Connect & Initialize Database**. The database will be created and populated instantly!

### Option C: Manual MySQL CLI Execution
You can also run the schema file directly via the MySQL command line:
```powershell
mysql -u root -p < database/schema.sql
```

---

## 🖥️ Running the Streamlit Application

Execute the following command in the VS Code terminal:
```powershell
streamlit run app/main.py
```
Your default web browser will automatically open:
```
Local URL: http://localhost:8501
```

### Mobile browser access

The Streamlit interface adapts to phone-sized screens. To open it on a phone connected to the same Wi-Fi network as the computer running the app, start Streamlit so it listens on the network:

```powershell
streamlit run app/main.py --server.address 0.0.0.0
```

Then open `http://<computer-local-IP>:8501` in the phone's browser. Allow Streamlit through the computer's firewall if prompted. This provides a mobile-friendly web app; it does not install as a native Android or iOS app.

---

## 🔐 Demo Login Credentials

On first launch, you will be greeted by the secure login screen:

* **Username:** `admin`
* **Password:** `admin123`

*(These can be customized in `app/config.py` or via environment variables).*

---

## 📦 Module Walkthrough

### 1. 📊 Dashboard
* **KPI Metrics:** Real-time counters for Total Donors, Available Donors, Partner Hospitals, Pending Requests, and Total Blood Stock.
* **Inventory Overview:** Visual stock badges for all 8 blood groups with color-coded deficit warnings (Green $\ge 10$, Amber $5-9$, Red $< 5$).
* **Pending Queue Snapshot:** Front element of the FIFO blood request queue.
* **LIFO Operation Stack:** Recent operations list with a single-click **Undo** button.

### 2. 👥 Donor Management (Linked List)
* **Live Node Chain:** Displays the in-memory ASCII pointer sequence:
  `[Head: #1 Aarav (O+)] ➔ [#2 Priya (A+)] ➔ ... ➔ [NULL]`
* **Register Donor:** Form with clinical validation:
  * Name $\ge 3$ characters
  * Age between 18 and 65
  * Valid 10-digit phone with duplicate check
  * Valid email regex with duplicate check
  * Clinical blood group selector
* **Filter Donors:** Traverse the linked list filtering by availability or blood group.
* **Update & Delete:** Modify donor details or unlink and delete nodes in $O(n)$ time.

### 3. 🌳 Hierarchical Data & BST (MODULE 3)
* **Binary Search Tree:** Built using numeric `donor_id` as keys.
* **Visual Topology:** Graphviz rendering of the binary search tree layout.
* **Logarithmic Search:** Search for any `donor_id` and view the exact branch decision path (e.g. `[7 > 4] ➔ Move Right`).
* **Traversals:**
  * **Inorder (Left $\to$ Root $\to$ Right):** Produces strictly ascending order of Donor IDs.
  * **Preorder (Root $\to$ Left $\to$ Right):** Useful for tree cloning/serialization.
  * **Postorder (Left $\to$ Right $\to$ Root):** Useful for bottom-up memory deallocation.
* **Interactive Insertion:** Add new nodes and watch the BST dynamically rebalance its branches.

### 4. 🩸 Blood Requests (FIFO Queue & LIFO Stack)
* **Create Request:** Select hospital, blood group, units, and urgency level (Normal, Urgent, Critical). The form displays a clear success confirmation or submission error after you submit.
* **FIFO Processing Queue:** Dequeues the oldest pending request from the front. If sufficient inventory exists, it deducts units from `blood_inventory` and marks the request as `Completed`. If stock is low, it updates the status to `Processing` and warns the administrator.
* **Priority Triage:** Instantly filters active Critical and Urgent emergencies.
* **Undo via LIFO Stack:** Reverts the last status transition and restores deducted inventory.

### 5. 🏥 Blood Availability & Inventory Control
* Interactive stock cards for all 8 blood groups.
* Direct restocking and manual volume overrides with audit logging.

### 6. 🌐 Hospitals & Graph (BFS / DFS)
* **Adjacency List:** Represents connected hospitals with edge weights (distances in km).
* **Network Visualization:** Interactive Graphviz diagram of medical distribution centers.
* **Breadth-First Search (BFS):** Layer-by-layer exploration starting from any selected hospital using a FIFO queue.
* **Depth-First Search (DFS):** Deep branch exploration using Recursion / Stack.
* **Route Creator:** Add custom transit corridors between hospitals.

### 7. 🔍 Searching & Sorting
* **Linear Search:** Sequential scanning by Blood Group, City, or Name with step-by-step comparison logs.
* **Binary Search:** Divide-and-conquer on sorted donor records by Donor ID, showing `low`, `mid`, and `high` window indices.
* **Insertion Sort:** Manual implementation sorting by Name, Blood Group, City, or Donor ID with comparison and shift metrics.

### 8. 🧠 Algorithmic Problem Solving
* **Greedy Algorithm:** Emergency donor selection considering biological compatibility, availability, and recency of donation.
* **Backtracking:** Exact unit-combination logic is retained in `app/algorithms.py` and covered by automated tests; it is not exposed in the donor-matching interface.
* **Dynamic Programming (0/1 Knapsack):** The algorithm remains available in `app/algorithms.py` and is covered by automated tests; request planning is not part of the donor-matching screen.

---

## 🧪 Automated Testing

To verify all 10 Data Structures and Algorithms without launching the UI, run the automated test suite:
```powershell
python tests/test_dsa.py
```
Expected output:
```
--- Running Blood Donation Management System DSA Verification ---
[PASS] Linked List tests passed.
[PASS] FIFO Queue tests passed.
[PASS] LIFO Stack tests passed.
[PASS] BST tests passed.
[PASS] Graph BFS/DFS tests passed.
[PASS] Searching & Sorting tests passed.
[PASS] Greedy, Dynamic Programming, and Backtracking tests passed.

[ALL TESTS PASSED SUCCESSFULLY!]
```

---

## 🎓 College Viva Examination Guide & FAQs

### Q1: Why use a custom Linked List instead of Python's built-in list for donor records?
> **Answer:** Python lists are implemented internally as dynamic arrays. Appending to a full dynamic array requires allocating a new memory block and copying all elements, incurring occasional $O(n)$ reallocations. A Linked List uses individual nodes with pointers, offering true $O(1)$ insertion at the head and dynamic, non-contiguous memory growth without reallocation overhead.

### Q2: Why is a FIFO Queue critical for blood requests?
> **Answer:** In hospital blood banking, blood requests must be triaged ethically and chronologically based on arrival time. A FIFO (First-In, First-Out) Queue guarantees that earlier requests are not starved by subsequent arrivals, maintaining strict medical fairness.

### Q3: How does Binary Search achieve $O(\log n)$ time complexity?
> **Answer:** Binary Search requires the array to be sorted. At each comparison step, it checks the middle element and discards half of the remaining search space. For $n$ elements, the search space reduces as $n, n/2, n/4, \dots, 1$. Setting $n / 2^k = 1$ gives $k = \log_2 n$ comparisons.

### Q4: Why does Inorder Traversal of a BST always yield sorted keys?
> **Answer:** By the BST definition, for any node with key $K$, all nodes in its left subtree have keys $< K$, and all nodes in its right subtree have keys $> K$. Since Inorder traversal recursively visits **Left Subtree $\to$ Root $\to$ Right Subtree**, it visits elements in strictly increasing order.

### Q5: What is the difference between BFS and DFS in hospital routing?
> **Answer:** 
> * **BFS (Breadth-First Search)** explores vertices layer-by-layer using a **FIFO Queue**. It is optimal for finding the shortest transit path (fewest hops) to the nearest blood bank.
> * **DFS (Depth-First Search)** explores as deep as possible along each path using a **LIFO Stack / Recursion**. It is used for cycle detection, full connectivity analysis, and topological sorting.

### Q6: What is the difference between Greedy and Dynamic Programming?
> **Answer:**
> * **Greedy:** Makes the locally optimal choice at each step without backtracking or reconsidering past decisions. It is faster ($O(n \log n)$), but only works when the problem satisfies the greedy choice property.
> * **Dynamic Programming:** Solves subproblems, memoizes their solutions in a table (`dp[i][w]`), and evaluates overlapping subproblems to guarantee a globally optimal solution even when local decisions conflict.

### Q7: How does Backtracking avoid brute-force exponential blowup?
> **Answer:** Brute-force generates all $2^n$ possible subsets. Backtracking employs a **bounding condition (pruning)**: if the running sum of blood units exceeds the target, it immediately terminates exploration of that entire subtree and steps back, discarding invalid branches without exploring them.

---

## 👨‍💻 Project Authors & Academic Submission

* **Project Title:** Blood Donation Management System (BDMS)
* **Domain:** Healthcare Data Management & Algorithmic Problem Solving
* **Core Technologies:** Python Streamlit, MySQL, mysql-connector-python
* **Version:** 1.0.0
