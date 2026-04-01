from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(retriever):

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer ONLY from the context.\n\nContext:\n{context}"
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{query}")
        ]
    )

    parallel_chain = RunnableParallel(
        {
            "context": RunnableLambda(lambda x: x["query"]) | retriever | RunnableLambda(format_docs),
            "query": RunnableLambda(lambda x: x["query"]),
            "chat_history": RunnableLambda(lambda x: x["chat_history"])
        }
    )

    model = ChatOllama(
        model="llama3",
        streaming=True
    )

    chain = parallel_chain | prompt | model | StrOutputParser()

    return chain