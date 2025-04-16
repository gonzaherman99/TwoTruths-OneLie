import csv
import random

# ----------------------------
# Custom Hash Table (by topic)
# ----------------------------

class HashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return sum(ord(char) for char in key) % self.size

    def insert(self, key, value):
        idx = self._hash(key)
        self.table[idx].append((key, value))

    def get(self, key):
        idx = self._hash(key)
        return [val for k, val in self.table[idx] if k == key]

# ----------------------------
# Custom Binary Search Tree for Statement Search
# ----------------------------

class TreeNode:
    def __init__(self, statement):
        self.statement = statement
        self.left = None
        self.right = None

class StatementTree:
    def __init__(self):
        self.root = None

    def insert(self, statement):
        if not self.search(statement):  # ✅ Prevent duplicates
            self.root = self._insert_recursive(self.root, statement)

    def _insert_recursive(self, node, statement):
        if node is None:
            return TreeNode(statement)
        if statement < node.statement:
            node.left = self._insert_recursive(node.left, statement)
        else:
            node.right = self._insert_recursive(node.right, statement)
        return node

    def search(self, target):
        return self._search_recursive(self.root, target)

    def _search_recursive(self, node, target):
        if node is None:
            return False
        if node.statement == target:
            return True
        elif target < node.statement:
            return self._search_recursive(node.left, target)
        else:
            return self._search_recursive(node.right, target)


# ----------------------------
# Fisher-Yates Shuffle (custom shuffle)
# ----------------------------

def fisher_yates_shuffle(arr):
    for i in range(len(arr) - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

# ----------------------------
# Load CSV Data
# ----------------------------

def load_data(filepath):
    data_by_topic = HashTable()
    search_tree = StatementTree()
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            topic = row.get("Category", "General")
            entry = {
                "truth1": row["Truth 1"],
                "truth2": row["Truth 2"],
                "lie": row["Lie"]
            }
            data_by_topic.insert(topic, entry)
            search_tree.insert(row["Truth 1"])
            search_tree.insert(row["Truth 2"])
            search_tree.insert(row["Lie"])
    return data_by_topic, search_tree

# ----------------------------
# Game Round Logic
# ----------------------------

def play_round(entry):
    statements = [entry["truth1"], entry["truth2"], entry["lie"]]
    fisher_yates_shuffle(statements)

    print("\nWhich of the following is the lie?")
    for i, s in enumerate(statements, 1):
        print(f"{i}. {s}")

    while True:
        try:
            choice = int(input("Enter the number you think is the lie (1–3): "))
            if 1 <= choice <= 3:
                break
        except ValueError:
            pass
        print("Invalid choice, try again.")

    guess = statements[choice - 1]
    if guess == entry["lie"]:
        print(" Correct!")
        return True
    else:
        print(f" Wrong. The lie was: {entry['lie']}")
        return False

# ----------------------------
# Run the Game
# ----------------------------

def run_game():
    data_by_topic, search_tree = load_data("two_truths_and_a_lie.csv")

    topic = "General"
    entries = data_by_topic.get(topic)

    if not entries:
        print("No entries for this category. Showing fallback questions.")
        entries = data_by_topic.get("General")

    random.shuffle(entries)
    correct = 0
    for i in range(min(5, len(entries))):  # Play 5 rounds
        if play_round(entries[i]):
            correct += 1

    print(f"\n🎓 You scored {correct}/5!")

# ----------------------------
# Start
# ----------------------------

if __name__ == "__main__":
    run_game()

