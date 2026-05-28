---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Document Processing Pipeline

## Concept

End-to-end document pipeline: PDF ingestion → text extraction → entity classification → structured storage. Uses parallel agents for speed and a coordinator for quality control.

## Architecture

```
PDF Upload
    │
    ▼
Extract Agent (OCR, text, tables)
    │
    ├──► Classify Agent (document type: invoice, contract, report)
    ├──► Entity Agent (extract: dates, amounts, names, addresses)
    └──► Summary Agent (1-paragraph summary)
    │
    ▼
Validate Agent (cross-check: does amount match line items?)
    │
    ▼
Store → Database + Vector DB (for semantic search)
```

## Code Skeleton

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

def extract_text(filepath: str) -> dict:
    """Extract text, tables, and metadata from a document."""
    import fitz  # PyMuPDF
    doc = fitz.open(filepath)
    pages = []
    for page in doc:
        pages.append({
            "text": page.get_text(),
            "tables": page.find_tables(),
            "page_num": page.number,
        })
    return {"filename": filepath, "pages": pages, "total_pages": len(pages)}

def classify_document(text: str) -> str:
    """Classify document type from text content."""
    patterns = {
        "invoice": ["invoice #", "due date", "amount due"],
        "contract": ["agreement", "parties", "hereby"],
        "report": ["executive summary", "findings", "recommendation"],
    }
    scores = {doc_type: sum(1 for kw in keywords if kw.lower() in text.lower())
              for doc_type, keywords in patterns.items()}
    return max(scores, key=scores.get)

extract_agent = Agent(
    name="extractor",
    model="gemini-2.5-flash",
    tools=[FunctionTool(extract_text)],
    instruction="Extract all text and tables from the uploaded document.",
)

classify_agent = Agent(
    name="classifier",
    model="gemini-2.5-flash",
    instruction="Classify document type: invoice, contract, report, or other.",
)

validate_agent = Agent(
    name="validator",
    model="gemini-2.5-pro",
    instruction="Cross-check extracted data: do amounts match line items? Are dates consistent? Flag discrepancies.",
)
```

## Pipeline Flow

```python
async def process_document(filepath: str) -> dict:
    # Step 1: Extract
    extracted = run_agent(extract_agent, f"Process: {filepath}")

    # Step 2: Parallel classification + entity extraction
    classify_result, entity_result = await asyncio.gather(
        run_agent_async(classify_agent, extracted),
        run_agent_async(entity_agent, extracted),
    )

    # Step 3: Validate
    validation = run_agent(validate_agent, f"{extracted}\n{entity_result}")

    # Step 4: Store
    doc_id = db.insert({
        "file": filepath,
        "type": classify_result,
        "entities": entity_result,
        "validation": validation,
    })
    return {"doc_id": doc_id, "type": classify_result}
```

## Pitfalls

- **PDF complexity**: Scanned PDFs need OCR, tables with merged cells break extraction, and multi-column layouts confuse text ordering. Test with real-world documents.
- **Entity extraction accuracy**: LLMs hallucinate numbers (invoice amounts, dates). Always validate extracted entities against source text.
- **Scale**: Processing one document takes 5-15s. For 10,000 documents, that's 14-42 hours. Use batch processing with async queues.
