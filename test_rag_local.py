# tests/test_rag_local.py
from backend.ai.retriever import Retriever
from backend.ai.generator import make_prompt, generate_answer

def main():
    # Initialize retriever
    r = Retriever()
    query = "Spike in DLQ messages after maintenance on EDI"
    
    # Step 1: Retrieve top matches from cases and KB
    hits = r.search(query, top_k=3)
    
    # Step 2: Build prompt from retrieved context
    messages = make_prompt(query, hits)
    
    # Step 3: Print retrieved snippets
    print("=== CONTEXT HITS ===")
    for k, v in hits.items():
        print(f"{k} -> {[h.get('text', '')[:80] for h in v]}")  # show short preview
    
    # Step 4: Generate and print the answer (mocked if no LLM)
    print("\n=== ANSWER ===")
    print(generate_answer(messages))

if __name__ == "__main__":
    main()
