"""Service for seeding default prompts into the database."""
import logging
from domain.entities.prompt import Prompt
from domain.repositories.prompt_repository import PromptRepository

logger = logging.getLogger(__name__)


DEFAULT_PROMPTS = [
    {
        "name": "document_summary",
        "description": "Generate a comprehensive summary of a document",
        "category": "summary",
        "template": """Please provide a comprehensive summary of the following document:

{full_text}

Please provide:
1. A concise summary (2-3 paragraphs)
2. 3-5 key points or takeaways

Format your response as:
SUMMARY:
[Your summary here]

KEY POINTS:
- [Point 1]
- [Point 2]
- [Point 3]"""
    },
    {
        "name": "document_qa",
        "description": "Answer questions about a document",
        "category": "qa",
        "template": """Based on the following document context:

{context}

Please answer this question: {question}

Provide a clear, detailed answer based only on the information in the document. If the answer cannot be found in the document, say so."""
    },
    {
        "name": "flashcard_generation",
        "description": "Generate flashcards from document content",
        "category": "flashcards",
        "template": """Based on the following document content:

{content}

Generate {num_cards} educational flashcards that help learn and retain the key information.

Format each flashcard as:
QUESTION: [Question that tests understanding]
ANSWER: [Clear, concise answer]
DIFFICULTY: [easy/medium/hard]

Make the questions varied - include definitions, concepts, applications, and critical thinking."""
    },
    {
        "name": "chunk_analysis",
        "description": "Analyze and extract key information from a text chunk",
        "category": "analysis",
        "template": """Analyze the following text chunk and extract key information:

{chunk_text}

Provide:
1. Main topic or theme
2. Key entities mentioned (people, places, organizations, dates)
3. Important facts or claims
4. Relevance score (1-10) for: {query_context}"""
    },
    {
        "name": "legal_document_summary",
        "description": "Specialized summary for legal documents",
        "category": "summary",
        "template": """Analyze the following legal document:

{full_text}

Provide a professional legal summary including:

1. DOCUMENT TYPE & PARTIES:
   - Type of legal document
   - Parties involved
   - Date and jurisdiction

2. KEY PROVISIONS:
   - Main terms and conditions
   - Rights and obligations
   - Important clauses

3. CRITICAL DATES & DEADLINES:
   - Effective dates
   - Expiration dates
   - Notice periods

4. POTENTIAL ISSUES OR RISKS:
   - Areas requiring attention
   - Ambiguous provisions
   - Compliance requirements

5. SUMMARY:
   - Executive summary in plain language"""
    },
    {
        "name": "research_paper_summary",
        "description": "Specialized summary for research papers",
        "category": "summary",
        "template": """Analyze the following research paper:

{full_text}

Provide a structured summary including:

1. TITLE & AUTHORS:
2. RESEARCH QUESTION/HYPOTHESIS:
3. METHODOLOGY:
4. KEY FINDINGS:
5. CONCLUSIONS:
6. LIMITATIONS:
7. IMPLICATIONS:
8. FUTURE RESEARCH DIRECTIONS:

Also provide a brief 2-3 sentence abstract suitable for quick reference."""
    }
]


class PromptSeeder:
    def __init__(self, prompt_repo: PromptRepository):
        self.prompt_repo = prompt_repo
    
    async def seed_default_prompts(self):
        """Seed the database with default prompts if they don't exist."""
        seeded_count = 0
        
        for prompt_data in DEFAULT_PROMPTS:
            try:
                # Check if prompt already exists
                existing = await self.prompt_repo.get_prompt_by_name(prompt_data["name"])
                if existing:
                    logger.info(f"Prompt '{prompt_data['name']}' already exists, skipping...")
                    continue
                
                # Create and save new prompt
                prompt = Prompt.create(
                    name=prompt_data["name"],
                    description=prompt_data["description"],
                    template=prompt_data["template"],
                    category=prompt_data["category"],
                    metadata=prompt_data.get("metadata", {}),
                )
                
                await self.prompt_repo.save_prompt(prompt)
                seeded_count += 1
                logger.info(f"Seeded prompt: {prompt_data['name']}")
                
            except Exception as e:
                logger.error(f"Error seeding prompt '{prompt_data.get('name', 'unknown')}': {e}")
        
        logger.info(f"Seeding complete. Added {seeded_count} new prompts.")
        return seeded_count