import heapq


class TrieNode:
    def __init__(self):
        self.children = {}
        # Store matching usernames directly at prefix nodes for O(L) retrieval
        self.usernames = set()


class PrefixTrie:
    """Trie for instant O(L) prefix autocomplete on names, usernames, and skills."""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, text: str, username: str):
        node = self.root
        for char in text.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.usernames.add(username)

    def remove(self, text: str, username: str):
        node = self.root
        for char in text.lower():
            if char not in node.children:
                return
            node = node.children[char]
            node.usernames.discard(username)

    def search_prefix(self, prefix: str) -> list[str]:
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return sorted(list(node.usernames))


def merge_feed_k_way(posts_by_user: dict[str, list[dict]], limit: int = 20) -> list[dict]:
    """
    Merges sorted post lists from 1st-degree connections using a Max-Heap.
    Python's heapq is a min-heap, so timestamps are negated for newest-first order.
    Time Complexity: O(N log K), where K is the number of connections.
    """
    max_heap = []
    for username, posts in posts_by_user.items():
        if posts:
            last_idx = len(posts) - 1
            newest_post = posts[last_idx]
            heapq.heappush(
                max_heap,
                (-newest_post["timestamp"], newest_post["id"], username, last_idx, newest_post)
            )

    feed = []
    while max_heap and len(feed) < limit:
        neg_ts, post_id, username, idx, post = heapq.heappop(max_heap)
        feed.append(post)
        if idx - 1 >= 0:
            next_post = posts_by_user[username][idx - 1]
            heapq.heappush(
                max_heap,
                (-next_post["timestamp"], next_post["id"], username, idx - 1, next_post)
            )

    return feed