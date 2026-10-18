export type TextChunk = {
  text: string;
  source: string;
  page: number;
};

export function splitIntoChunks(text: string, size = 1200, overlap = 200): string[] {
  const cleanText = text.replace(/\s+/g, " ").trim();
  if (!cleanText) return [];

  const chunks: string[] = [];
  let start = 0;
  while (start < cleanText.length) {
    let end = Math.min(start + size, cleanText.length);
    if (end < cleanText.length) {
      const boundary = Math.max(
        cleanText.lastIndexOf(". ", end),
        cleanText.lastIndexOf("? ", end),
        cleanText.lastIndexOf("! ", end),
        cleanText.lastIndexOf(" ", end),
      );
      if (boundary > start + size * 0.55) end = boundary + 1;
    }

    chunks.push(cleanText.slice(start, end).trim());
    if (end === cleanText.length) break;
    start = Math.max(start + 1, end - overlap);
  }
  return chunks;
}

export function cosineSimilarity(left: number[], right: number[]): number {
  if (left.length !== right.length || left.length === 0) return 0;
  let dot = 0;
  let leftNorm = 0;
  let rightNorm = 0;
  for (let index = 0; index < left.length; index += 1) {
    dot += left[index] * right[index];
    leftNorm += left[index] ** 2;
    rightNorm += right[index] ** 2;
  }
  if (!leftNorm || !rightNorm) return 0;
  return dot / Math.sqrt(leftNorm * rightNorm);
}

export function selectRelevant<T extends { vector: number[] }>(
  records: T[],
  queryVector: number[],
  threshold = 0.2,
  limit = 5,
): T[] {
  return records
    .map((record) => ({ record, score: cosineSimilarity(record.vector, queryVector) }))
    .filter(({ score }) => score >= threshold)
    .sort((left, right) => right.score - left.score)
    .slice(0, limit)
    .map(({ record }) => record);
}
