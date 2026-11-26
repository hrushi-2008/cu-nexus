import json
import os
from collections import deque
from graph_engine import CampusNetwork, User

DATA_FILE = "cu_network_data.json"


def save_network(net: CampusNetwork):
    serialized_posts = {}
    for author, posts in net.user_posts.items():
        serialized_posts[author] = []
        for p in posts:
            p_copy = dict(p)
            p_copy["likes"] = list(p.get("likes", set()))
            p_copy["comments"] = list(p.get("comments", []))
            p_copy.setdefault("image_b64", None)
            serialized_posts[author].append(p_copy)

    serialized_dms = {
        f"{u1}|{u2}": list(msgs) for (u1, u2), msgs in net.direct_messages.items()
    }

    serialized_groups = {}
    for gid, g in net.groups.items():
        serialized_groups[gid] = {
            "id": g["id"],
            "name": g["name"],
            "topic": g["topic"],
            "creator": g["creator"],
            "members": list(g["members"]),
            "messages": list(g["messages"]),
        }

    data = {
        "users": {u: user.to_dict() for u, user in net.users.items()},
        "adj_list": {u: list(friends) for u, friends in net.adj_list.items()},
        "pending_incoming": {u: list(q) for u, q in net.pending_incoming.items()},
        "notifications": {u: list(q) for u, q in net.notifications.items()},
        "user_posts": serialized_posts,
        "direct_messages": serialized_dms,
        "groups": serialized_groups,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_network() -> CampusNetwork:
    net = CampusNetwork()
    if not os.path.exists(DATA_FILE):
        seed_demo_data(net)
        save_network(net)
        return net

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for u, u_data in data.get("users", {}).items():
        u_data.setdefault("is_admin", False)
        user = User(**u_data)
        net.users[u] = user
        net._index_user_tries(user)

    for u, friends in data.get("adj_list", {}).items():
        net.adj_list[u] = set(friends)

    for u, reqs in data.get("pending_incoming", {}).items():
        net.pending_incoming[u] = deque(reqs)

    saved_notifs = data.get("notifications", {})
    for u in net.users:
        net.notifications[u] = deque(saved_notifs.get(u, []))

    raw_posts = data.get("user_posts", {u: [] for u in net.users})
    for author, posts in raw_posts.items():
        for p in posts:
            p["likes"] = set(p.get("likes", []))
            p.setdefault("comments", [])
            p.setdefault("image_b64", None)
    net.user_posts = raw_posts

    for pair_key, msgs in data.get("direct_messages", {}).items():
        parts = pair_key.split("|")
        if len(parts) == 2:
            for idx, m in enumerate(msgs):
                m.setdefault("id", f"dm_legacy_{idx}")
            net.direct_messages[(parts[0], parts[1])] = deque(msgs)

    for gid, g in data.get("groups", {}).items():
        g_msgs = g.get("messages", [])
        for idx, m in enumerate(g_msgs):
            m.setdefault("id", f"gm_legacy_{idx}")
        net.groups[gid] = {
            "id": g["id"],
            "name": g["name"],
            "topic": g.get("topic", "General"),
            "creator": g["creator"],
            "members": set(g.get("members", [])),
            "messages": deque(g_msgs),
        }

    if "admin" not in net.users:
        net.signup(
            "admin",
            "admin123",
            "System Administrator",
            "Administration",
            0,
            "Platform Moderator",
            [],
            is_admin=True,
        )
        save_network(net)

    return net


def seed_demo_data(net: CampusNetwork):
    net.signup(
        "admin",
        "admin123",
        "System Administrator",
        "Administration",
        0,
        "Platform Moderator",
        [],
        is_admin=True,
    )
    demo_users = [
        ("aarav", "pass123", "Aarav Sharma", "B.Tech CSAI", 2, "Building graph engines & ML models.", ["Python", "PyTorch", "DSA"]),
        ("diya", "pass123", "Diya Nair", "B.Tech EVE", 2, "Interested in VLSI and embedded systems.", ["Verilog", "Arduino", "C++"]),
        ("rohan", "pass123", "Rohan Kulkarni", "B.Tech EECS", 2, "Robotics & IoT enthusiast.", ["Python", "Arduino", "MATLAB"]),
        ("ananya", "pass123", "Ananya Rao", "B.Tech CSAI", 3, "Full-stack dev & hackathon organizer.", ["Python", "React", "SQL"]),
        ("karthik", "pass123", "Karthik Menon", "B.Tech EVE", 2, "Digital electronics & PCB design.", ["MATLAB", "Verilog", "C++"]),
    ]
    for args in demo_users:
        net.signup(*args)

    edges = [("aarav", "diya"), ("diya", "rohan"), ("rohan", "ananya"), ("diya", "karthik")]
    for u, v in edges:
        net.adj_list[u].add(v)
        net.adj_list[v].add(u)

    net.create_post("diya", "Looking for a teammate with Python + Arduino skills for our IoT sensor prototype!", "#IoT #Hardware")
    net.create_post("aarav", "Just implemented a K-way merge feed using Python heapq. Super fast!", "#DSA #Python")
    net.send_direct_message("aarav", "diya", "Hey Diya! Saw your IoT post—would love to collaborate on the Python backend.")
    net.create_group("diya", "CU Robotics & IoT Club", "Hardware + Embedded Systems", ["aarav", "rohan"])