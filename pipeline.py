import re
import sys

from agents import (
    build_reader_agent,
    build_researcher_agent,
    critic_chain,
    writer_chain,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tools import web_search
from vector_store import add_to_vector_db, search_vector_db


def safe_print(*args):
    text = " ".join(str(a) for a in args)
    sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()


def extract_urls(text):
    urls = re.findall(r'https?://[^\s\])}>"\']+', text)
    return [url.rstrip(".,;:") for url in urls]


def content_to_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or item))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


def run_research_pipeline(topic) -> dict:
    state = {}

    safe_print("\n" + "=" * 50)
    safe_print("RESEARCH PHASE")
    safe_print("=" * 50)

    search_results = content_to_text(web_search.invoke(topic))
    if not extract_urls(search_results):
        search_agent = build_researcher_agent()
        search_result = search_agent.invoke({
            "messages": [
                ("user", f"Find recent, reliable and detailed information about the topic: {topic}")
            ]
        })
        search_results = content_to_text(search_result["messages"][-1].content)

    state["search_results"] = search_results
    state["sources"] = extract_urls(state["search_results"])
    safe_print("\nSearch Results:\n", state["search_results"])

    safe_print("\n" + "=" * 50)
    safe_print("READING PHASE")
    safe_print("=" * 50)

    reader_agent = build_reader_agent()
    all_scraped = []

    for url in state["sources"][:3]:
        safe_print(f"\nScraping URL: {url}")
        result = reader_agent.invoke({
            "messages": [
                ("user", f"Scrape this URL and return the clean text content:\n{url}")
            ]
        })
        content = content_to_text(result["messages"][-1].content)
        all_scraped.append(content)

    state["scraped_content"] = "\n\n".join(all_scraped) if all_scraped else "No content scraped."
    safe_print("\nScraped Content:\n", state["scraped_content"])

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_text(state["scraped_content"][:5000])

    vector_ready = False
    for i, chunk in enumerate(chunks):
        try:
            add_to_vector_db([chunk], source=f"{topic[:60]}_chunk_{i}")
            vector_ready = True
        except Exception as exc:
            safe_print("Vector store unavailable; continuing without RAG:", exc)
            break

    safe_print("\n" + "=" * 50)
    safe_print("WRITING PHASE")
    safe_print("=" * 50)

    docs = []
    if vector_ready:
        try:
            docs = search_vector_db(topic, k=3)
        except Exception as exc:
            safe_print("Vector search unavailable; using scraped content:", exc)

    retrieved_text = "\n\n".join([doc.page_content for doc in docs]) if docs else state["scraped_content"][:2000]
    research_combined = f"""=== RELEVANT CONTEXT (RAG) ===
{retrieved_text}

=== SEARCH RESULTS ===
{state['search_results'][:1000]}
"""

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
    })

    safe_print("\nReport:\n", state["report"])

    safe_print("\n" + "=" * 50)
    safe_print("CRITIC PHASE")
    safe_print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"],
    })

    safe_print("\nCritic Review:\n", state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\nEnter a Research Topic: ")
    run_research_pipeline(topic)
