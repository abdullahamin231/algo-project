import json
import time
import math


class Post:
    def __init__(self, postid, timestamp, score):
        self.postid = postid
        self.timestamp = timestamp
        self.score = score

    def __repr__(self):
        return "Post(id={}, ts={}, score={})".format(
            self.postid, self.timestamp, self.score
        )


# =========================
# BST IMPLEMENTATION
# =========================

class BSTNode:
    def __init__(self, post):
        self.post = post
        self.key = (post.timestamp, post.postid)
        self.left = None
        self.right = None
        self.parent = None


class BSTFeed:
    def __init__(self):
        self.root = None
        self.id_to_node = {}
        self.size = 0
        self.stats = {
            "insert_count": 0,
            "insert_time_total": 0.0,
            "delete_count": 0,
            "delete_time_total": 0.0,
            "like_count": 0,
            "like_time_total": 0.0,
            "get_popular_count": 0,
            "get_popular_time_total": 0.0,
        }

    # ---- Public API ----

    def addPost(self, postid, timestamp, score):
        start = time.perf_counter()
        post = Post(postid, timestamp, score)
        node = BSTNode(post)

        if self.root is None:
            self.root = node
        else:
            self._insert_node(self.root, node)

        self.id_to_node[postid] = node
        self.size += 1

        end = time.perf_counter()
        self.stats["insert_count"] += 1
        self.stats["insert_time_total"] += (end - start)

    def likePost(self, postid):
        start = time.perf_counter()
        node = self.id_to_node.get(postid)
        if node is not None:
            node.post.score += 1
        end = time.perf_counter()
        self.stats["like_count"] += 1
        self.stats["like_time_total"] += (end - start)

    def deletePost(self, postid):
        start = time.perf_counter()
        node = self.id_to_node.get(postid)
        if node is not None:
            self._delete_node(node)
            del self.id_to_node[postid]
            self.size -= 1
        end = time.perf_counter()
        self.stats["delete_count"] += 1
        self.stats["delete_time_total"] += (end - start)

    def getMostPopular(self):
        start = time.perf_counter()
        best_post = None
        best_score = None

        stack = []
        node = self.root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            if best_post is None or node.post.score > best_score:
                best_post = node.post
                best_score = node.post.score
            node = node.right

        end = time.perf_counter()
        self.stats["get_popular_count"] += 1
        self.stats["get_popular_time_total"] += (end - start)

        return best_post

    def getMostRecent(self, k):
        result = []
        stack = []
        node = self.root

        # reverse in-order: right, node, left
        while (stack or node is not None) and len(result) < k:
            while node is not None:
                stack.append(node)
                node = node.right
            node = stack.pop()
            result.append(node.post)
            node = node.left

        return result

    # ---- Internal helpers ----

    def _insert_node(self, root, node):
        current = root
        while True:
            if node.key < current.key:
                if current.left is None:
                    current.left = node
                    node.parent = current
                    return
                current = current.left
            else:
                if current.right is None:
                    current.right = node
                    node.parent = current
                    return
                current = current.right

    def _transplant(self, u, v):
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        if v is not None:
            v.parent = u.parent

    def _minimum(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _delete_node(self, node):
        if node.left is None:
            self._transplant(node, node.right)
        elif node.right is None:
            self._transplant(node, node.left)
        else:
            successor = self._minimum(node.right)
            if successor.parent != node:
                self._transplant(successor, successor.right)
                successor.right = node.right
                successor.right.parent = successor
            self._transplant(node, successor)
            successor.left = node.left
            successor.left.parent = successor

    # ---- Structural metrics ----

    def height(self):
        return self._compute_height(self.root)

    def _compute_height(self, node):
        if node is None:
            return 0
        left_h = self._compute_height(node.left)
        right_h = self._compute_height(node.right)
        return 1 + max(left_h, right_h)

    def balancing_factor(self):
        if self.size == 0:
            return 0.0
        h = self.height()
        ideal = math.ceil(math.log(self.size + 1, 2))
        if ideal == 0:
            return float(h)
        return float(h) / float(ideal)


# =========================
# TREAP IMPLEMENTATION
# =========================

class TreapNode:
    def __init__(self, post):
        self.post = post
        self.key = (post.timestamp, post.postid)  # BST key
        self.priority = post.score                # heap key (max-heap)
        self.left = None
        self.right = None
        self.parent = None


class TreapFeed:
    def __init__(self):
        self.root = None
        self.id_to_node = {}
        self.size = 0
        self.rotation_count = 0
        self.stats = {
            "insert_count": 0,
            "insert_time_total": 0.0,
            "delete_count": 0,
            "delete_time_total": 0.0,
            "like_count": 0,
            "like_time_total": 0.0,
            "get_popular_count": 0,
            "get_popular_time_total": 0.0,
        }

    # ---- Rotations ----

    def _rotate_left(self, x):
        y = x.right
        if y is None:
            return
        x.right = y.left
        if y.left is not None:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        self.rotation_count += 1

    def _rotate_right(self, y):
        x = y.left
        if x is None:
            return
        y.left = x.right
        if x.right is not None:
            x.right.parent = y
        x.parent = y.parent
        if y.parent is None:
            self.root = x
        elif y == y.parent.left:
            y.parent.left = x
        else:
            y.parent.right = x
        x.right = y
        y.parent = x
        self.rotation_count += 1

    # ---- Public API ----

    def addPost(self, postid, timestamp, score):
        start = time.perf_counter()
        post = Post(postid, timestamp, score)
        node = TreapNode(post)

        if self.root is None:
            self.root = node
        else:
            self._bst_insert(node)
            self._heapify_up(node)

        self.id_to_node[postid] = node
        self.size += 1

        end = time.perf_counter()
        self.stats["insert_count"] += 1
        self.stats["insert_time_total"] += (end - start)

    def likePost(self, postid):
        start = time.perf_counter()
        node = self.id_to_node.get(postid)
        if node is not None:
            node.post.score += 1
            node.priority = node.post.score
            self._heapify_up(node)
        end = time.perf_counter()
        self.stats["like_count"] += 1
        self.stats["like_time_total"] += (end - start)

    def deletePost(self, postid):
        start = time.perf_counter()
        node = self.id_to_node.get(postid)
        if node is not None:
            self._delete_node(node)
            del self.id_to_node[postid]
            self.size -= 1
        end = time.perf_counter()
        self.stats["delete_count"] += 1
        self.stats["delete_time_total"] += (end - start)

    def getMostPopular(self):
        start = time.perf_counter()
        root_post = self.root.post if self.root is not None else None
        end = time.perf_counter()
        self.stats["get_popular_count"] += 1
        self.stats["get_popular_time_total"] += (end - start)
        return root_post

    def getMostRecent(self, k):
        result = []
        stack = []
        node = self.root

        # reverse in-order: right, node, left
        while (stack or node is not None) and len(result) < k:
            while node is not None:
                stack.append(node)
                node = node.right
            node = stack.pop()
            result.append(node.post)
            node = node.left

        return result

    # ---- Internal helpers ----

    def _bst_insert(self, node):
        current = self.root
        while True:
            if node.key < current.key:
                if current.left is None:
                    current.left = node
                    node.parent = current
                    return
                current = current.left
            else:
                if current.right is None:
                    current.right = node
                    node.parent = current
                    return
                current = current.right

    def _heapify_up(self, node):
        while node.parent is not None and node.priority > node.parent.priority:
            if node == node.parent.left:
                self._rotate_right(node.parent)
            else:
                self._rotate_left(node.parent)

    def _delete_node(self, node):
        # rotate down until node has at most one child, then remove it
        while node.left is not None or node.right is not None:
            if node.left is None:
                self._rotate_left(node)
            elif node.right is None:
                self._rotate_right(node)
            else:
                if node.left.priority > node.right.priority:
                    self._rotate_right(node)
                else:
                    self._rotate_left(node)
        # now node is a leaf
        if node.parent is None:
            self.root = None
        else:
            if node == node.parent.left:
                node.parent.left = None
            else:
                node.parent.right = None

    # ---- Structural metrics ----

    def height(self):
        return self._compute_height(self.root)

    def _compute_height(self, node):
        if node is None:
            return 0
        left_h = self._compute_height(node.left)
        right_h = self._compute_height(node.right)
        return 1 + max(left_h, right_h)

    def balancing_factor(self):
        if self.size == 0:
            return 0.0
        h = self.height()
        ideal = math.ceil(math.log(self.size + 1, 2))
        if ideal == 0:
            return float(h)
        return float(h) / float(ideal)


# =========================
# DATASET LOADER (SIMPLE)
# =========================

def iter_posts_from_file(path):
    """
    Simple JSON lines iterator.
    Each line must contain keys: id, created_utc, score.
    """
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            postid = obj.get("id")
            timestamp = int(obj.get("created_utc", 0))
            score = int(obj.get("score", 0))
            yield Post(postid, timestamp, score)