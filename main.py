from src.transcript import get_transcript
from src.vector_store import create_vector_store, get_retriever
from src.rag_chain import build_rag_chain


def process_video(video_url: str):
    
    transcript = get_transcript(video_url)

    if not transcript:
        return None

    vectorstore = create_vector_store(transcript)
    retriever = get_retriever(vectorstore)

    rag_chain = build_rag_chain(retriever)
    
    return rag_chain


# 🔥 streaming generator
def ask_question(chain, query: str, chat_history):
    return chain.stream({
        "query": query,
        "chat_history": chat_history
    })
