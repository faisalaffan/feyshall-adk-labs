"""Context Compaction — token budgeting and conversation summarization.
Run: python 03-memory-and-state/context-compaction/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


class ContextCompactor:
    """Compacts old conversation turns to stay within token budget."""

    def __init__(self, max_tokens: int = 4000, keep_recent: int = 5):
        self.max_tokens = max_tokens
        self.keep_recent = keep_recent

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (~4 chars per token)."""
        return len(text) // 4

    def should_compact(self, history: list[dict]) -> bool:
        total_text = "".join(m.get("content", "") for m in history)
        return self.estimate_tokens(total_text) > self.max_tokens

    def compact(self, history: list[dict]) -> list[dict]:
        """Keep recent messages verbatim, summarize older ones."""
        if len(history) <= self.keep_recent:
            return history

        recent = history[-self.keep_recent:]
        older = history[:-self.keep_recent]
        older_text = " | ".join(
            f"{m['role']}: {m.get('content', '')[:80]}" for m in older
        )
        summary = {
            "role": "system",
            "content": f"[Compacted {len(older)} earlier messages] Summary: {older_text[:200]}...",
        }
        return [summary] + recent


def main():
    print("Context Compaction Demo\n")

    # Simulate a long conversation
    history = []
    for i in range(30):
        history.append({"role": "user", "content": f"Message {i}: " + "hello " * 10})
        history.append({"role": "assistant", "content": f"Response {i}: " + "ok " * 15})

    compactor = ContextCompactor(max_tokens=2000, keep_recent=5)
    total_chars = sum(len(m["content"]) for m in history)

    print(f"Original: {len(history)} messages, ~{total_chars} chars "
          f"(~{total_chars // 4} tokens)")

    if compactor.should_compact(history):
        compacted = compactor.compact(history)
        compacted_chars = sum(len(m["content"]) for m in compacted)
        print(f"Compacted: {len(compacted)} messages, ~{compacted_chars} chars "
              f"(~{compacted_chars // 4} tokens)")
        print(f"Savings: {(1 - compacted_chars/total_chars)*100:.0f}%")
        print(f"\nCompacted history structure:")
        for msg in compacted:
            role = msg["role"].upper()
            preview = msg["content"][:80]
            print(f"  [{role}] {preview}...")
    else:
        print("No compaction needed (under budget)")


if __name__ == "__main__":
    main()
