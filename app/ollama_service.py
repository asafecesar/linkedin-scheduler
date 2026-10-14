import json
import re
import time
import httpx
from typing import Dict, Any, List, Optional
from app import database as db

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:14b"

LINKEDIN_CREATOR_ROLE_PROMPT = """You are an elite LinkedIn Content Creator and Executive Tech Ghostwriter specializing in the Canadian Technology Ecosystem, particularly the Ottawa & Kanata North tech hub (Canada's largest technology park) and North American IT leadership.

PRIMARY DIRECTIVE:
ALWAYS write strictly in natural, high-signal North American English. Tailor insights, lessons, and terminology to software engineers, tech leads, engineering managers, and tech founders in the Ottawa / Canadian tech sector (Enterprise SaaS, GovTech / Public Sector digital modernization, Cloud Infrastructure, Telecom & 5G, Cybersecurity, and AI engineering).

CRITICAL LINKEDIN WRITING RULES:
1. THE HOOK (Lines 1-2):
   - The opening line must stop the scroll before the "...see more" fold.
   - NEVER open with AI clichés or corporate jargon: "In today's fast-paced world", "I am thrilled to announce", "In the realm of", "Game-changer", "Let's dive in", "Unlocking leverage".
   - Open with a counter-intuitive observation, a concrete metric, a battle-tested rule, or an honest engineering lesson learned the hard way.
2. MOBILE-FIRST FORMATTING:
   - Ultra-readable: 1-2 sentences per paragraph with clean blank lines between thoughts.
   - Use clean bullets (• or → or numbered lists) for frameworks and steps.
   - Avoid walls of text.
3. AUTHENTIC ENGINEERING & LEADERSHIP VALUE:
   - Speak peer-to-peer as a senior builder sharing real production trade-offs, architecture decisions, developer productivity, or tech career lessons.
   - Practical, pragmatic, and relatable to Canadian tech teams and builders.
4. ENGAGEMENT CLOSER:
   - Conclude with an authentic, open-ended question that prompts thoughtful replies from fellow engineers, managers, and tech peers.
5. NATURAL PROFESSIONAL TONE:
   - Maintain a confident, clear, and grounded tone without sounding overly academic or overly casual.
   - Write like a seasoned professional sharing hard-earned insights.
6. ABSOLUTELY ZERO MARKDOWN BOLD OR ASTERISKS:
   - The LinkedIn feed DOES NOT render Markdown asterisks. Double asterisks like **Reliability**: look like raw AI copy-pastes.
   - NEVER use double asterisks (**). Instead, use clean Unicode bullets: "• Reliability: ..." or "1. Reliability: ...".
   - Keep formatting clean, natural, and human."""

def sanitize_linkedin_text(text: str) -> str:
    if not text:
        return ""
    # Remove markdown bold **word** -> word
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove markdown headers like ###
    cleaned = re.sub(r'^#{1,6}\s*', '', cleaned, flags=re.MULTILINE)
    # Clean up any rogue double asterisks
    cleaned = cleaned.replace("**", "").replace("__", "")
    return cleaned.strip()

def get_ollama_config() -> Dict[str, str]:
    base_url = db.get_setting("ollama_base_url", DEFAULT_OLLAMA_URL).strip() or DEFAULT_OLLAMA_URL
    model = db.get_setting("ollama_model", DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL
    return {"base_url": base_url.rstrip("/"), "model": model}

_status_cache: Dict[str, Any] = {"time": 0.0, "data": None}
_is_busy: bool = False

async def check_ollama_status() -> Dict[str, Any]:
    global _status_cache
    config = get_ollama_config()
    now = time.time()

    # If currently generating or checked within last 15s, return fast
    if _is_busy:
        return {
            "online": True,
            "base_url": config["base_url"],
            "current_model": config["model"],
            "available_models": _status_cache["data"].get("available_models", []) if _status_cache["data"] else [],
            "model_count": 1,
            "status": "generating"
        }

    if _status_cache["data"] and (now - _status_cache["time"] < 15.0):
        return _status_cache["data"]

    try:
        timeout = httpx.Timeout(connect=2.0, read=2.0, write=2.0, pool=2.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            res = await client.get(f"{config['base_url']}/api/tags")
            if res.status_code == 200:
                data = res.json()
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                result = {
                    "online": True,
                    "base_url": config["base_url"],
                    "current_model": config["model"],
                    "available_models": models,
                    "model_count": len(models)
                }
                _status_cache = {"time": now, "data": result}
                return result
    except Exception as e:
        if _status_cache["data"]:
            return _status_cache["data"]
        return {
            "online": False,
            "base_url": config["base_url"],
            "current_model": config["model"],
            "available_models": [],
            "error": str(e)
        }
    return {
        "online": False,
        "base_url": config["base_url"],
        "current_model": config["model"],
        "available_models": []
    }

async def call_ollama(prompt: str, system_instruction: str = "", format_json: bool = True) -> str:
    global _is_busy
    config = get_ollama_config()
    full_system = f"{LINKEDIN_CREATOR_ROLE_PROMPT}\n\n{system_instruction}".strip()

    payload: Dict[str, Any] = {
        "model": config["model"],
        "prompt": prompt,
        "system": full_system,
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_ctx": 4096
        }
    }

    if format_json:
        payload["format"] = "json"

    _is_busy = True
    try:
        async with httpx.AsyncClient(timeout=150.0) as client:
            try:
                res = await client.post(
                    f"{config['base_url']}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                if res.status_code != 200:
                    raise Exception(f"Ollama returned status {res.status_code}: {res.text}")

                data = res.json()
                response_text = data.get("response", "")
                if not response_text:
                    raise Exception("Ollama returned an empty response.")
                return response_text
            except httpx.ConnectError:
                raise Exception(f"Could not connect to Ollama at {config['base_url']}. Make sure 'ollama serve' is running.")
            except Exception as e:
                raise Exception(f"Error calling Ollama ({config['model']}): {str(e)}")
    finally:
        _is_busy = False

def clean_json_response(raw_text: str) -> str:
    cleaned = raw_text.strip()
    # Match markdown code block first
    code_block = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned, flags=re.IGNORECASE)
    if code_block:
        cleaned = code_block.group(1).strip()

    # Find first { or [ to last } or ]
    first_brace = cleaned.find('{')
    first_bracket = cleaned.find('[')
    candidates = [idx for idx in (first_brace, first_bracket) if idx != -1]
    if candidates:
        start = min(candidates)
        last_brace = cleaned.rfind('}')
        last_bracket = cleaned.rfind(']')
        end = max(last_brace, last_bracket)
        if end > start:
            cleaned = cleaned[start:end + 1]

    return cleaned.strip()

def extract_or_normalize_hashtags(content: str, hashtags_list: Optional[List[str]] = None, topic: str = "") -> List[str]:
    tags = []
    if hashtags_list and isinstance(hashtags_list, list):
        for h in hashtags_list:
            if isinstance(h, str):
                cleaned = re.sub(r'[^a-zA-Z0-9_]', '', h)
                if cleaned:
                    tags.append(f"#{cleaned}")

    if not tags and content:
        found = re.findall(r'#([a-zA-Z0-9_]+)', content)
        for f in found:
            tags.append(f"#{f}")

    if not tags:
        words = [w.capitalize() for w in re.findall(r'[a-zA-Z0-9]+', topic) if len(w) > 3]
        if words:
            tags.append(f"#{''.join(words[:2])}")
        tags.extend(["#SoftwareEngineering", "#TechLeadership", "#OttawaTech"])

    # Deduplicate while preserving order (max 5 tags)
    unique_tags = []
    for t in tags:
        if t.lower() not in [ut.lower() for ut in unique_tags]:
            unique_tags.append(t)
    return unique_tags[:5]

async def generate_batch_posts_ollama(
    topic: str,
    count: int = 3,
    angle: str = "Practical Insight",
    custom_notes: str = ""
) -> Dict[str, Any]:
    system_instruction = """STYLE & TONE DIRECTIVE:
- Tone: Pragmatic, direct, peer-to-peer engineer and technology leader.
- Formatting: 1-2 sentence paragraphs with clean blank lines between thoughts.
- Bullets: Use clean Unicode bullets (• or →).
- ZERO MARKDOWN BOLD: NEVER use double asterisks (**).
- HASHTAGS: Include 3 to 5 highly relevant, high-visibility LinkedIn hashtags (e.g. #SoftwareEngineering #AIDevelopment #OttawaTech #CloudArchitecture) at the bottom of the post.
- Language: Strictly natural North American English tailored to the Ottawa / Canadian tech ecosystem."""

    prompt = f"""As a LinkedIn Content Creator & Tech Ghostwriter for the Ottawa/Canadian tech market, write {count} distinct, high-impact LinkedIn post variations based on the following topic.

CRITICAL MANDATORY INSTRUCTION:
- You MUST write the final hook and content 100% IN ENGLISH.
- Even if the topic or input notes are written in Portuguese or French, TRANSLATE THE ESSENCE AND WRITE THE POST FULLY IN ENGLISH for the Canadian/Ottawa IT market.
- NEVER output Portuguese text in the generated posts.
- Suggest 3-5 relevant LinkedIn hashtags in the 'hashtags' array and append them at the end of the post content.

TOPIC / CORE IDEA:
{topic}

CONTENT ANGLE / LENS:
{angle}

ADDITIONAL NOTES & CONSTRAINTS:
{custom_notes or 'None'}

Return your response STRICTLY as a valid JSON object with a 'posts' array of objects (no markdown wrapping):
{{
  "posts": [
    {{
      "hook": "The opening 1-2 magnetic lines written in English before the '...see more' fold",
      "content": "The full post text written strictly in English, formatted with double line breaks between short sentences, clean bullets, an engaging closing question, and the hashtags at the end",
      "hashtags": ["#SoftwareEngineering", "#AIDevelopment", "#OttawaTech"],
      "angle": "{angle}",
      "estimated_read_time": "1 min"
    }}
  ]
}}"""

    raw = await call_ollama(prompt, system_instruction, format_json=False)
    cleaned = clean_json_response(raw)

    try:
        parsed = json.loads(cleaned)
        posts_list = parsed.get("posts", []) if isinstance(parsed, dict) else parsed
        if isinstance(posts_list, list) and len(posts_list) > 0:
            for p in posts_list:
                tags = extract_or_normalize_hashtags(p.get("content", ""), p.get("hashtags", []), topic)
                p["hashtags"] = tags
                p["angle"] = p.get("angle") or angle
                p["estimated_read_time"] = p.get("estimated_read_time") or "1 min"

                raw_c = sanitize_linkedin_text(p.get("content", "")).rstrip()
                # Clean any loose trailing hashtags at the bottom to avoid duplication
                c_lines = raw_c.split("\n")
                while c_lines and (not c_lines[-1].strip() or all(word.startswith("#") for word in c_lines[-1].strip().split())):
                    c_lines.pop()
                raw_c = "\n".join(c_lines).rstrip()

                tag_block = " ".join(tags)
                if tag_block:
                    p["content"] = f"{raw_c}\n\n{tag_block}"
                else:
                    p["content"] = raw_c

                if "hook" in p:
                    p["hook"] = sanitize_linkedin_text(p["hook"])
            return {"posts": posts_list, "is_mock": False, "provider": "ollama"}
    except Exception as e:
        print(f"[Ollama] Failed to parse JSON: {e}. Raw: {cleaned[:200]}")

    # Fallback to direct call parsing
    fallback_tags = extract_or_normalize_hashtags(cleaned, [], topic)
    tag_str = " ".join(fallback_tags)
    fallback_content = sanitize_linkedin_text(cleaned)
    if tag_str and not any(t.lower() in fallback_content.lower() for t in fallback_tags):
        fallback_content = f"{fallback_content.rstrip()}\n\n{tag_str}"

    return {
        "posts": [
            {
                "hook": f"What most engineering teams overlook when it comes to {topic}:",
                "content": fallback_content,
                "hashtags": fallback_tags,
                "angle": angle,
                "estimated_read_time": "1 min"
            }
        ],
        "is_mock": False,
        "provider": "ollama"
    }

async def refine_post_ollama(content: str, instruction: str) -> str:
    system_instruction = """STYLE & REFINEMENT DIRECTIVE:
- Tone: Pragmatic, direct, engineer-to-engineer.
- Language: English (North American tech market).
- Formatting: NO markdown double asterisks (**). Use clean plain text and Unicode bullets (•).
- Hashtags: Preserve or enhance the 3-5 relevant LinkedIn hashtags at the bottom of the post."""

    prompt = f"""As a LinkedIn Content Creator for tech leaders in the Ottawa/Canadian IT market, refine the following post according to the author's instructions.
Keep it strictly in English with punchy line breaks, an authentic peer-to-peer tone, and relevant hashtags at the bottom.
NEVER use double asterisks (**) around words. Use clean plain text or bullets (•).

CURRENT POST:
{content}

REFINEMENT INSTRUCTION:
{instruction}

Return ONLY the refined post text in English. Do not add intro text, quotes, or markdown code blocks."""

    raw = await call_ollama(prompt, system_instruction, format_json=False)
    return sanitize_linkedin_text(raw)
