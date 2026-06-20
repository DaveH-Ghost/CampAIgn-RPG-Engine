"""Rough prompt token estimates for UI hints (V0.4.2)."""


def estimate_prompt_tokens(text: str) -> int:
    """
    Approximate input tokens for English prose (~4 characters per token).

    Not model-exact; good enough for hover hints before Run turn.
    """
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)
