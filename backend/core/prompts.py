STORY_PROMPT = """
You are a formatter that outputs ONLY JSON matching the provided schema.

STRICTLY FOLLOW THESE RULES (must follow):
- Output must be a single valid JSON object with no extra text, no prose, no Markdown, and no code fences.
- Do not include comments or trailing commas.
- Booleans must be true/false.
- Every non-ending node MUST have EXACTLY 2(THAT's IMPORTANT, LESS THAN 2 IS NOT ACCEPTED) options; ending nodes must have no options field.
- Depth 4 levels from the root, with varied path lengths.
- At least one winning ending (isWinningEnding: true).

IMAGE PROMPT RULE (must follow):
- For EVERY story node (including root and nested nodes), you must include two distinct fields: 'image_prompt_1' and 'image_prompt_2'.
- Each prompt MUST be a detailed, visual description (maximum 20 words) of the scene described in the 'content' field.
- 'image_prompt_1' and 'image_prompt_2' must be DIFFERENT from each other.

Return EXACTLY one JSON object that conforms to the schema:
{format_instructions}
"""
json_structure = """
        {
            "title": "Story Title",
            "rootNode": {
                "content": "The starting situation of the story",
                "image_prompt_1": "A lone pirate ship sailing under a stormy sky, cinematic lighting.",
                "image_prompt_2": "Close-up of a weathered, leather-bound map resting on a ship's wheel.",
                "isEnding": false,
                "isWinningEnding": false,
                "options": [
                    {
                        "text": "Option 1 text",
                        "nextNode": {
                            "content": "What happens for option 1",
                            "image_prompt_1": "A mysterious glowing cave entrance, fantasy art.",
                            "image_prompt_2": "Two frightened sailors looking into the dark opening of a cave.",
                            "isEnding": false,
                            "isWinningEnding": false,
                            "options": [
                                // More nested options
                            ]
                        }
                    },
                    {
                        "text": "Option 2 text",
                        "nextNode": {
                            // ...
                        }
                    }
                ]
            }
        }
        """