from rag import build_rag_system


def main():
    rag = build_rag_system()
    print(f"Indexed {rag.chunk_count} chunks from {rag.page_count} PDF pages.")

    question = input("Question: ").strip()
    if not question:
        raise ValueError("Question cannot be empty.")

    print(f"\nAnswer:\n{rag.chain.invoke(question)}")


if __name__ == "__main__":
    main()
