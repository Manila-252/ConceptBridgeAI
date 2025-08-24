# app/services/analogy_service.py
import json
import time
import logging
from typing import List, Dict, Any, Tuple, Optional
from openai import OpenAI
from ..schemas import AnalogyExample
import os

logger = logging.getLogger(__name__)

class AnalogyGenerationService:
    """Service for generating personalized analogies using AI"""
    
    def __init__(self):
        # Initialize OpenAI client (you'll need to set OPENAI_API_KEY in environment)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-openai-key-here"))
        self.model = "gpt-4"
        
        # Profession-specific contexts and metaphors
        self.profession_contexts = {
            "cooking": {
                "keywords": ["recipe", "ingredients", "cooking process", "kitchen tools", "preparation", "seasoning", "timing"],
                "metaphors": ["mixing ingredients", "following recipes", "kitchen workflow", "taste testing", "meal planning"],
                "examples": ["preparing a multi-course meal", "organizing a kitchen", "scaling recipes", "ingredient substitution"]
            },
            "gaming": {
                "keywords": ["levels", "progression", "stats", "inventory", "quests", "NPCs", "skill trees", "gameplay"],
                "metaphors": ["character builds", "quest completion", "resource management", "level progression", "guild systems"],
                "examples": ["RPG character development", "strategy game tactics", "puzzle-solving mechanics", "multiplayer coordination"]
            },
            "sports": {
                "keywords": ["team strategy", "training", "performance", "competition", "tactics", "coaching", "practice"],
                "metaphors": ["team formations", "training regimens", "game strategy", "performance metrics", "tournament brackets"],
                "examples": ["building a winning team", "developing game strategy", "analyzing player statistics", "tournament preparation"]
            },
            "music": {
                "keywords": ["harmony", "rhythm", "composition", "instruments", "scales", "tempo", "arrangement"],
                "metaphors": ["musical composition", "orchestra coordination", "rhythm patterns", "harmonic progressions", "song structure"],
                "examples": ["composing a symphony", "arranging instruments", "creating rhythm patterns", "musical improvisation"]
            },
            "business": {
                "keywords": ["organization", "processes", "management", "efficiency", "workflow", "teams", "projects"],
                "metaphors": ["company structure", "project management", "resource allocation", "team coordination", "business strategy"],
                "examples": ["organizational hierarchy", "project planning", "resource optimization", "team management"]
            }
        }
    
    def generate_analogy(self, 
                        profession: str, 
                        concept_name: str, 
                        concept_description: str,
                        topic_context: str = "",
                        difficulty_level: str = "intermediate",
                        creativity_level: int = 3) -> Tuple[str, str, List[AnalogyExample], float]:
        """
        Generate a personalized analogy using AI
        
        Returns: (analogy_title, analogy_explanation, examples, generation_time)
        """
        start_time = time.time()
        
        try:
            # Build the prompt
            prompt = self._build_analogy_prompt(
                profession, concept_name, concept_description, 
                topic_context, difficulty_level, creativity_level
            )
            
            # Generate with OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=min(0.3 + (creativity_level * 0.15), 1.0),
                max_tokens=1500
            )
            
            # Parse response
            content = response.choices[0].message.content
            analogy_data = self._parse_analogy_response(content)
            
            generation_time = time.time() - start_time
            
            logger.info(f"Generated analogy for {profession} -> {concept_name} in {generation_time:.2f}s")
            
            return (
                analogy_data["title"],
                analogy_data["explanation"], 
                analogy_data["examples"],
                generation_time
            )
            
        except Exception as e:
            logger.error(f"Failed to generate analogy: {e}")
            # Fallback to template-based analogy
            return self._generate_fallback_analogy(profession, concept_name, concept_description, time.time() - start_time)
    
    def _get_system_prompt(self) -> str:
        """System prompt for AI analogy generation"""
        return """You are ConceptBridge AI, an expert at creating personalized learning analogies. Your job is to explain complex concepts using analogies from the user's professional background.

Guidelines:
1. Create analogies that are accurate, memorable, and directly relatable
2. Use specific terminology and scenarios from the user's profession
3. Provide concrete examples that illuminate the concept
4. Make abstract ideas tangible through familiar experiences
5. Ensure the analogy actually helps understanding, not just entertains

Response Format (JSON):
{
  "title": "Catchy analogy title",
  "explanation": "Detailed explanation using the analogy (3-4 paragraphs)",
  "examples": [
    {
      "title": "Example 1 Title",
      "description": "Detailed example description",
      "code_snippet": "Optional code/pseudo-code",
      "visual_metaphor": "Visual description"
    }
  ],
  "key_connections": ["Connection 1", "Connection 2"],
  "practical_applications": ["Application 1", "Application 2"]
}"""
    
    def _build_analogy_prompt(self, profession: str, concept_name: str, 
                            concept_description: str, topic_context: str, 
                            difficulty_level: str, creativity_level: int) -> str:
        """Build the analogy generation prompt"""
        
        profession_context = self.profession_contexts.get(profession.lower(), {
            "keywords": ["processes", "systems", "organization"],
            "metaphors": ["structured approaches", "systematic thinking"],
            "examples": ["workflow optimization", "systematic problem solving"]
        })
        
        prompt = f"""
Create a personalized analogy to explain "{concept_name}" to someone with a {profession} background.

CONCEPT TO EXPLAIN:
- Name: {concept_name}
- Description: {concept_description}
- Topic Context: {topic_context}
- Target Difficulty: {difficulty_level}

USER'S BACKGROUND ({profession.upper()}):
- Relevant Keywords: {', '.join(profession_context['keywords'])}
- Common Metaphors: {', '.join(profession_context['metaphors'])}
- Familiar Examples: {', '.join(profession_context['examples'])}

CREATIVITY LEVEL: {creativity_level}/5 
{"(Be highly creative and use unexpected connections)" if creativity_level >= 4 else "(Use straightforward, clear analogies)" if creativity_level <= 2 else "(Balance creativity with clarity)"}

Requirements:
1. Use terminology and scenarios specifically from {profession}
2. Create 2-3 concrete examples that show the concept in action
3. Make the abstract concept tangible and memorable
4. Ensure technical accuracy while maintaining the analogy
5. Include practical applications they can relate to

Provide your response in the JSON format specified in the system prompt.
"""
        return prompt.strip()
    
    def _parse_analogy_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            # Try to parse as JSON
            if content.strip().startswith('{'):
                data = json.loads(content)
            else:
                # If not JSON, extract manually (fallback)
                data = self._extract_analogy_parts(content)
            
            # Convert examples to AnalogyExample objects
            examples = []
            for ex in data.get("examples", []):
                if isinstance(ex, dict):
                    examples.append(AnalogyExample(
                        title=ex.get("title", "Example"),
                        description=ex.get("description", ""),
                        code_snippet=ex.get("code_snippet"),
                        visual_metaphor=ex.get("visual_metaphor")
                    ))
            
            return {
                "title": data.get("title", "Concept Explanation"),
                "explanation": data.get("explanation", ""),
                "examples": examples
            }
            
        except Exception as e:
            logger.error(f"Failed to parse analogy response: {e}")
            return {
                "title": "Understanding Through Analogy",
                "explanation": content[:500] + "..." if len(content) > 500 else content,
                "examples": []
            }
    
    def _extract_analogy_parts(self, content: str) -> Dict[str, Any]:
        """Extract analogy parts from unstructured text (fallback)"""
        lines = content.split('\n')
        
        title = "Understanding Through Analogy"
        explanation = content
        examples = []
        
        # Try to find title (often in first line or after "Title:")
        for line in lines[:3]:
            if len(line.strip()) > 0 and len(line.strip()) < 100:
                if any(keyword in line.lower() for keyword in ['like', 'analogy', 'imagine', 'think of']):
                    title = line.strip().strip('"').strip()
                    break
        
        return {
            "title": title,
            "explanation": explanation,
            "examples": examples
        }
    
    def _generate_fallback_analogy(self, profession: str, concept_name: str, 
                                 concept_description: str, generation_time: float) -> Tuple[str, str, List[AnalogyExample], float]:
        """Generate a simple template-based analogy as fallback"""
        
        profession_context = self.profession_contexts.get(profession.lower(), {})
        
        title = f"Understanding {concept_name} Through {profession.title()}"
        
        explanation = f"""
Let me explain {concept_name} using concepts from {profession} that you're familiar with.

{concept_description}

In {profession}, you probably work with {', '.join(profession_context.get('keywords', ['systems', 'processes'])[:3])}. 
{concept_name} works in a similar way - it's about organizing and managing information systematically.

Think of it like {profession_context.get('examples', ['a structured process'])[0]} where you need to:
1. Understand the components involved
2. Follow a systematic approach
3. Achieve a specific outcome efficiently

This concept is fundamental in computer science because it helps solve complex problems by breaking them down into manageable parts, much like how you approach challenges in {profession}.
        """.strip()
        
        examples = [
            AnalogyExample(
                title=f"Basic {concept_name} Example",
                description=f"A simple example relating {concept_name} to {profession} practices",
                visual_metaphor=f"Like organizing {profession_context.get('keywords', ['items'])[0]}"
            )
        ]
        
        return title, explanation, examples, generation_time
    
    def generate_quick_analogy(self, profession: str, concept: str, 
                             context: str = "", creativity_level: int = 3) -> Dict[str, Any]:
        """Generate a quick analogy without database storage"""
        start_time = time.time()
        
        # Simplified prompt for quick generation
        prompt = f"""
Explain "{concept}" to someone with a {profession} background.
{f"Context: {context}" if context else ""}

Make it concise but memorable. Use {profession} terminology and examples.
Provide a clear analogy, 2-3 practical examples, and key connections.

Format as JSON with: title, explanation, practical_examples, key_connections, next_steps
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at creating clear, concise analogies. Always respond in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3 + (creativity_level * 0.1),
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            data = json.loads(content) if content.startswith('{') else {"title": "Quick Explanation", "explanation": content}
            
            generation_time = time.time() - start_time
            
            return {
                "concept": concept,
                "profession_context": profession,
                "analogy_title": data.get("title", f"Understanding {concept}"),
                "explanation": data.get("explanation", ""),
                "practical_examples": data.get("practical_examples", []),
                "key_connections": data.get("key_connections", []),
                "next_steps": data.get("next_steps", []),
                "generation_time": generation_time
            }
            
        except Exception as e:
            logger.error(f"Quick analogy generation failed: {e}")
            return {
                "concept": concept,
                "profession_context": profession,
                "analogy_title": f"Understanding {concept} Through {profession.title()}",
                "explanation": f"Let me explain {concept} using examples from {profession}...",
                "practical_examples": [f"Example from {profession}"],
                "key_connections": [f"Connection to {profession}"],
                "next_steps": ["Practice with examples", "Apply to real scenarios"],
                "generation_time": time.time() - start_time
            }