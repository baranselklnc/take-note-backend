"""AI service for Take Note Backend API using Hugging Face models."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import re

# Optional AI imports - will fallback to mock if not available
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("AI dependencies not available, using mock responses")

logger = logging.getLogger(__name__)


class AIService:
    """AI service for note processing using Hugging Face models."""
    
    def __init__(self):
        """Initialize AI service with Hugging Face models."""
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Initialize models (lazy loading)
        self._summarizer = None
        self._classifier = None
        self._sentiment_analyzer = None
        self._tokenizer = None
        
        # Model configurations
        self.models = {
            "summarization": "facebook/bart-large-cnn",
            "text_classification": "microsoft/DialoGPT-medium", 
            "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest"
        }
        
        logger.info("AI Service initialized")
    
    def _get_summarizer(self):
        """Get summarization model (lazy loading)."""
        if not AI_AVAILABLE:
            return None
            
        if self._summarizer is None:
            try:
                self._summarizer = pipeline(
                    "summarization",
                    model=self.models["summarization"],
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("Summarization model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load summarization model: {e}")
                return None
        return self._summarizer
    
    def _get_classifier(self):
        """Get text classification model (lazy loading)."""
        if not AI_AVAILABLE:
            return None
            
        if self._classifier is None:
            try:
                self._classifier = pipeline(
                    "text-classification",
                    model=self.models["text_classification"],
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("Classification model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load classification model: {e}")
                return None
        return self._classifier
    
    def _get_sentiment_analyzer(self):
        """Get sentiment analysis model (lazy loading)."""
        if not AI_AVAILABLE:
            return None
            
        if self._sentiment_analyzer is None:
            try:
                self._sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model=self.models["sentiment"],
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("Sentiment analysis model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load sentiment model: {e}")
                return None
        return self._sentiment_analyzer
    
    async def summarize_note(self, content: str, max_length: int = 150) -> Dict[str, Any]:
        """
        Summarize a note using BART model.
        
        Args:
            content: Note content to summarize
            max_length: Maximum length of summary
            
        Returns:
            Dict containing summary and metadata
        """
        try:
            if not content or len(content.strip()) < 50:
                return {
                    "summary": content,
                    "original_length": len(content),
                    "summary_length": len(content),
                    "compression_ratio": 1.0,
                    "model": "no_summary_needed"
                }
            
            # Run summarization in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._run_summarization,
                content,
                max_length
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in summarize_note: {e}")
            return {
                "summary": content[:max_length] + "..." if len(content) > max_length else content,
                "original_length": len(content),
                "summary_length": min(len(content), max_length),
                "compression_ratio": min(len(content), max_length) / len(content),
                "model": "fallback",
                "error": str(e)
            }
    
    def _run_summarization(self, content: str, max_length: int) -> Dict[str, Any]:
        """Run summarization in thread."""
        summarizer = self._get_summarizer()
        if not summarizer:
            raise Exception("Summarizer model not available")
        
        # Truncate content if too long
        max_input_length = 1024
        if len(content) > max_input_length:
            content = content[:max_input_length]
        
        result = summarizer(content, max_length=max_length, min_length=30, do_sample=False)
        
        summary = result[0]['summary_text']
        
        return {
            "summary": summary,
            "original_length": len(content),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(content),
            "model": self.models["summarization"]
        }
    
    async def categorize_note(self, content: str) -> Dict[str, Any]:
        """
        Categorize a note using text classification.
        
        Args:
            content: Note content to categorize
            
        Returns:
            Dict containing category and confidence
        """
        try:
            if not content or len(content.strip()) < 10:
                return {
                    "category": "General",
                    "confidence": 0.0,
                    "model": "default"
                }
            
            # Simple rule-based categorization for demo
            category = self._rule_based_categorization(content)
            
            return {
                "category": category,
                "confidence": 0.85,  # Mock confidence
                "model": "rule_based"
            }
            
        except Exception as e:
            logger.error(f"Error in categorize_note: {e}")
            return {
                "category": "General",
                "confidence": 0.0,
                "model": "error",
                "error": str(e)
            }
    
    def _rule_based_categorization(self, content: str) -> str:
        """Simple rule-based categorization."""
        content_lower = content.lower()
        
        # Define category keywords
        categories = {
            "Work": ["meeting", "project", "deadline", "task", "work", "business", "client", "team"],
            "Personal": ["family", "friend", "personal", "home", "hobby", "vacation", "birthday"],
            "Study": ["study", "learn", "course", "exam", "homework", "research", "book", "lesson"],
            "Health": ["doctor", "medicine", "exercise", "diet", "health", "appointment", "symptoms"],
            "Finance": ["money", "budget", "expense", "income", "investment", "bill", "payment"],
            "Shopping": ["buy", "purchase", "shop", "price", "discount", "store", "cart"]
        }
        
        # Count keyword matches
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "General"
    
    async def generate_tags(self, content: str) -> Dict[str, Any]:
        """
        Generate tags for a note using NLP techniques.
        
        Args:
            content: Note content to generate tags for
            
        Returns:
            Dict containing tags and confidence scores
        """
        try:
            if not content or len(content.strip()) < 10:
                return {
                    "tags": [],
                    "confidence_scores": [],
                    "model": "default"
                }
            
            # Extract keywords and create tags
            tags = self._extract_keywords(content)
            
            return {
                "tags": tags,
                "confidence_scores": [0.8] * len(tags),  # Mock confidence scores
                "model": "keyword_extraction"
            }
            
        except Exception as e:
            logger.error(f"Error in generate_tags: {e}")
            return {
                "tags": [],
                "confidence_scores": [],
                "model": "error",
                "error": str(e)
            }
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'
        }
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        tags = [word for word, freq in sorted_words[:5] if freq > 1]
        
        return tags[:5]  # Return top 5 tags
    
    async def semantic_search(self, query: str, notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform semantic search on notes.
        
        Args:
            query: Search query
            notes: List of notes to search in
            
        Returns:
            List of notes ranked by relevance
        """
        try:
            if not query or not notes:
                return []
            
            # Simple text similarity search
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            scored_notes = []
            for note in notes:
                title = note.get('title', '').lower()
                content = note.get('content', '').lower()
                
                # Calculate simple similarity score
                title_words = set(title.split())
                content_words = set(content.split())
                
                title_score = len(query_words.intersection(title_words)) / len(query_words) if query_words else 0
                content_score = len(query_words.intersection(content_words)) / len(query_words) if query_words else 0
                
                # Weighted score (title more important)
                total_score = (title_score * 0.7) + (content_score * 0.3)
                
                if total_score > 0:
                    scored_notes.append({
                        **note,
                        'relevance_score': total_score
                    })
            
            # Sort by relevance score
            scored_notes.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return scored_notes
            
        except Exception as e:
            logger.error(f"Error in semantic_search: {e}")
            return []
    
    async def process_note_ai(self, content: str) -> Dict[str, Any]:
        """
        Process a note with all AI features.
        
        Args:
            content: Note content
            
        Returns:
            Dict containing all AI processing results
        """
        try:
            # Run all AI tasks in parallel
            tasks = [
                self.summarize_note(content),
                self.categorize_note(content),
                self.generate_tags(content)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            summary_result = results[0] if not isinstance(results[0], Exception) else {"summary": content, "error": str(results[0])}
            category_result = results[1] if not isinstance(results[1], Exception) else {"category": "General", "error": str(results[1])}
            tags_result = results[2] if not isinstance(results[2], Exception) else {"tags": [], "error": str(results[2])}
            
            return {
                "summary": summary_result,
                "category": category_result,
                "tags": tags_result,
                "processed_at": "2024-01-01T00:00:00Z"  # Would be actual timestamp
            }
            
        except Exception as e:
            logger.error(f"Error in process_note_ai: {e}")
            return {
                "error": str(e),
                "summary": {"summary": content},
                "category": {"category": "General"},
                "tags": {"tags": []}
            }


# Global AI service instance
ai_service = AIService()
