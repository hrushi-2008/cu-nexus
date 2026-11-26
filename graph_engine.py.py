import hashlib
import time
from collections import deque
from dsa_structures import PrefixTrie, merge_feed_k_way


class User:
    def __init__(
        self,
        username: str,
        password_hash: str,
        name: str,
        programme: str,
        year: int,
        bio: str,
        skills: list[str],
        is_admin: bool = False,
    ):
        self.username = username
        self.password_hash = password_hash
        self.name = name
        self.programme = programme
        self.year = year
        self.bio = bio
        self.skills = [s.strip() for s in skills if s.strip()]
        self.is_admin = is_admin

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "name": self.name,
            "programme": self.programme,
            "year": self.year,
            "bio": self.bio,
            "skills": self.skills,
            "is_admin": self.is_admin,
        }


class CampusNetwork:
    def __init__(self):
        # Hash Table for O(1) user lookups
        self.users: dict[str, User] = {}
        # Undirected Graph via Adjacency List: username -> set of connected usernames
        self.adj_list: dict[str, set[str]] = {}
        # Directed Pending Requests via FIFO Queues: receiver -> deque of senders
        self.pending_incoming: dict[str, deque[str]] = {}
        # Notifications Queue (FIFO) per user: username -> deque of notification strings
        self.notifications: dict[str, deque[str]] = {}
        # Posts stored per user in chronological order
        self.user_posts: dict[str, list[dict]] = {}
        # Direct Messages: sorted tuple (user_a, user_b) -> deque of message dicts
        self.direct_messages: dict[tuple[str, str], deque[dict]] = {}
        # Groups: group_id -> {id, name, topic, creator, members: set[str], messages: deque[dict]}
        self.groups: dict[str, dict] = {}
        # Prefix Trie for name/username search
        self.trie = PrefixTrie()
        # Prefix Trie for skill-based search
        self.skill_trie = PrefixTrie()
        # Navigation history Stack
        self.nav_stack: list[str] = []

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _index_user_tries(self, user: User):
        if user.is_admin:
            return
        self.trie.insert(user.username, user.username)
        for part in user.name.split():
            self.trie.insert(part, user.username)
        for skill in user.skills:
            self.skill_trie.insert(skill, user.username)

    def _remove_user_tries(self, user: User):
        self.trie.remove(user.username, user.username)
        for part in user.name.split():
            self.trie.remove(part, user.username)
        for skill in user.skills:
            self.skill_trie.remove(skill, user.username)

    # --- ACCOUNTS ---
    def signup(
        self,
        username: str,
        password: str,
        name: str,
        programme: str,
        year: int,
        bio: str,
        skills: list[str],
        is_admin: bool = False,
    ) -> tuple[bool, str]:
        username = username.strip().lower()
        if not username or " " in username or username in self.users:
            return False, "Username already exists or contains spaces."
        if not password or not name.strip():
            return False, "Name and password are required."

        user = User(
            username,
            self.hash_password(password),
            name.strip(),
            programme,
            year,
            bio.strip(),
            skills,
            is_admin,
        )
        self.users[username] = user
        self.adj_list[username] = set()
        self.pending_incoming[username] = deque()
        self.notifications[username] = deque()
        self.user_posts[username] = []
        self._index_user_tries(user)
        return True, "Account created successfully! Please sign in."

    def update_profile(
        self,
        username: str,
        name: str,
        programme: str,
        year: int,
        bio: str,
        skills: list[str],
    ) -> tuple[bool, str]:
        if username not in self.users:
            return False, "User not found."
        if not name.strip():
            return False, "Name cannot be empty."

        user = self.users[username]
        self._remove_user_tries(user)

        user.name = name.strip()
        user.programme = programme
        user.year = year
        user.bio = bio.strip()
        user.skills = [s.strip() for s in skills if s.strip()]

        self._index_user_tries(user)
        return True, "Profile updated successfully!"

    def login(self, username: str, password: str) -> bool:
        username = username.strip().lower()
        user = self.users.get(username)
        return bool(user and user.password_hash == self.hash_password(password))

    def delete_user_account(self, username: str) -> bool:
        if username not in self.users:
            return False
        user = self.users[username]
        self._remove_user_tries(user)

        for friend in list(self.adj_list.get(username, set())):
            self.adj_list[friend].discard(username)
        self.adj_list.pop(username, None)

        self.pending_incoming.pop(username, None)
        for other_u, q in self.pending_incoming.items():
            if username in q:
                q.remove(username)

        for gid in list(self.groups.keys()):
            self.groups[gid]["members"].discard(username)
            if not self.groups[gid]["members"]:
                self.groups.pop(gid, None)

        self.notifications.pop(username, None)
        self.user_posts.pop(username, None)
        self.users.pop(username, None)
        return True

    # --- NOTIFICATIONS (FIFO QUEUE) ---
    def add_notification(self, username: str, message: str):
        if username in self.notifications:
            stamp = time.strftime("%I:%M %p")
            self.notifications[username].append(f"[{stamp}] {message}")

    def get_notifications(self, username: str) -> list[str]:
        return list(self.notifications.get(username, deque()))

    def clear_notifications(self, username: str):
        if username in self.notifications:
            self.notifications[username].clear()

    # --- CONNECTIONS & REQUEST QUEUES ---
    def send_request(self, sender: str, receiver: str) -> tuple[bool, str]:
        if sender == receiver:
            return False, "Cannot connect to yourself (no self-loops)."
        if receiver not in self.users or self.users[receiver].is_admin:
            return False, "User does not exist."
        if receiver in self.adj_list[sender]:
            return False, "Already connected."
        if sender in self.pending_incoming[receiver]:
            return False, "Request already pending."
        if receiver in self.pending_incoming[sender]:
            return self.accept_request(sender, receiver)

        self.pending_incoming[receiver].append(sender)
        self.add_notification(receiver, f"@{sender} sent you a connection request.")
        return True, f"Request sent to {receiver}."

    def accept_request(self, receiver: str, sender: str) -> tuple[bool, str]:
        if sender not in self.pending_incoming[receiver]:
            return False, "No pending request from this user."
        self.pending_incoming[receiver].remove(sender)
        self.adj_list[receiver].add(sender)
        self.adj_list[sender].add(receiver)
        self.add_notification(sender, f"@{receiver} accepted your connection request.")
        return True, f"Connected with {sender}!"

    def reject_or_cancel_request(self, receiver: str, sender: str) -> bool:
        if sender in self.pending_incoming.get(receiver, deque()):
            self.pending_incoming[receiver].remove(sender)
            return True
        return False

    def remove_connection(self, user_a: str, user_b: str):
        self.adj_list[user_a].discard(user_b)
        self.adj_list[user_b].discard(user_a)

    # --- DIRECT MESSAGING (1-ON-1 CHAT + DELETE MESSAGE) ---
    @staticmethod
    def _dm_key(user_a: str, user_b: str) -> tuple[str, str]:
        return (user_a, user_b) if user_a < user_b else (user_b, user_a)

    def send_direct_message(self, sender: str, receiver: str, text: str) -> tuple[bool, str]:
        clean_text = text.strip()
        if not clean_text:
            return False, "Message cannot be empty."
        if receiver not in self.adj_list.get(sender, set()):
            return False, "You can only chat with connected peers."

        key = self._dm_key(sender, receiver)
        if key not in self.direct_messages:
            self.direct_messages[key] = deque()

        self.direct_messages[key].append({
            "id": f"dm_{sender}_{int(time.time() * 1000000)}",
            "sender": sender,
            "text": clean_text,
            "time_str": time.strftime("%d %b, %I:%M %p"),
        })
        self.add_notification(receiver, f"New message from @{sender}: \"{clean_text[:30]}\"")
        return True, "Sent"

    def delete_direct_message(self, user_a: str, user_b: str, msg_id: str, requester: str) -> bool:
        key = self._dm_key(user_a, user_b)
        q = self.direct_messages.get(key)
        if not q:
            return False
        original_len = len(q)
        self.direct_messages[key] = deque(
            m for m in q if not (m.get("id") == msg_id and m.get("sender") == requester)
        )
        return len(self.direct_messages[key]) < original_len

    def get_direct_messages(self, user_a: str, user_b: str) -> list[dict]:
        key = self._dm_key(user_a, user_b)
        return list(self.direct_messages.get(key, deque()))

    # --- GROUPS & GROUP CHAT (MIN 2 MEMBERS, ADD MEMBERS, DELETE MESSAGE) ---
    def create_group(self, creator: str, name: str, topic: str, initial_members: list[str]) -> tuple[bool, str]:
        clean_name = name.strip()
        if not clean_name:
            return False, "Group name is required."

        members_set = {creator}
        for m in initial_members:
            if m in self.users and not self.users[m].is_admin:
                members_set.add(m)

        if len(members_set) < 2:
            return False, "A group requires at least 2 members (select at least 1 other member)."

        group_id = f"grp_{int(time.time() * 1000)}"
        self.groups[group_id] = {
            "id": group_id,
            "name": clean_name,
            "topic": topic.strip() if topic.strip() else "General Campus Group",
            "creator": creator,
            "members": members_set,
            "messages": deque([
                {
                    "id": f"sys_{int(time.time() * 1000000)}",
                    "sender": "system",
                    "text": f"@{creator} created group '{clean_name}' with {len(members_set)} members.",
                    "time_str": time.strftime("%d %b, %I:%M %p"),
                }
            ]),
        }

        for m in members_set:
            if m != creator:
                self.add_notification(m, f"@{creator} added you to group '{clean_name}'.")
        return True, f"Group '{clean_name}' created!"

    def get_user_groups(self, username: str) -> list[dict]:
        return [g for g in self.groups.values() if username in g["members"]]

    def add_group_member(self, group_id: str, adder: str, new_member: str) -> tuple[bool, str]:
        group = self.groups.get(group_id)
        if not group or adder not in group["members"]:
            return False, "Group not found or access denied."
        if new_member not in self.users or self.users[new_member].is_admin:
            return False, "Invalid user."
        if new_member in group["members"]:
            return False, f"@{new_member} is already in this group."

        group["members"].add(new_member)
        group["messages"].append({
            "id": f"sys_{int(time.time() * 1000000)}",
            "sender": "system",
            "text": f"@{adder} added @{new_member} to the group.",
            "time_str": time.strftime("%d %b, %I:%M %p"),
        })
        self.add_notification(new_member, f"@{adder} added you to group '{group['name']}'.")
        return True, f"Added @{new_member}!"

    def leave_group(self, group_id: str, username: str) -> bool:
        group = self.groups.get(group_id)
        if not group or username not in group["members"]:
            return False
        group["members"].discard(username)
        if not group["members"]:
            self.groups.pop(group_id, None)
        else:
            group["messages"].append({
                "id": f"sys_{int(time.time() * 1000000)}",
                "sender": "system",
                "text": f"@{username} left the group.",
                "time_str": time.strftime("%d %b, %I:%M %p"),
            })
        return True

    def send_group_message(self, group_id: str, sender: str, text: str) -> tuple[bool, str]:
        clean_text = text.strip()
        group = self.groups.get(group_id)
        if not group or sender not in group["members"]:
            return False, "Not a member of this group."
        if not clean_text:
            return False, "Message cannot be empty."

        group["messages"].append({
            "id": f"gm_{sender}_{int(time.time() * 1000000)}",
            "sender": sender,
            "text": clean_text,
            "time_str": time.strftime("%d %b, %I:%M %p"),
        })
        return True, "Sent"

    def delete_group_message(self, group_id: str, msg_id: str, requester: str) -> bool:
        group = self.groups.get(group_id)
        if not group or requester not in group["members"]:
            return False
        q = group["messages"]
        original_len = len(q)
        group["messages"] = deque(
            m for m in q if not (m.get("id") == msg_id and m.get("sender") == requester)
        )
        return len(group["messages"]) < original_len

    # --- GRAPH ALGORITHMS ---
    def get_mutual_connections(self, user_a: str, user_b: str) -> list[str]:
        return sorted(list(self.adj_list[user_a].intersection(self.adj_list[user_b])))

    def find_shortest_path_bfs(self, start: str, target: str) -> tuple[int, list[str]]:
        if start == target:
            return 0, [start]
        visited = {start}
        queue = deque([(start, [start])])

        while queue:
            current, path = queue.popleft()
            for neighbor in self.adj_list[current]:
                if neighbor == target:
                    full_path = path + [neighbor]
                    return len(full_path) - 1, full_path
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return -1, []

    def recommend_teammates(self, username: str, top_k: int = 5) -> list[tuple[str, float, list[str]]]:
        my_friends = self.adj_list[username]
        my_skills = set(s.lower() for s in self.users[username].skills)
        scored_candidates = []

        for candidate, cand_user in self.users.items():
            if candidate == username or cand_user.is_admin or candidate in my_friends:
                continue

            cand_friends = self.adj_list[candidate]
            friend_union = my_friends.union(cand_friends)
            jaccard_friends = len(my_friends.intersection(cand_friends)) / len(friend_union) if friend_union else 0.0

            cand_skills = set(s.lower() for s in cand_user.skills)
            skill_union = my_skills.union(cand_skills)
            jaccard_skills = len(my_skills.intersection(cand_skills)) / len(skill_union) if skill_union else 0.0

            score = round((0.7 * jaccard_friends) + (0.3 * jaccard_skills), 3)
            shared_skills = sorted(list(my_skills.intersection(cand_skills)))
            scored_candidates.append((candidate, score, shared_skills))

        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[:top_k]

    # --- POSTS, PHOTO ATTACHMENTS, LIKES, COMMENTS & FEED ---
    def create_post(self, author: str, content: str, tags: str = "", image_b64: str | None = None):
        post = {
            "id": f"{author}_{int(time.time() * 1000)}",
            "author": author,
            "content": content.strip(),
            "tags": tags.strip(),
            "image_b64": image_b64,
            "timestamp": time.time(),
            "time_str": time.strftime("%d %b %Y, %I:%M %p"),
            "likes": set(),
            "comments": [],
        }
        self.user_posts[author].append(post)

    def delete_post(self, author: str, post_id: str):
        if author in self.user_posts:
            self.user_posts[author] = [p for p in self.user_posts[author] if p["id"] != post_id]

    def toggle_like(self, author: str, post_id: str, liker: str) -> bool:
        for post in self.user_posts.get(author, []):
            if post["id"] == post_id:
                likes_set = post.setdefault("likes", set())
                if liker in likes_set:
                    likes_set.remove(liker)
                else:
                    likes_set.add(liker)
                    if liker != author:
                        self.add_notification(author, f"@{liker} liked your post.")
                return True
        return False

    def add_comment(self, author: str, post_id: str, commenter: str, text: str) -> bool:
        clean_text = text.strip()
        if not clean_text:
            return False
        for post in self.user_posts.get(author, []):
            if post["id"] == post_id:
                post.setdefault("comments", []).append({
                    "author": commenter,
                    "text": clean_text,
                    "time_str": time.strftime("%d %b, %I:%M %p"),
                })
                if commenter != author:
                    self.add_notification(author, f"@{commenter} commented on your post: \"{clean_text[:30]}\"")
                return True
        return False

    def get_home_feed(self, username: str) -> list[dict]:
        relevant_users = self.adj_list[username].union({username})
        posts_map = {u: self.user_posts[u] for u in relevant_users}
        return merge_feed_k_way(posts_map)

    # --- SEARCH (BY NAME/USERNAME OR BY SKILL) ---
    def search_users(self, prefix: str) -> list[User]:
        if not prefix.strip():
            return []
        matched_usernames = self.trie.search_prefix(prefix.strip())
        return [self.users[u] for u in matched_usernames if u in self.users and not self.users[u].is_admin]

    def search_by_skill(self, skill_prefix: str) -> list[User]:
        if not skill_prefix.strip():
            return []
        matched_usernames = self.skill_trie.search_prefix(skill_prefix.strip())
        return [self.users[u] for u in matched_usernames if u in self.users and not self.users[u].is_admin]