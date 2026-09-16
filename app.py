from hashlib import sha256
from threading import RLock
from flask import Flask, jsonify, request

app = Flask(__name__)


class BloomFilter:
    def __init__(self, size=2048, hash_count=4):
        if size <= 0 or hash_count <= 0:
            raise ValueError("size and hash_count must be positive")
        self.size = size
        self.hash_count = hash_count
        self.bits = bytearray((size + 7) // 8)
        self.items_added = 0
        self.lock = RLock()

    def _positions(self, value):
        digest = sha256(value.encode("utf-8")).digest()
        h1 = int.from_bytes(digest[:8], "big")
        h2 = int.from_bytes(digest[8:16], "big") or 1
        return [(h1 + i * h2) % self.size for i in range(self.hash_count)]

    def _set_bit(self, position):
        self.bits[position // 8] |= 1 << (position % 8)

    def _get_bit(self, position):
        return bool(self.bits[position // 8] & (1 << (position % 8)))

    def add(self, value):
        if not isinstance(value, str) or not value:
            raise ValueError("value must be a non-empty string")
        with self.lock:
            for position in self._positions(value):
                self._set_bit(position)
            self.items_added += 1

    def might_contain(self, value):
        if not isinstance(value, str) or not value:
            raise ValueError("value must be a non-empty string")
        with self.lock:
            return all(self._get_bit(p) for p in self._positions(value))

    def stats(self):
        with self.lock:
            set_bits = sum(byte.bit_count() for byte in self.bits)
            return {
                "size": self.size,
                "hash_count": self.hash_count,
                "items_added": self.items_added,
                "set_bits": set_bits,
                "fill_ratio": round(set_bits / self.size, 4),
            }


bloom = BloomFilter()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "bloom-filter"})


@app.post("/api/items")
def add_item():
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not isinstance(body.get("value"), str):
        return jsonify({"error": "JSON body with string 'value' is required"}), 400
    if not body["value"]:
        return jsonify({"error": "value cannot be empty"}), 400
    bloom.add(body["value"])
    return jsonify({"value": body["value"], "added": True}), 201


@app.post("/api/items/batch")
def add_batch():
    body = request.get_json(silent=True)
    values = body.get("values") if isinstance(body, dict) else None
    if not isinstance(values, list) or not all(isinstance(v, str) and v for v in values):
        return jsonify({"error": "non-empty string list 'values' is required"}), 400
    for value in values:
        bloom.add(value)
    return jsonify({"added": len(values)}), 201


@app.get("/api/check/<value>")
def check(value):
    try:
        result = bloom.might_contain(value)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"value": value, "might_contain": result})


@app.get("/api/stats")
def stats():
    return jsonify(bloom.stats())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
