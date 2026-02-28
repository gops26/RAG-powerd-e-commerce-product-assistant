# Reranking Feature

The project used LLM for re-ranking the context vectors. I am now exploring advanced re-ranking features. 

I propose a future plan to integrate with BGE Reranker qwen3 re-ranker.  


- ## QWEN RERANKER - 

Qwen3-Reranker-0.6B: A lightweight, 0.6-billion parameter model designed for maximum efficiency. It is ideal for budget-conscious pipelines or applications with lower complexity.

Qwen3-Reranker-4B: With 4 billion parameters, this model offers an optimal balance between accuracy and computational cost, making it suitable for most standard production RAG systems.

Qwen3-Reranker-8B: This 8-billion parameter model represents the "pinnacle of reranking accuracy" for mission-critical applications where maximum relevance is required regardless of compute cost.

- ## BGE reranker

Developed by BAAI, the BGE-reranker-v2-m3 is an open-source, multilingual model that supports over 100 languages. It is positioned as a high-accuracy choice for production environments, particularly those with access to dedicated hardware.