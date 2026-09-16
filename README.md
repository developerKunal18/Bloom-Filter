# Bloom Filter

A Flask service demonstrating a Bloom filter for fast, memory-efficient probabilistic membership checks.

## Key idea

A Bloom filter can tell you:

- **False:** the item is definitely not present.
- **True:** the item may be present.

False positives are possible; false negatives are not.

## Features

- SHA-256 based hashing
- Double hashing for multiple bit positions
- Configurable filter size and hash count
- Batch insertion
- Fast membership checks
- Thread-safe operations
- Fill-ratio statistics
- Health endpoint
- Pytest test suite

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/items` | Add one value |
| POST | `/api/items/batch` | Add multiple values |
| GET | `/api/check/<value>` | Check probable membership |
| GET | `/api/stats` | Filter statistics |

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Tests:

```bash
pytest -q
```

## Example

```bash
curl -X POST http://localhost:5000/api/items -H "Content-Type: application/json" -d '{"value":"user-100"}'
curl http://localhost:5000/api/check/user-100
curl http://localhost:5000/api/check/unknown-user
```

## Architecture

```text
Input
  |
  v
Hash Functions
  |
  v
+-------------------+
|     Bit Array     |
| 0 1 0 1 1 0 ...   |
+-------------------+
  |
  v
Membership Check
  |             |
 FALSE         TRUE
 definite      maybe
 absent        present

```

## Learning Goals

Probabilistic data structures, hashing, bit arrays, memory-efficient membership checks, false positives, and practical uses in caches, databases, URL filtering, and distributed systems.
