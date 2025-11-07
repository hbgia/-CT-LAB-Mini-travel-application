import json
import requests
from typing import List, Optional

DEFAULT_TIMEOUT = 300


def build_prompt(origin: str, destination: str, start_date: str, end_date: str, interests: List[str], pace: List[str]) -> str:
    """Builds the LLM prompt from user inputs.

    Kept concise and explicit to match original behavior.
    """
    return (
        f"You are a concise travel planner. Input: Origin: {origin}, Destination: {destination}, "
        f"Dates: {start_date} to {end_date}, Interests: {interests}, Pace: {pace}. "
        "Output: Return a markdown-like plain text of a day-by-day itinerary (morning/afternoon/evening) "
        "with short explanations. If interest not available, suggest reasonable alternative. No comment."
    )


def call_pg_api(pg_link: str, data: dict, timeout: int = DEFAULT_TIMEOUT) -> requests.Response:
    """
    Sends the POST request to the provisioning/gateway link and returns a Response.

    Raises requests.exceptions.RequestException on network/HTTP errors.
    """
    r = requests.post(pg_link, json=data, timeout=timeout)
    r.raise_for_status()
    return r


def unquote_json_string(s: str) -> str:
    """
    If s is a quoted JSON string literal (e.g. '"# Title\\n..."'), unquote it.

    Otherwise return the original string.
    """
    s_strip = s.strip()
    if (s_strip.startswith('"') and s_strip.endswith('"')) or (s_strip.startswith("'") and s_strip.endswith("'")):
        try:
            unq = json.loads(s_strip)
            if isinstance(unq, str):
                return unq
        except Exception:
            # If unquoting fails, keep original string
            pass
    return s


def extract_text_from_response(r: requests.Response) -> Optional[str]:
    """
    Extract a Markdown/plain-text answer from the response.

    Tries common JSON keys first, then falls back to the first string value in the JSON
    object, then to the raw response text. Also unquotes JSON-encoded string literals.
    """
    llm_text: Optional[str] = None
    try:
        resp_json = r.json()
    except ValueError:
        resp_json = None

    if resp_json is not None:
        if isinstance(resp_json, dict):
            for key in ("response", "result", "output", "text", "data", "message"):
                val = resp_json.get(key)
                if isinstance(val, str) and val.strip():
                    llm_text = val
                    break
            if llm_text is None:
                for v in resp_json.values():
                    if isinstance(v, str) and v.strip():
                        llm_text = v
                        break
        elif isinstance(resp_json, str):
            llm_text = resp_json

    if llm_text is None:
        # fallback to raw text body
        llm_text = r.text

    if isinstance(llm_text, str):
        llm_text = unquote_json_string(llm_text)

    return str(llm_text) if llm_text is not None else None


def build_chat_prompt(origin: str, destination: str, start_date: str, end_date: str, interests: List[str], pace: List[str], user_message: Optional[str], history: Optional[List[dict]] = None) -> str:
    """
    Build a prompt suitable for a continuation chat: include travel context then conversation history
    and the latest user message.
    History is expected as a list of {'role': 'user'|'assistant', 'content': str}.
    """
    base = (
        "You are a concise travel assistant. Context: "
        + f"Origin: {origin}, Destination: {destination}, Dates: {start_date} to {end_date}, "
        + f"Interests: {interests}, Pace: {pace}."
    )

    conv = ""
    if history:
        for m in history:
            role = m.get('role', 'user')
            content = m.get('content', '')
            if role == 'user':
                conv += f"User: {content}\n"
            else:
                conv += f"Assistant: {content}\n"

    # append the newest user message
    conv += f"User: {user_message}\nAssistant:"

    return base + "\n\nConversation:\n" + conv + "\nRespond concisely and helpfully."


def get_LLM_response(pinggy_link: str, origin: str, destination: str, start_date: str, end_date: str, interests: List[str], pace: List[str], user_message: Optional[str] = None, history: Optional[List[dict]] = None):
    """
    Public wrapper: builds prompt (plan or chat), calls the API, extracts text and returns it.
    If user_message is provided, a chat-style prompt is built using history and user_message.
    """
    if user_message:
        prompt = build_chat_prompt(origin, destination, start_date, end_date, interests, pace, user_message, history)
    else:
        prompt = build_prompt(origin, destination, start_date, end_date, interests, pace)

    data = {
        "model": "gpt-oss:20b",
        # "model": "gemma:2b", # faster model but more limited
        "prompt": prompt,
        "stream": False,
    }

    try:
        r = call_pg_api(pinggy_link, data)
        return extract_text_from_response(r)
    except requests.exceptions.RequestException as e:
        return "[ERROR]: " + str(e)