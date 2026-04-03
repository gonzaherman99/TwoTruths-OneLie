# 🎭 Two Truths and a Lie

A terminal-based trivia game written in Python where players guess the lie hidden among three statements. Built with custom data structures and a CSV data pipeline for managing and validating question sets.

---

## 🎮 How to Play

Each round presents three statements — two are true, one is a lie. Your job is to pick the lie. Choose a category, answer up to 5 questions, and see how well you score.

```
┌─────────────────────────────────────────┐
│            Two Truths and a Lie         │
├─────────────────────────────────────────┤
│  1) Play Game                           │
│  2) Exit                                │
└─────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- No external dependencies — uses only the standard library

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/gonzaherman99/TwoTruths-OneLie.git
cd TwoTruths-OneLie

# 2. Run the game
python "project python.py"
```

That's it. No pip installs needed.

---

## 📁 Project Structure

```
TwoTruths-OneLie/
├── project python.py      # Main game entry point and UI
├── optimized_csv.py       # CSV data pipeline and optimizer
├── lies.csv               # Question dataset (Truth1, Truth2, Lie, Category)
├── optimized_data.jsonl   # Processed question data (auto-generated)
├── data_index.json        # Fast-lookup index by entry ID (auto-generated)
├── data.zip               # Compressed JSONL archive (auto-generated)
└── validation_report.json # Data quality report (auto-generated)
```

---

## 🧠 Architecture

### Data Structures

The game uses two custom data structures implemented from scratch:

**`HashTable`** — Organizes questions by category for O(1) average-case lookup. Questions are bucketed by topic so the game can quickly retrieve all entries for a chosen category.

**`StatementTree`** (Binary Search Tree) — Indexes every individual statement for duplicate detection and fast search across the full question pool.

### Data Pipeline (`optimized_csv.py`)

The `CSVOptimizer` class handles loading and processing the raw `lies.csv` file before the game starts:

- **Column detection** — Automatically finds truth/lie columns by name (no hardcoded headers needed)
- **Duplicate removal** — Hashes each statement set with SHA-256 to deduplicate entries
- **Validation** — Skips malformed rows and logs invalid entry counts
- **Storage optimization** — Exports to `.jsonl`, compresses to `.zip`, and builds a JSON index for fast access

The pipeline can run standalone to regenerate the processed files:

```bash
python optimized_csv.py
```

---

## 📊 Adding Your Own Questions

The game reads from `lies.csv`. The file must have columns with "truth" and "lie" in their names, and optionally a `Category` column:

| Truth1 | Truth2 | Lie | Category |
|---|---|---|---|
| Water boils at 100°C | The sky is blue | Cats can fly | Science |
| Paris is in France | Gold is a metal | Fish can climb trees | General |

Column names are detected automatically — as long as they contain the words `truth` and `lie`, the optimizer will find them.

---

## 🛠️ Running the Data Optimizer Standalone

If you update `lies.csv` and want to regenerate the processed files:

```bash
python optimized_csv.py
```

This will output:
- `optimized_data.jsonl` — one JSON entry per question
- `data.zip` — compressed version of the above
- `data_index.json` — ID-based lookup index
- `validation_report.json` — summary of processed, duplicate, and invalid entries

---

## 🤝 Contributing

Pull requests are welcome! If you'd like to add questions, fix bugs, or improve the UI, feel free to fork the repo and open a PR.

1. Fork the project
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source. Feel free to use, modify, and distribute it.
