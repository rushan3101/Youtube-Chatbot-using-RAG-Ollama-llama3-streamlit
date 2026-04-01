from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


def create_vector_store(transcript: str):
    """
    Create a vector store from a given transcript.

    The transcript is split into smaller chunks using the RecursiveCharacterTextSplitter,
    and then embedded into a vector space using the OllamaEmbeddings model.

    The resulting vectorstore is persisted to disk in the "chroma_db" directory.

    :param transcript: The transcript to create the vector store from.
    :return: The created vectorstore.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    documents = text_splitter.create_documents([transcript])

    embedding_model = OllamaEmbeddings(model="nomic-embed-text")

    vectorstore = Chroma.from_documents(
        documents,
        embedding_model
    )

    return vectorstore


def get_retriever(vectorstore):
    """
    Return a retriever from a given vectorstore.

    The retriever is configured to search for documents with similar
    embeddings, and to return the top 5 most similar documents.

    :param vectorstore: The vectorstore to create the retriever from.
    :return: The created retriever.
    """
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
    return retriever