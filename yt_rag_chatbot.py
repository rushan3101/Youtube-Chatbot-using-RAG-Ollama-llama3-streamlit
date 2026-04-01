from langchain_ollama import ChatOllama, OllamaEmbeddings
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough,RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

import os
os.chdir('D:\\Rushan\\Data Science\\Langchain\\Projects\\YT_ChatBot')

def get_transcript(video_url):
    video_id = video_url.split("v=")[-1]

    try:
        ytApi = YouTubeTranscriptApi()
        transcript_list = ytApi.fetch(video_id,languages=['en'])
        transcript = " ".join(chunk.text for chunk in transcript_list)
        return transcript
    
    except (TranscriptsDisabled, Exception) as e:
        print(f"Error fetching transcript for {video_url}: {e}")
        print("Try a different video.")
        return None
    
def transcript_to_retriever(transcript):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.create_documents([transcript])
    
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(chunks, embedding_model,persist_directory="chroma_db")

    retriever = vectorstore.as_retriever(search_type="similarity",search_kwargs={"k": 3})

    return retriever
    
def query_to_generator(query,retriever):

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant that answers questions based on the provided youtube video transcript. {context}"),
            ("human", "{query}"),
        ]
    )

    def format_docs(retrieved_docs):
        return "\n\n".join(doc.page_content for doc in retrieved_docs)
    
    parallel_chain = RunnableParallel(
        {
            "context" : retriever | RunnableLambda(format_docs),
            "query" : RunnablePassthrough()
        }
    )

    model = ChatOllama(model="llama3")

    final_chain = parallel_chain | prompt | model | StrOutputParser()

    return final_chain.invoke(query)

    
if __name__ == "__main__":

    video_url = "https://www.youtube.com/watch?v=9QXCkMTbrSk"
    transcript = get_transcript(video_url)
    
    if transcript:
        query = "What is the video about?"
        retriever = transcript_to_retriever(transcript)
        response = query_to_generator(query, retriever)
        print("Response: \n", response)