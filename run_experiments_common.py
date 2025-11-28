import random
import time
from typing import Any, Dict, List, Sequence, Tuple

from main import BSTFeed, TreapFeed, iter_posts_from_file

PostTuple = Tuple[str, int, int]

STRUCTURE_ORDER = ("BST", "Treap")
STRUCTURE_CLASSES = {
    "BST": BSTFeed,
    "Treap": TreapFeed,
}

METRIC_KEYS = [
    "Insertion Time (avg)",
    "Deletion Time (avg)",
    "Search Time (avg)",
    "Height of the Tree",
    "Tree Balancing Factor",
]
TIME_METRIC_KEYS = METRIC_KEYS[:3]


def load_posts(dataset_path: str, sample_size: int) -> List[PostTuple]:
    """Load up to sample_size posts from a JSONL dataset."""
    posts: List[PostTuple] = []
    for post in iter_posts_from_file(dataset_path):
        posts.append((post.postid, post.timestamp, post.score))
        if len(posts) >= sample_size:
            break
    if not posts:
        raise ValueError(f"No posts found in dataset {dataset_path}")
    return posts


def generate_synthetic_posts(sample_size: int, seed: int) -> List[PostTuple]:
    rng = random.Random(seed)
    base_ts = int(time.time())
    posts = []
    for idx in range(sample_size):
        postid = f"synthetic_{idx}"
        timestamp = base_ts + rng.randint(-500_000, 500_000)
        score = rng.randint(1, 10_000)
        posts.append((postid, timestamp, score))
    return posts


def _search_by_key(node, key):
    """Standard BST search that works for both BSTNode and TreapNode."""
    current = node
    while current is not None:
        if key == current.key:
            return current
        if key < current.key:
            current = current.left
        else:
            current = current.right
    return None


def run_trial(
    feed_cls,
    posts: Sequence[PostTuple],
    search_trials: int,
    delete_ratio: float,
    rng: random.Random,
) -> Dict[str, Any]:
    feed = feed_cls()
    for postid, timestamp, score in posts:
        feed.addPost(postid, timestamp, score)

    keys = [(timestamp, postid) for (postid, timestamp, _score) in posts]
    sample_keys = rng.sample(keys, min(search_trials, len(keys)))

    search_total = 0.0
    for key in sample_keys:
        start = time.perf_counter()
        _search_by_key(feed.root, key)
        end = time.perf_counter()
        search_total += end - start

    delete_count = int(len(posts) * delete_ratio)
    if delete_count > 0:
        to_delete = rng.sample([pid for pid, _, _ in posts], delete_count)
        for postid in to_delete:
            feed.deletePost(postid)

    metrics: Dict[str, Any] = {
        "Insertion Time (avg)": feed.stats["insert_time_total"] / max(feed.stats["insert_count"], 1),
        "Deletion Time (avg)": feed.stats["delete_time_total"] / max(feed.stats["delete_count"], 1),
        "Search Time (avg)": search_total / max(len(sample_keys), 1),
        "Height of the Tree": feed.height(),
        "Tree Balancing Factor": feed.balancing_factor(),
    }
    if hasattr(feed, "rotation_count"):
        metrics["Rotation Count"] = feed.rotation_count
    return metrics


def print_results_table(results: Dict[str, Dict[str, Any]], structures: Sequence[str]):
    headers = ["Metric", *structures]
    rows = []
    for key in METRIC_KEYS:
        row = [key]
        for structure in structures:
            value = results[structure][key]
            if isinstance(value, float):
                row.append(f"{value:.6f}")
            else:
                row.append(str(value))
        rows.append(tuple(row))

    if any("Rotation Count" in results[structure] for structure in structures):
        rotation_row = ["Rotation Count"]
        for structure in structures:
            rotation_row.append(str(results[structure].get("Rotation Count", "-")))
        rows.append(tuple(rotation_row))

    col_widths = [max(len(str(item)) for item in column) for column in zip(headers, *rows)]

    def format_row(row):
        return " | ".join(str(item).ljust(width) for item, width in zip(row, col_widths))

    print(format_row(headers))
    print("-+-".join("-" * width for width in col_widths))
    for row in rows:
        print(format_row(row))
