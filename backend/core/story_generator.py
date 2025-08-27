import json
import logging
import re
from typing import Any, Dict, Optional


from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


from core.prompts import STORY_PROMPT
from models.story import Story, StoryNode
from core.models import StoryLLMResponse, StoryNodeLLM
from core.euriai_client import EuriaiChat
from core.config import settings


logger = logging.getLogger("app.story")



class StoryGenerator:


    @classmethod
    def _get_llm(cls):
        api_key = settings.EURI_API_KEY or settings.CHOREO_OPENAI_CONNECTION_OPENAI_API_KEY
        base_url = settings.EURI_BASE_URL or settings.CHOREO_OPENAI_CONNECTION_SERVICEURL
        model = settings.EURI_MODEL or "gpt-4.1-nano"
        return EuriaiChat(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.2,
            max_tokens=1400,
        )


    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "fantasy", user_id: Optional[int] = None) -> Story:
        """
        1) Call Euriai and get assistant content (JSON string or dict)
        2) Convert to dict robustly (unfence, unescape, cleanup)
        3) Normalize schema drift (key typos, null options, ending rules)
        4) Validate and persist
        """
        try:
            llm = cls._get_llm()
            strict_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", STORY_PROMPT),
                    ("user", f"Create the story with this theme: {theme}. Respond with JSON only.")
                ]
            ).partial(format_instructions=strict_parser.get_format_instructions())

            # 1) Call model; client returns assistant message.content in .content
            raw = llm.invoke(prompt.invoke({}))
            content = raw.content if hasattr(raw, "content") else str(raw)
            logger.debug("LLM raw response len=%d preview=%s", len(str(content)), str(content)[:500])

            # 2) Convert to dict robustly
            obj = cls._to_object(content)
            logger.debug("Parsed content to object type=%s keys=%s", type(obj).__name__, list(obj.keys())[:5] if isinstance(obj, dict) else "n/a")

            # 3) Normalize to schema
            obj = cls._normalize_top(obj)
            logger.debug("Normalized object keys=%s", list(obj.keys())[:5] if isinstance(obj, dict) else "n/a")

            # 4) Validate and persist
            story_structure = StoryLLMResponse.model_validate(obj)
            logger.debug("Pydantic validation successful")

            story_db = Story(
                title=story_structure.title, 
                session_id=session_id,
                user_id=user_id
            )
            db.add(story_db)
            db.flush()

            root_node_data = story_structure.rootNode
            if isinstance(root_node_data, dict):
                root_node_data = StoryNodeLLM.model_validate(root_node_data)

            cls._process_story_node(db, story_db.id, root_node_data, is_root=True)
            db.commit()
            logger.debug("Story generation completed successfully")
            return story_db
            
        except Exception as e:
            logger.error("Story generation failed: %s", str(e), exc_info=True)
            db.rollback()
            raise




    # ---------- Helpers: parsing and normalization ----------


    @staticmethod
    def _strip_fences(s: str) -> str:
        s2 = s.strip()
        if s2.startswith("```"):
            first_nl = s2.find("\n")
            s2 = s2[first_nl + 1 :] if first_nl != -1 else s2.lstrip("`")
            s2 = s2.rstrip("`").strip()
        return s2


    @classmethod
    def _to_object(cls, maybe_json_str_or_obj: Any) -> Dict[str, Any]:
        """
        Accept dict (return as-is) or string (strip code fences, unescape, json.loads with cleanup fallback).
        """
        if isinstance(maybe_json_str_or_obj, dict):
            return maybe_json_str_or_obj

        s = str(maybe_json_str_or_obj)
        s = cls._strip_fences(s)

        # If it's a quoted/escaped JSON string, try to unescape
        if (s.startswith('"') and s.endswith('"')) or '\\"' in s:
            try:
                unescaped = json.loads(s)
                if isinstance(unescaped, str):
                    s = unescaped
                else:
                    # Already an object/array; return it directly
                    return unescaped
            except Exception as e:
                logger.debug("Failed to unescape JSON: %s", e)
                s = s.replace('\\"', '"').replace('\\n', '\n')

        # Try strict JSON parsing first
        try:
            obj = json.loads(s)
            logger.debug("Successfully parsed JSON on first attempt")
            return obj
        except json.JSONDecodeError as e:
            logger.debug("Initial JSON parse failed: %s", e)
            
            # 🔧 FIX: Only apply regex cleanup to strings, not dicts
            if isinstance(s, str):
                logger.debug("Attempting JSON cleanup and retry")
                # Remove comments and trailing commas then retry
                s2 = re.sub(r"//.*", "", s)
                s2 = re.sub(r",\s*([}$])", r"\1", s2)
                
                try:
                    obj = json.loads(s2)
                    logger.debug("Successfully parsed JSON after cleanup")
                    return obj
                except json.JSONDecodeError as e2:
                    logger.error("JSON parsing failed even after cleanup. Original: %s, Cleaned: %s, Error: %s", 
                            s[:200], s2[:200], e2)
                    # Try to extract just the content between first { and last }
                    try:
                        first_brace = s.find('{')
                        last_brace = s.rfind('}')
                        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                            extracted = s[first_brace:last_brace+1]
                            obj = json.loads(extracted)
                            logger.debug("Successfully extracted and parsed JSON")
                            return obj
                    except Exception as e3:
                        logger.error("Failed to extract JSON: %s", e3)
                        raise RuntimeError(f"Could not parse JSON response: {e2}. Content preview: {s[:200]}")
            else:
                raise RuntimeError(f"Expected string for JSON parsing, got {type(s).__name__}")

        # Final validation
        if not isinstance(obj, dict):
            if isinstance(obj, list) and obj and isinstance(obj[0], dict):
                obj = obj[0]
            else:
                raise RuntimeError(f"Expected JSON object, got {type(obj).__name__}: {obj}")

        return obj


    @classmethod
    def _normalize_top(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure top-level has title and rootNode, and recursively normalize nodes.
        """
        # If wrapped or missing keys, try to pull inner object
        if "title" not in obj or "rootNode" not in obj:
            # 🔧 FIX: Handle Euriai data wrapper first
            if "data" in obj and isinstance(obj["data"], dict):
                obj = obj["data"]
                logger.debug("Extracted from Euriai 'data' wrapper")
            
            # If envelope leaked in somehow, try to drill down
            if "choices" in obj and isinstance(obj["choices"], list):
                try:
                    # 🔧 FIX: Access choices as LIST, not dict
                    first_choice = obj["choices"][0] if obj["choices"] else {}
                    msg = first_choice.get("message", {})
                    inner = msg.get("content", "")
                    if inner:
                        obj = cls._to_object(inner)
                        logger.debug("Extracted content from choices[0].message.content")
                except Exception as e:
                    logger.warning("Failed to extract from choices: %s", e)


        # If rootNode is a stringified JSON, decode it
        if isinstance(obj.get("rootNode"), str):
            try:
                obj["rootNode"] = json.loads(cls._strip_fences(obj["rootNode"]))
            except Exception:
                pass


        # Normalize root node
        if isinstance(obj.get("rootNode"), dict):
            obj["rootNode"] = cls._normalize_node(obj["rootNode"])


        return obj


    @classmethod
    def _normalize_node(cls, node: Dict[str, Any]) -> Dict[str, Any]:
        # Fix key typos/casing
        if "Nextnode" in node:
            node["nextNode"] = node.pop("Nextnode")
        if "nextnode" in node:
            node["nextNode"] = node.pop("nextnode")


        node.setdefault("isEnding", False)
        node.setdefault("isWinningEnding", False)


        if node["isEnding"]:
            node.pop("options", None)
        else:
            opts = node.get("options", None)
            if not isinstance(opts, list):
                node["options"] = []
            else:
                cleaned = []
                for opt in opts:
                    if not isinstance(opt, dict):
                        continue
                    text_val = opt.get("text") or opt.get("label") or opt.get("option")
                    nxt = opt.get("nextNode") or opt.get("Nextnode") or opt.get("nextnode")
                    if text_val and isinstance(nxt, dict):
                        cleaned.append({"text": text_val, "nextNode": cls._normalize_node(nxt)})
                node["options"] = cleaned


        return node


    # ---------- Persistence ----------


    @classmethod
    def _process_story_node(cls, db: Session, story_id: int, node_data: StoryNodeLLM, is_root: bool = False) -> StoryNode:
        content = node_data.content if hasattr(node_data, "content") else node_data["content"]
        is_ending = node_data.isEnding if hasattr(node_data, "isEnding") else node_data["isEnding"]
        is_winning_ending = (
            node_data.isWinningEnding if hasattr(node_data, "isWinningEnding") else node_data["isWinningEnding"]
        )


        node = StoryNode(
            story_id=story_id,
            content=content,
            is_root=is_root,
            is_ending=is_ending,
            is_winning_ending=is_winning_ending,
            options=[],
        )
        db.add(node)
        db.flush()


        opts = getattr(node_data, "options", None)
        if not is_ending and opts:
            options_list = []
            for opt in opts:
                next_n = opt.nextNode if hasattr(opt, "nextNode") else opt.get("nextNode")
                if isinstance(next_n, dict):
                    next_n = StoryNodeLLM.model_validate(next_n)
                child = cls._process_story_node(db, story_id, next_n, is_root=False)
                options_list.append({"text": opt.text if hasattr(opt, "text") else opt.get("text"), "node_id": child.id})
            node.options = options_list


        db.flush()
        return node