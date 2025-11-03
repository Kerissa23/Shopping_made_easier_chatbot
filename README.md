# ShopSmart AI Assistant

ShopSmart AI is an intelligent shopping assistant that helps users find products across multiple e-commerce platforms (Flipkart, Myntra, Snapdeal). It leverages the power of Large Language Models (LLMs) for natural language understanding and ChromaDB for persistent storage of chat history and scraped product data, enabling a more informed and conversational shopping experience through Retrieval Augmented Generation (RAG).

Video:
[https://github.com/Kerissa23/Shopping_made_easier_chatbot/blob/main/Recording%202025-11-03%20175319.gif]
## Features

*   **Multi-Platform Product Search:** Aggregates product data from Flipkart, Myntra, and Snapdeal based on user queries.
*   **Intelligent Conversational Interface (LLM-powered):** Understands natural language queries, greetings, farewells, and generic questions using a Large Language Model (LLM).
*   **Persistent Chat History:** Stores conversation history using ChromaDB, allowing the bot to maintain context across interactions.
*   **Product Data Caching & RAG:** Scraped product data is stored in ChromaDB, forming a knowledge base. This data is then retrieved and augmented into the LLM's prompt (Retrieval Augmented Generation - RAG) for generating more accurate and specific product recommendations, reducing the need for repeated web scraping and improving response quality.
*   **Dynamic Bot Responses (LLM-powered):** Generates nuanced and context-aware responses using an LLM, informed by retrieved chat history and product results.
*   **"Show More" Functionality:** Allows users to view additional results from an ongoing search without initiating a new query.

## Technologies Used

*   **FastAPI:** For building the backend API.
*   **LangChain:** For orchestrating LLM interactions, including intent classification, keyword extraction, and response generation, integrating the RAG pipeline.
*   **ChromaDB:** A vector database used for persistent storage and semantic search of both chat history and product data, serving as the retrieval component for RAG.
*   **Sentence Transformers:** For generating embeddings (via ChromaDB's `SentenceTransformerEmbeddingFunction`) to enable semantic search for RAG.
*   **OpenAI (or Compatible LLM):** The core Large Language Model (LLM) used for natural language processing, conversational understanding, and response generation.
*   **Selenium:** (Likely) Used in `flipkart.py`, `myntra.py`, `snapdeal.py` for dynamic web scraping, handling JavaScript-rendered content.
*   **Pydantic:** For data validation and settings management.
*   **Python-dotenv:** For managing environment variables securely.

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Kerissa23/Shopping_made_easier_chatbot
cd shopping_chatbot
