STORY_PROMPT = """
You are a formatter that outputs ONLY JSON matching the provided schema.

Hard rules (must follow):
- Output must be a single valid JSON object with no extra text, no prose, no Markdown, and no code fences.
- Do not include comments or trailing commas.
- Booleans must be true/false.
- Every non-ending node must have 2–3 options; ending nodes must have no options field.
- Depth 3–4 levels from the root, with varied path lengths.
- At least one winning ending (isWinningEnding: true).

Return EXACTLY one JSON object that conforms to the schema:
{format_instructions}
"""
json_structure = """
        {
            "title": "Story Title",
            "rootNode": {
                "content": "The starting situation of the story",
                "isEnding": false,
                "isWinningEnding": false,
                "options": [
                    {
                        "text": "Option 1 text",
                        "nextNode": {
                            "content": "What happens for option 1",
                            "isEnding": false,
                            "isWinningEnding": false,
                            "options": [
                                // More nested options
                            ]
                        }
                    },
                    // More options for root node
                ]
            }
        }
        """