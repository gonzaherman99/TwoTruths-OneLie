#!/usr/bin/env python3
import sys
import random
from optimized_csv import CSVOptimizer

# ----------------------------
# ASCII UI Templates
# ----------------------------
MAIN_MENU = r"""
┌─────────────────────────────────────────┐
│   Two Truths and a Lie                 │
├─────────────────────────────────────────┤
│ 1) Play Game                           │
│ 2) View Progress                       │
│ 3) Exit                                │
└─────────────────────────────────────────┘
"""

CATEGORY_MENU = r"""
┌─────────────────────────────────────────┐
│   Choose a Category                    │
├─────────────────────────────────────────┤
│ Available: {available:<27}│
│ Category: [{default:<24}]│
└─────────────────────────────────────────┘
"""

QUESTION_SCREEN = r"""
┌─────────────────────────────────────────┐
│   Round {roundno} of {total:<23}│
│   Category: {category:<23}│
├─────────────────────────────────────────┤
│ Which of the following is the lie?     │
│                                         │
│ 1. {s1:<33}│
│ 2. {s2:<33}│
│ 3. {s3:<33}│
└─────────────────────────────────────────┘
"""

RESULT_SCREEN = r"""
┌─────────────────────────────────────────┐
│   Result                               │
├─────────────────────────────────────────┤
│ {outcome:<37}│
│ Score: {score}/{total:<29}│
└─────────────────────────────────────────┘
"""

PROGRESS_SCREEN_HEADER = r"""
┌─────────────────────────────────────────┐
│   Progress Over Time                   │
├─────────────────────────────────────────┤
"""
PROGRESS_SCREEN_ROW = "│ {date} │ {score}/{total:<21}│"

# ----------------------------
# Data Structures
# ----------------------------
class HashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [[] for _ in range(size)]
    def _hash(self, key):
        return sum(ord(c) for c in key) % self.size
    def insert(self, key, value):
        self.table[self._hash(key)].append((key, value))
    def get(self, key):
        return [v for k, v in self.table[self._hash(key)] if k == key]

class TreeNode:
    def __init__(self, statement):
        self.statement = statement
        self.left = None
        self.right = None

class StatementTree:
    def __init__(self): self.root = None
    def insert(self, stmt):
        if not self.search(stmt):
            self.root = self._insert(self.root, stmt)
    def _insert(self, node, stmt):
        if node is None: return TreeNode(stmt)
        if stmt < node.statement: node.left  = self._insert(node.left, stmt)
        else:                    node.right = self._insert(node.right, stmt)
        return node
    def search(self, target): return self._search(self.root, target)
    def _search(self, node, target):
        if not node: return False
        if node.statement == target: return True
        return self._search(node.left if target < node.statement else node.right, target)

# ----------------------------
# Util
# ----------------------------
def load_from_optimizer(optimizer):
    data_by_topic = HashTable()
    search_tree = StatementTree()
    for entry in optimizer.data:
        row = entry['original_columns']
        topic = row.get('Category', 'General')
        t1, t2, lie = entry['statements']
        data_by_topic.insert(topic, {'truth1':t1,'truth2':t2,'lie':lie})
        for stmt in (t1, t2, lie): search_tree.insert(stmt)
    return data_by_topic, search_tree

# ----------------------------
# UI
# ----------------------------
def show_main_menu():
    print(MAIN_MENU)
    return input("Enter choice: ").strip()

def show_category_menu(topics, default='General'):
    avail = ", ".join(topics)
    print(CATEGORY_MENU.format(available=avail, default=default))
    return input("Category: ").strip() or default

def play_round_ui(entry, roundno, total, category):
    t1, t2, lie = entry['truth1'], entry['truth2'], entry['lie']
    arr = [t1, t2, lie]
    random.shuffle(arr)
    print(QUESTION_SCREEN.format(roundno=roundno, total=total, category=category, s1=arr[0], s2=arr[1], s3=arr[2]))
    while True:
        try:
            choice = int(input("Your answer (1–3): "))
            if 1 <= choice <= 3: break
        except:
            pass
        print("Invalid choice, try again.")
    guess = arr[choice-1]
    correct = (guess == lie)
    outcome = "Correct!" if correct else f"Wrong. Lie was: \"{lie}\""
    return correct, outcome

def show_result(correct, outcome, score, total):
    print(RESULT_SCREEN.format(outcome=outcome, score=score, total=total))
    input("[Press ↵ for next]")

# ----------------------------
# Main Game
# ----------------------------
def run_game():
    # Optimize data
    try:
        opt = CSVOptimizer('lies.csv', write_files=False).validate_entries()
    except Exception as e:
        print(f" Optimization error: {e}")
        sys.exit(1)
    # Build structures
    data_by_topic, _ = load_from_optimizer(opt)
    topics = sorted(set(k for bucket in data_by_topic.table for k,_ in bucket))

    while True:
        choice = show_main_menu()
        if choice == '1':
            cat = show_category_menu(topics)
            entries = data_by_topic.get(cat) or data_by_topic.get('General')
            if not entries:
                print("No questions available. Returning to menu.")
                continue
            random.shuffle(entries)
            score = 0
            total = min(5, len(entries))
            for i in range(1, total+1):
                correct, outcome = play_round_ui(entries[i-1], i, total, cat)
                if correct: score += 1
                show_result(correct, outcome, score, total)
            print(f"\n🎓 You scored {score}/{total}!\n")
        elif choice == '2':
            print("Progress feature coming soon.")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid menu choice.")

if __name__ == '__main__':
    run_game()
