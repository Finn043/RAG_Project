import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Config } from "@netlify/functions";
import { getDocument } from "pdfjs-dist/legacy/build/pdf.mjs";
import { WorkerMessageHandler } from "pdfjs-dist/legacy/build/pdf.worker.mjs";
import { selectRelevant, splitIntoChunks, type TextChunk } from "../../server/rag-core";

const pdfjsGlobal = globalThis as typeof globalThis & {
  pdfjsWorker?: { WorkerMessageHandler: typeof WorkerMessageHandler };
};
pdfjsGlobal.pdfjsWorker ??= { WorkerMessageHandler };

type IndexedChunk = TextChunk & { vector: number[] };

const EMBEDDING_MODEL = "text-embedding-3-small";
const CHAT_MODEL = "gpt-4o-mini";
const PAPERS_DIRECTORY = join(process.cwd(), "papers");

let indexedCorpus: Promise<IndexedChunk[]> | undefined;

async function openAiRequest<T>(path: string, body: unknown): Promise<T> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("OPENAI_API_KEY is not configured.");

  const response = await fetch(`https://api.openai.com/v1/${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(45_000),
  });
  if (!response.ok) throw new Error(`OpenAI request failed with ${response.status}.`);
  return response.json() as Promise<T>;
}

async function embed(texts: string[]): Promise<number[][]> {
  const result = await openAiRequest<{ data: { embedding: number[] }[] }>("embeddings", {
    model: EMBEDDING_MODEL,
    input: texts,
  });
  return result.data.map((item: { embedding: number[] }) => item.embedding);
}

async function readPdfPages(fileName: string): Promise<TextChunk[]> {
  const fileBuffer = await readFile(join(PAPERS_DIRECTORY, fileName));
  const pdf = await getDocument({ data: new Uint8Array(fileBuffer), useSystemFonts: true }).promise;
  const pages: TextChunk[] = [];

  for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
    const page = await pdf.getPage(pageNumber);
    const content = await page.getTextContent();
    const text = content.items
      .filter((item): item is typeof item & { str: string } => "str" in item)
      .map((item) => item.str)
      .join(" ");
    pages.push({ text, source: fileName, page: pageNumber });
  }
  return pages;
}

async function buildIndex(): Promise<IndexedChunk[]> {
  const files = (await readdir(PAPERS_DIRECTORY)).filter((name) => name.toLowerCase().endsWith(".pdf")).sort();
  if (!files.length) throw new Error("No PDF files found in the papers directory.");

  const pages = (await Promise.all(files.map(readPdfPages))).flat();
  const chunks = pages.flatMap((page) =>
    splitIntoChunks(page.text).map((text) => ({ text, source: page.source, page: page.page })),
  );
  if (!chunks.length) throw new Error("No searchable text found in the PDF corpus.");

  const vectors = await embed(chunks.map((chunk) => chunk.text));
  return chunks.map((chunk, index) => ({ ...chunk, vector: vectors[index] }));
}

function getIndex(): Promise<IndexedChunk[]> {
  indexedCorpus ??= buildIndex().catch((error) => {
    indexedCorpus = undefined;
    throw error;
  });
  return indexedCorpus;
}

const systemPrompt = `You are a rigorous research analyst specializing in Brazilian Jiu-Jitsu.
Rules:
1. Answer using only the supplied context.
2. Do not invent facts or use outside knowledge.
3. If the context is insufficient, say: "I don't know based on the provided sources."
4. Put an exact [Source: filename, page N] citation after every factual sentence or bullet.
5. Always answer in English, regardless of the language of the question.`;

export default async (request: Request) => {
  if (request.method !== "POST") {
    return Response.json({ error: "Method not allowed." }, { status: 405 });
  }

  let question: unknown;
  try {
    const body = await request.json();
    question = typeof body === "object" && body !== null && "question" in body
      ? body.question
      : undefined;
  } catch {
    return Response.json({ error: "Request body must be valid JSON." }, { status: 400 });
  }
  if (typeof question !== "string" || !question.trim() || question.length > 2000) {
    return Response.json({ error: "Enter a question of 1–2,000 characters." }, { status: 400 });
  }

  try {
    const [records, [queryVector]] = await Promise.all([getIndex(), embed([question.trim()])]);
    const relevant = selectRelevant(records, queryVector);
    const context = relevant
      .map((chunk) => `[Source: ${chunk.source}, page ${chunk.page}]\n${chunk.text}`)
      .join("\n\n");
    const result = await openAiRequest<{
      choices: { message: { content: string | null } }[];
    }>("chat/completions", {
      model: CHAT_MODEL,
      temperature: 0,
      messages: [
        { role: "system", content: `${systemPrompt}\n\nContext:\n${context || "No relevant context was found."}` },
        { role: "user", content: question.trim() },
      ],
    });
    return Response.json({ answer: result.choices[0]?.message?.content ?? "" });
  } catch (error) {
    console.error("RAG request failed", error);
    return Response.json({ error: "Unable to answer right now. Please try again." }, { status: 502 });
  }
};

export const config: Config = {
  path: "/api/chat",
  method: "POST",
  rateLimit: {
    windowLimit: 6,
    windowSize: 60,
    aggregateBy: ["ip"],
  },
};
