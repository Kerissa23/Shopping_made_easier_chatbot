
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from prompt import get_prompt
from dotenv import load_dotenv

load_dotenv('.env.sh')

def get_chroma_client():
    """
    Returns a chroma vector store instance.
    """
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        collection_name="website_data",
        embedding_function=embedding_function,
        persist_directory="data/chroma")

def make_chain():
    """
    Creates a chain of langchain components.
    """
    model = ChatOpenAI(
        model_name="llama3-70b-8192",
        temperature=0.0,
        verbose=True,
    )
    vector_store = get_chroma_client()
    prompt = get_prompt()

    retriever = vector_store.as_retriever(search_type="mmr", verbose=True)

    chain = ConversationalRetrievalChain.from_llm(
        model,
        retriever=retriever,
        return_source_documents=True,
        combine_docs_chain_kwargs=dict(prompt=prompt),
        verbose=True,
        rephrase_question=False,
    )
    return chain


def get_response(question):
    """
    Generates a response based on the input question.
    """
    chat_history = ""
    chain = make_chain()
    response = chain({"question": question, "chat_history": chat_history})
    return response['answer']