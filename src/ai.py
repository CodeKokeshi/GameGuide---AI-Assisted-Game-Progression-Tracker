# -*- coding: utf-8 -*-
"""
AI Management Module

Handles all AI provider interactions and guide generation logic.
"""

import json
import time
import requests


class AIManager:
    """Manages AI provider interactions and guide generation"""
    
    def __init__(self):
        self.gemini_models = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-exp",
            "gemini-2.5-latest",
            "gemini-2.5-lite",
            "gemini-2.5-lite-latest",
            "gemini-flash-latest",
            "gemini-flash-lite-latest",
            "gemini-2.0-flash",
            "gemini-2.0-flash-exp",
            "gemini-2.5-pro",
        ]
        self.default_fallback = "No reliable hint could be confirmed from the available guides."
    
    def call_ai_api(self, game_title, situation, objective, behavior, api_key, provider, status_callback=None):
        """Call AI API to generate guide hint"""
        
        # Build a more specific prompt for better search results
        if objective:
            # If we have an objective, focus on that
            search_query = f"{game_title} walkthrough guide {situation} {objective}"
            main_question = f"In the game '{game_title}', the player's current situation is: {situation}. Their immediate objective is: {objective}."
        else:
            # If no objective, just use the situation
            search_query = f"{game_title} walkthrough guide {situation}"
            main_question = f"In the game '{game_title}', the player's current situation is: {situation}."
        
        def log(message):
            if status_callback and message:
                status_callback(message)

        refined_context = ""
        if provider == "Gemini":
            refined_context = self._refine_context_gemini(
                game_title=game_title,
                situation=situation,
                objective=objective,
                behavior=behavior,
                api_key=api_key,
                search_query=search_query,
                status_callback=log,
            )

        # Build the user prompt
        prompt_parts = [main_question]

        if refined_context:
            prompt_parts.append(
                "Verified context from walkthrough research: "
                f"{refined_context}"
            )
            prompt_parts.append(
                "Cross-check this researched context against the player's own words before making your response."
            )
        
        if behavior:
            # If there's special behavior instruction, add it
            prompt_parts.append(behavior)
        else:
            # Standard question
            prompt_parts.append("Search online game guides and walkthroughs to find: What is the EXACT next step the player should take right now?")
            prompt_parts.append("Provide ONLY the immediate, actionable next step. Be specific and concise.")
        
        if not behavior:
            prompt_parts.append("If you find conflicting information, provide the most commonly recommended solution.")
        
        user_prompt = " ".join(prompt_parts)
        
        # Enhanced system prompt for accuracy - adjusted based on behavior
        if behavior and "strategic" in behavior.lower():
            system_prompt = f"""You are an expert video game guide assistant. Provide comprehensive strategic guidance based on REAL game walkthroughs and guides found online.

IMPORTANT INSTRUCTIONS:
1. Search the internet for "{search_query}" to find accurate walkthrough information
2. Use ONLY information from actual game guides, walkthroughs, and wikis
3. Provide strategic breakdown with context and planning
4. Be specific with locations, items, or actions
5. Structure your response according to the user's request
6. Do NOT make up information - only use what you find in guides

Focus on accuracy and helpful structure."""
        elif behavior and "context" in behavior.lower():
            system_prompt = f"""You are an expert video game guide assistant. Analyze the player's position in the game based on REAL walkthroughs and guides found online.

IMPORTANT INSTRUCTIONS:
1. Search the internet for "{search_query}" to find accurate walkthrough information
2. Use ONLY information from actual game guides, walkthroughs, and wikis
3. Focus on explaining WHERE they are in the game's progression
4. Provide context about what comes before and after
5. Do NOT just tell them what to do next - explain their situation
6. Do NOT make up information - only use what you find in guides

Focus on contextual understanding over direction."""
        elif behavior and "tips" in behavior.lower() or behavior and "tricks" in behavior.lower():
            system_prompt = f"""You are an expert video game guide assistant specializing in tips, tricks, and optimization. Provide helpful secrets and strategies based on REAL game guides and community knowledge.

IMPORTANT INSTRUCTIONS:
1. Search the internet for "{search_query}" along with terms like "tips", "tricks", "secrets", "exploits"
2. Use information from game guides, wikis, and community resources
3. Focus on optimization, shortcuts, and advantages
4. Include hidden content and secret techniques
5. Provide practical tips the player can use immediately
6. Do NOT make up information - only use what you find

Focus on giving them an edge."""
        else:
            system_prompt = f"""You are an expert video game guide assistant. Your task is to provide accurate, actionable guidance based on REAL game walkthroughs and guides found online.

IMPORTANT INSTRUCTIONS:
1. Search the internet for "{search_query}" to find accurate walkthrough information
2. Use ONLY information from actual game guides, walkthroughs, and wikis
3. Provide the IMMEDIATE next step - not general advice
4. Be specific with locations, items, or actions
5. If multiple solutions exist, mention the most common one
6. Do NOT make up information - only use what you find in guides
7. Keep your response concise (2-3 sentences max)

Focus on accuracy over creativity. The player needs reliable information."""
        
        guides = []
        evaluation = {}
        active_model = None

        if provider == "Gemini":
            attempts_per_model = 3
            delay_seconds = 1.5
            last_error = None

            log("Starting Gemini guide generation with fallback models...")

            for model_name in self.gemini_models:
                log(f"Trying model '{model_name}'...")
                model_guides = []
                fallback_guide = None

                try:
                    for attempt in range(attempts_per_model):
                        batch = self._call_gemini_api(
                            user_prompt,
                            system_prompt,
                            api_key,
                            model_name=model_name,
                            status_callback=log,
                            fallback_text=self.default_fallback,
                        )

                        for guide in batch:
                            text = (guide.get("text", "") or "").strip()
                            if not text:
                                continue

                            if text == self.default_fallback:
                                if not fallback_guide:
                                    fallback_guide = guide
                                continue

                            model_guides.append(guide)
                            if len(model_guides) >= attempts_per_model:
                                break

                        if len(model_guides) >= attempts_per_model:
                            break

                        if attempt < attempts_per_model - 1:
                            time.sleep(delay_seconds)

                except Exception as exc:
                    last_error = exc
                    log(f"Model '{model_name}' failed: {exc}")
                    continue

                if not model_guides and fallback_guide:
                    model_guides.append(fallback_guide)

                if model_guides:
                    guides = model_guides[:attempts_per_model]
                    active_model = model_name
                    log(f"Model '{model_name}' succeeded with {len(guides)} guide(s).")

                    if guides:
                        log("Running reliability evaluation...")
                        try:
                            evaluation = self._evaluate_gemini_guides(
                                game_title=game_title,
                                situation=situation,
                                objective=objective,
                                behavior=behavior,
                                guides=guides,
                                api_key=api_key,
                                model_name=model_name,
                                status_callback=log
                            )
                        except Exception as eval_exc:
                            log(f"Evaluation step failed: {eval_exc}")
                            evaluation = {}

                    break
                else:
                    log(f"Model '{model_name}' returned no guidance.")

            if not guides:
                raise last_error or Exception("All Gemini models failed to provide guidance.")

        elif provider == "ChatGPT":
            log("Sending request to ChatGPT...")
            text = self._call_openai_api(user_prompt, system_prompt, api_key)
            cleaned = text.strip()
            if cleaned:
                guides.append({"text": cleaned, "sources": []})
                log("Received response from ChatGPT.")

        elif provider == "Claude":
            log("Sending request to Claude...")
            text = self._call_claude_api(user_prompt, system_prompt, api_key)
            cleaned = text.strip()
            if cleaned:
                guides.append({"text": cleaned, "sources": []})
                log("Received response from Claude.")

        else:
            raise ValueError("Please select a supported AI provider (Gemini, ChatGPT, or Claude).")

        return {
            "guides": guides,
            "provider": provider,
            "evaluation": evaluation,
            "model_used": active_model if provider == "Gemini" else None,
            "refined_context": refined_context,
        }
    
    def _refine_context_gemini(self, game_title, situation, objective, behavior, api_key, search_query, status_callback=None):
        """Gather additional context from guides before generating next steps"""

        if status_callback:
            status_callback("Refining player request using walkthrough research...")

        objective_text = objective if objective else "Not specified"
        behavior_text = behavior if behavior else "No special behavior requests"

        user_prompt = (
            "The player supplied the following notes while playing '{game_title}':\n"
            "• Situation: {situation}\n"
            "• Immediate objective: {objective_text}\n"
            "• Special behavior: {behavior_text}\n\n"
            "Search trusted walkthroughs for '{search_query}' and summarise what section of the game these notes describe."
            " Identify the named locations, quest or chapter titles, key NPCs, and any critical items already involved."
            " Provide the summary as 2-4 bullet points. Do NOT describe the next step or solution yet; focus only on clarifying the context."
        ).format(
            game_title=game_title,
            situation=situation,
            objective_text=objective_text,
            behavior_text=behavior_text,
            search_query=search_query,
        )

        system_prompt = (
            "You are an assistant verifying the player's description before offering help."
            " Use Google Search to cross-check reliable game guides."
            " Return concise bullet points that clarify what part of the game the player is referencing."
            " Do not invent new information and do not provide the next action."
        )

        try:
            results = self._call_gemini_api(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                api_key=api_key,
                model_name=self.gemini_models[0],
                status_callback=status_callback,
                fallback_text=None,
            )
        except Exception as exc:
            if status_callback:
                status_callback(f"Context refinement skipped: {exc}")
            return ""

        for candidate in results:
            text = (candidate.get("text", "") or "").strip()
            if text:
                return text

        return ""

    def _call_gemini_api(self, user_prompt, system_prompt, api_key, model_name, status_callback=None, fallback_text=None):
        """Call Google Gemini API with Google Search grounding"""
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "tools": [{"google_search": {}}],  # Enable Google Search grounding
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "candidateCount": 1,
                "temperature": 0.3,  # Lower temperature for more factual responses
                "topP": 0.8,
                "topK": 20,
                "maxOutputTokens": 500
            }
        }

        max_retries = 3
        backoff_seconds = 2.0
        response = None

        for attempt in range(max_retries):
            if status_callback:
                status_callback(f"Sending request to '{model_name}' (attempt {attempt + 1}/{max_retries})...")
            try:
                response = requests.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=30
                )
            except requests.RequestException as exc:
                if attempt < max_retries - 1:
                    if status_callback:
                        status_callback(f"Request to '{model_name}' failed ({exc}). Retrying...")
                    time.sleep(backoff_seconds * (attempt + 1))
                    continue
                raise Exception(f"Failed to reach Gemini API: {exc}") from exc

            if response.status_code == 200:
                break

            if response.status_code in (429, 500, 502, 503) and attempt < max_retries - 1:
                if status_callback:
                    status_callback(f"Received {response.status_code} from '{model_name}'. Retrying after backoff...")
                time.sleep(backoff_seconds * (attempt + 1))
                continue

            raise Exception(f"API returned status {response.status_code}: {response.text}")

        if response is None:
            raise Exception("No response from Gemini API.")

        result = response.json()

        guides = []
        candidates = result.get("candidates", [])

        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [{}])
            text = parts[0].get("text", "").strip()

            if not text:
                continue

            # Extract sources if available
            grounding_metadata = candidate.get("groundingMetadata", {})
            attributions = grounding_metadata.get("groundingAttributions", [])

            sources = set()
            seen_uris = set()
            for attr in attributions:
                web = attr.get("web", {})
                title = web.get("title", "").strip()
                uri = web.get("uri", "").strip()
                if not uri or uri in seen_uris:
                    continue
                seen_uris.add(uri)
                if title:
                    sources.add(f"{title} — {uri}")
                else:
                    sources.add(uri)

            guides.append({
                "text": text,
                "sources": list(sources)
            })

        if not guides and fallback_text:
            guides.append({
                "text": fallback_text,
                "sources": []
            })

        return guides

    def _evaluate_gemini_guides(self, game_title, situation, objective, behavior, guides, api_key, model_name, status_callback=None):
        """Ask Gemini to pick the most reliable guide hint"""
        if not guides:
            return {}

        objective_text = objective if objective else "Not specified."
        behavior_text = behavior if behavior else "No special behavior requests."

        guide_lines = []
        for idx, guide in enumerate(guides, start=1):
            text = (guide.get("text", "") or "").strip().replace("\\n", " ")
            sources = guide.get("sources", [])
            source_text = "; ".join(sources) if sources else "No sources provided."
            guide_lines.append(f"Guide {idx}:\\nHint: {text}\\nSources: {source_text}")

        guides_block = "\\n\\n".join(guide_lines)

        user_prompt = f"""You are verifying hints for the game '{game_title}'.
Current situation: {situation}
Immediate objective: {objective_text}
Special behavior requests: {behavior_text}

Three candidate hints were gathered from web searches:

{guides_block}

Determine which hint is the most reliable immediate next step. If none of the hints look trustworthy, indicate that.
Respond STRICTLY with JSON matching this schema:
{{
  "recommended_index": <integer from 1 to {len(guides)} indicating which hint to follow, or 0 if none>,
  "confidence": <integer 0-100 indicating certainty>,
  "reasoning": "<brief justification in one or two sentences>"
}}
Do not wrap the JSON with additional commentary."""

        system_prompt = """You are a quality assurance expert for video game walkthroughs.
Cross-check hints with known guides and select the most reliable immediate action.
Return only valid JSON that matches the requested schema."""

        evaluation_results = self._call_gemini_api(
            user_prompt,
            system_prompt,
            api_key,
            model_name,
            status_callback=status_callback,
            fallback_text=None
        )
        if not evaluation_results:
            return {}

        raw_text = evaluation_results[0].get("text", "").strip()
        if not raw_text:
            return {}

        cleaned_text = raw_text.strip()

        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
            if cleaned_text.lower().startswith("json"):
                cleaned_text = cleaned_text[4:]
            cleaned_text = cleaned_text.strip()
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3].strip()

        if not cleaned_text.startswith("{"):
            start = cleaned_text.find("{")
            end = cleaned_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                cleaned_text = cleaned_text[start:end + 1]

        try:
            parsed = json.loads(cleaned_text)
        except json.JSONDecodeError:
            return {
                "recommended_index": 0,
                "confidence": 0,
                "reasoning": raw_text
            }

        return parsed
    
    def _call_openai_api(self, user_prompt, system_prompt, api_key):
        """Call OpenAI ChatGPT API"""
        api_url = "https://api.openai.com/v1/chat/completions"
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            api_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}: {response.text}")
        
        result = response.json()
        text = result.get("choices", [{}])[0].get("message", {}).get("content", "Could not generate a hint.")
        
        return text
    
    def _call_claude_api(self, user_prompt, system_prompt, api_key):
        """Call Anthropic Claude API"""
        api_url = "https://api.anthropic.com/v1/messages"
        
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 500,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        
        response = requests.post(
            api_url,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}: {response.text}")
        
        result = response.json()
        text = result.get("content", [{}])[0].get("text", "Could not generate a hint.")
        
        return text