import time

from ..config import GEMINI_API_KEY, GEMINI_MODEL, LLM_PROVIDER


class LLMProvider:
    def generate(self, prompt: str) -> str:
        if LLM_PROVIDER == "gemini" and GEMINI_API_KEY:
            return self._gemini(prompt)
        return self._mock_answer(prompt)

    def _gemini(self, prompt: str) -> str:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = model.generate_content(prompt)
                return response.text or "The model returned an empty answer."
            except Exception as exc:
                last_error = exc
                time.sleep(2**attempt)
        raise RuntimeError(f"LLM request failed: {last_error}")

    def _mock_answer(self, prompt: str) -> str:
        markers = [line.split("]", 1)[0] + "]" for line in prompt.splitlines() if line.startswith("[chunk:")]
        marker_text = " ".join(markers[:3])
        return (
            "LLM provider is not configured, so this is a retrieval preview. "
            "Use the cited chunks as grounded evidence. "
            f"{marker_text}"
        ).strip()


def get_llm_provider() -> LLMProvider:
    return LLMProvider()
