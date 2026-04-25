import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import create_react_agent

from tools import scrape_url, web_search

load_dotenv()


def clear_dead_local_proxy():
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        if os.getenv(key) == "http://127.0.0.1:9":
            os.environ.pop(key, None)


clear_dead_local_proxy()

llm = ChatMistralAI(model="mistral-small-latest", temperature=0)


def build_researcher_agent():
    return create_react_agent(
        model=llm,
        tools=[web_search],
    )


def build_reader_agent():
    return create_react_agent(
        model=llm,
        tools=[scrape_url],
    )


writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write polished, factual research briefs with clear sections, concise paragraphs, and no placeholder citations."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Executive Summary
- Key Findings (4-6 numbered findings with short, evidence-based explanations)
- India-Specific Implications
- Risks and Uncertainties
- Conclusion
- Sources (list only real URLs found in the research; do not invent URLs or use example.com)

Use markdown headings, short paragraphs, and bullets where helpful. Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()


critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest, specific, concise, and useful."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

Final Verdict:
...

Keep the review focused and avoid repeating the full report."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
