from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from prompt import get_prompt
from dotenv import load_dotenv
import json
import re

load_dotenv('.env.sh')

def get_llm():
    """Creates and returns the base language model instance."""
    return ChatOpenAI(
        model_name="llama3-70b-8192",
        temperature=0.0,
        verbose=True,
    )

def get_chroma_client():
    """Returns a chroma vector store instance."""
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        collection_name="website_data",
        embedding_function=embedding_function,
        persist_directory="data/chroma")

def make_chain():
    """Creates the full conversational chain."""
    model = get_llm()
    vector_store = get_chroma_client()
    prompt = get_prompt()
    
    chain = ConversationalRetrievalChain.from_llm(
        model,
        retriever=vector_store.as_retriever(),
        return_source_documents=True,
        combine_docs_chain_kwargs=dict(prompt=prompt),
        verbose=True,
        rephrase_question=True,
    )
    return chain

def get_response(question, chat_history):
    """Generates the final, formatted table response from the LLM."""
    chain = make_chain()
    response = chain({"question": question, "chat_history": chat_history})
    return response['answer']

def parse_query_to_keywords(query, chat_history):
    """
    Uses the LLM to convert a natural language query into an effective
    e-commerce search term, using history for context.
    """
    parsing_prompt_template = """
    You are an expert e-commerce search query optimizer. Your task is to take a user's conversational query
    and the chat history, and convert it into a clean, effective search keyword phrase.

    **Chat History:**
    {chat_history}
    
    **Latest User Query:** "{user_query}"
    
    Extract the core product and all relevant attributes (color, brand, gender, etc.)
    and create a single, powerful search string.
    
    Respond ONLY with a JSON object in the following format:
    {{
      "keywords": "the optimized search keywords"
    }}

    Example 1 (Follow-up):
    Chat History: [("show me purple kurtas", "...")]
    Latest User Query: "only from myntra"
    Response: {{"keywords": "purple kurtas from myntra"}}

    Example 2 (New Search):
    Latest User Query: "i want red shoes between 1000 and 3000"
    Response: {{"keywords": "red shoes between 1000 and 3000"}}
    """
    
    llm = get_llm()
    history_str = "\n".join([f"Human: {q}\nAI: {a}" for q, a in chat_history])
    parsing_prompt = parsing_prompt_template.format(user_query=query, chat_history=history_str)
    
    response = llm.invoke(parsing_prompt)
    
    try:
        json_string = re.search(r'\{.*\}', response.content, re.DOTALL).group()
        parsed_data = json.loads(json_string)
        print(f"LLM extracted keywords as: {parsed_data}")
        return parsed_data.get("keywords", query)
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing keywords from LLM: {e}. Using raw query.")
        return query