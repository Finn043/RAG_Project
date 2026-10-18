import assert from "node:assert/strict";
import test from "node:test";
import { cosineSimilarity, selectRelevant, splitIntoChunks } from "../server/rag-core.ts";

test("chunking respects size and keeps overlap between adjacent chunks", () => {
  const text = "A cited research sentence. ".repeat(150);
  const chunks = splitIntoChunks(text, 120, 20);

  assert.ok(chunks.length > 1);
  assert.ok(chunks.every((chunk) => chunk.length <= 120));
  const overlap = Array.from({ length: 20 }, (_, index) => 20 - index).find((size) =>
    chunks[1].startsWith(chunks[0].slice(-size)),
  );
  assert.ok(overlap && overlap >= 15);
});

test("cosine similarity handles aligned, orthogonal, and invalid vectors", () => {
  assert.equal(cosineSimilarity([1, 0], [1, 0]), 1);
  assert.equal(cosineSimilarity([1, 0], [0, 1]), 0);
  assert.equal(cosineSimilarity([], []), 0);
});

test("retrieval filters by threshold and returns at most top five", () => {
  const records = Array.from({ length: 7 }, (_, index) => ({
    id: index,
    vector: [1 - index * 0.1, Math.sqrt(1 - (1 - index * 0.1) ** 2)],
  }));

  const matches = selectRelevant(records, [1, 0], 0.5, 5);
  assert.deepEqual(matches.map(({ id }) => id), [0, 1, 2, 3, 4]);
});
