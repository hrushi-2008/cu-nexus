# CU NEXES

## Student Networking Platform

CU NEXES is a student networking web application developed using **Python and Streamlit**. It provides a platform where students can create profiles, connect with other students, search for users, share posts, send messages, and find potential project teammates.

The project focuses on applying **Data Structures and Algorithms (DSA)** to real-world student networking features.

## Features

- Student registration and login
- Student profiles with skills and interests
- Send and manage connection requests
- Student search
- Create and view posts
- Direct messaging
- Notifications
- Profile navigation history
- Shortest connection path between students
- Teammate recommendations based on friends and skills
- Chronological social feed

## Data Structures & Algorithms Used

| DSA Concept | Application |
|---|---|
| Hash Table | Fast student/user lookup |
| Graph | Represents student connections |
| Adjacency List | Stores connections efficiently |
| BFS | Finds shortest connection path |
| Trie | Prefix-based student and skill search |
| Queue | Connection requests, notifications and messages |
| Stack | Profile navigation history |
| Heap | Efficient feed generation |
| Jaccard Similarity | Teammate recommendation |
| K-Way Merge | Merging posts into a chronological feed |

## Technology Stack

- **Programming Language:** Python
- **Web Framework:** Streamlit
- **Data Storage:** JSON
- **DSA:** Graph, BFS, Trie, Queue, Stack, Heap, Hash Table
- **Algorithms:** BFS, Jaccard Similarity, K-Way Merge

## Project Structure

```text
CU-NEXES/
│
├── app.py
├── graph_engine.py
├── dsa_structures.py
├── storage.py
├── cu_network_data.json
└── README.md
```

### `app.py`

Main application file responsible for the Streamlit interface and user interactions.

### `graph_engine.py`

Handles student connections, graph operations, BFS shortest paths, recommendations, posts, messages and notifications.

### `dsa_structures.py`

Contains the Trie and heap/K-Way Merge implementations used for searching and feed generation.

### `storage.py`

Handles saving and loading application data using JSON files.

## How the DSA Works

### Graph + BFS

Students are represented as vertices and their connections as edges. BFS is used to find the shortest connection path between two students.

### Trie

A Trie is used for efficient prefix-based searching of student names, usernames and technical skills.

### Queue

A queue follows **FIFO (First In, First Out)** and is used for requests, notifications and messages.

### Stack

A stack follows **LIFO (Last In, First Out)** and is used to maintain profile navigation history.

### Hash Table

Python dictionaries provide fast key-based lookup of student information.

### Jaccard Similarity

Jaccard Similarity compares students using their common friends and technical skills.

The formula used is:

```text
J(A,B) = |A ∩ B| / |A ∪ B|
```

The recommendation score combines friend similarity and skill similarity:

```text
Final Score = 0.7 × Friend Similarity + 0.3 × Skill Similarity
```

### Heap + K-Way Merge

A heap is used to efficiently merge multiple sorted post lists and generate a newest-first feed.

## Installation

Clone the repository:

```bash
git clone <your-github-repository-url>
```

Go to the project folder:

```bash
cd CU-NEXES
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

The application will open in your browser.

## Project Objective

The main objective of CU NEXES is to demonstrate how Data Structures and Algorithms can be applied to a practical real-world application. Instead of using DSA only as theoretical concepts, the project integrates them into features such as networking, searching, recommendations, messaging and feed generation.

## Future Scope

- Integration with MySQL or SQLite
- Improved authentication and security
- Mobile-responsive interface
- Enhanced search functionality
- Improved recommendation algorithms
- Additional student collaboration features

## Conclusion

CU NEXES demonstrates the practical use of Data Structures and Algorithms in developing a student networking platform. By combining Python, Streamlit, JSON storage and multiple DSA techniques, the project provides useful networking features while demonstrating efficient data organization and processing.

## Team

Developed as a **DSA Mini Project**.
