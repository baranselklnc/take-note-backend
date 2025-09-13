"""AI service using Hugging Face Inference API for Take Note Backend."""

import os
import requests
import json
import asyncio
import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class HuggingFaceAIService:
    """AI service using Hugging Face Inference API."""
    
    def __init__(self):
        """Initialize Hugging Face AI service."""
        self.base_url = "https://api-inference.huggingface.co/models"
        self.headers = {
            "Content-Type": "application/json"
        }
        # Add your HF token here if you have one (optional)
        # Get token from environment variable
        hf_token = os.getenv("HUGGINGFACE_API_KEY")
        if hf_token:
            self.headers["Authorization"] = f"Bearer {hf_token}"
    
    async def _make_request(self, model: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to Hugging Face API."""
        try:
            url = f"{self.base_url}/{model}"
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"HF API error: {response.status_code} - {response.text}")
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"HF API request failed: {e}")
            return {"error": str(e)}
    
    async def summarize_note(self, content: str) -> Dict[str, Any]:
        """Summarize note content using Hugging Face summarization model."""
        original_length = len(content)
        
        if original_length < 50:
            summary = content[:100] + "..." if len(content) > 100 else content
            return {
                "summary": summary,
                "model": "fallback_short_content",
                "original_length": original_length,
                "summary_length": len(summary),
                "compression_ratio": len(summary) / original_length if original_length > 0 else 1.0
            }
        
        # Use a lightweight summarization model
        payload = {
            "inputs": content[:1000],  # Limit input length
            "parameters": {
                "max_length": 150,
                "min_length": 30,
                "do_sample": False
            }
        }
        
        # Try multiple models for better results
        models_to_try = [
            "facebook/bart-large-cnn",
            "google/pegasus-xsum", 
            "sshleifer/distilbart-cnn-12-6"
        ]
        
        for model in models_to_try:
            result = await self._make_request(model, payload)
            
            if "error" not in result and isinstance(result, list) and len(result) > 0:
                summary = result[0].get("summary_text", "")
                if summary and len(summary) > 10:  # Valid summary
                    return {
                        "summary": summary,
                        "model": model,
                        "original_length": original_length,
                        "summary_length": len(summary),
                        "compression_ratio": len(summary) / original_length if original_length > 0 else 1.0
                    }
        
        return self._fallback_summarize(content)
    
    async def categorize_note(self, title: str, content: str) -> Dict[str, Any]:
        """Categorize note using Hugging Face classification model."""
        text = f"{title} {content}"
        
        # Use a text classification model
        payload = {
            "inputs": text[:512],  # Limit input length
            "parameters": {
                "top_k": 3
            }
        }
        
        result = await self._make_request("cardiffnlp/twitter-roberta-base-emotion", payload)
        
        if "error" in result:
            return self._fallback_categorize(title, content)
        
        if isinstance(result, list) and len(result) > 0:
            categories = []
            scores = []
            
            for item in result[:3]:  # Top 3 categories
                if isinstance(item, dict):
                    categories.append(item.get("label", "unknown"))
                    scores.append(item.get("score", 0.0))
            
            return {
                "categories": categories,
                "confidence_scores": scores,
                "model": "cardiffnlp/twitter-roberta-base-emotion"
            }
        
        return self._fallback_categorize(title, content)
    
    async def extract_tags(self, content: str) -> Dict[str, Any]:
        """Extract tags from note content using Hugging Face NER model."""
        if len(content) < 50:
            return self._fallback_extract_tags(content)
        
        # Use Named Entity Recognition model for better tag extraction
        payload = {
            "inputs": content[:512],  # Limit input length
            "parameters": {
                "aggregation_strategy": "simple"
            }
        }
        
        # Try multiple NER models (Turkish and English)
        models_to_try = [
            "savasy/bert-base-turkish-ner-cased",
            "dbmdz/bert-base-turkish-cased",
            "dbmdz/bert-base-turkish-uncased",
            "microsoft/Multilingual-MiniLM-L12-H384",
            "dbmdz/bert-large-cased-finetuned-conll03-english",
            "dslim/bert-base-NER"
        ]
        
        for model in models_to_try:
            result = await self._make_request(model, payload)
            
            if "error" not in result and isinstance(result, list):
                # Extract entities as tags
                entities = []
                scores = []
                
                for item in result:
                    if isinstance(item, dict) and item.get("entity_group"):
                        entity = item.get("word", "").strip()
                        score = item.get("score", 0.0)
                        
                        # Filter meaningful entities
                        if len(entity) > 2 and entity.isalpha():
                            entities.append(entity.lower())
                            scores.append(score)
                
                if entities:
                    return {
                        "tags": entities[:5],  # Top 5 entities
                        "confidence_scores": scores[:5],
                        "model": model
                    }
        
        return self._fallback_extract_tags(content)
    
    def _fallback_extract_tags(self, content: str) -> Dict[str, Any]:
        """Fallback keyword extraction using simple text processing."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Remove common stop words (English + Turkish)
        stop_words = {
            # English stop words
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use', 'this', 'that', 'with', 'have', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were', 'will', 'your', 'said', 'each', 'which', 'their', 'would', 'there', 'could', 'other', 'after', 'first', 'never', 'these', 'think', 'where', 'being', 'every', 'great', 'might', 'shall', 'still', 'those', 'under', 'while', 'years', 'again', 'before', 'large', 'place', 'small', 'sound', 'spell', 'through', 'another', 'because', 'between', 'change', 'follow', 'mother', 'should', 'without', 'around', 'became', 'before', 'during', 'family', 'friend', 'little', 'number', 'people', 'please', 'school', 'seemed', 'turned', 'wanted', 'better', 'enough', 'example', 'happened', 'important', 'instead', 'nothing', 'problem', 'question', 'remember', 'something', 'sometimes', 'together', 'understand', 'without', 'almost', 'already', 'although', 'another', 'anything', 'because', 'between', 'different', 'everything', 'following', 'happened', 'important', 'interest', 'probably', 'something', 'sometimes', 'together', 'understand',
            # Turkish stop words
            'bir', 'bu', 'şu', 'o', 've', 'ile', 'için', 'da', 'de', 'den', 'dan', 'e', 'a', 'ya', 'ye', 'den', 'dan', 'nin', 'nın', 'nun', 'nün', 'lar', 'ler', 'ı', 'i', 'u', 'ü', 'ı', 'i', 'u', 'ü', 'ben', 'sen', 'biz', 'siz', 'onlar', 'benim', 'senin', 'bizim', 'sizin', 'onların', 'beni', 'seni', 'bizi', 'sizi', 'onları', 'bana', 'sana', 'bize', 'size', 'onlara', 'bende', 'sende', 'bizde', 'sizde', 'onlarda', 'benden', 'senden', 'bizden', 'sizden', 'onlardan', 'benimle', 'seninle', 'bizimle', 'sizinle', 'onlarla', 'var', 'yok', 'olmak', 'etmek', 'yapmak', 'gelmek', 'gitmek', 'almak', 'vermek', 'görmek', 'bilmek', 'istemek', 'çok', 'az', 'büyük', 'küçük', 'iyi', 'kötü', 'güzel', 'çirkin', 'yeni', 'eski', 'genç', 'yaşlı', 'uzun', 'kısa', 'geniş', 'dar', 'yüksek', 'alçak', 'derin', 'sığ', 'hızlı', 'yavaş', 'sıcak', 'soğuk', 'sıcak', 'ılık', 'temiz', 'kirli', 'açık', 'kapalı', 'kolay', 'zor', 'basit', 'karmaşık', 'doğru', 'yanlış', 'gerçek', 'sahte', 'canlı', 'ölü', 'mutlu', 'üzgün', 'kızgın', 'korkmuş', 'şaşkın', 'sakin', 'heyecanlı', 'yorgun', 'dinç', 'aç', 'tok', 'susamış', 'kanmış', 'hasta', 'sağlıklı', 'güçlü', 'zayıf', 'şişman', 'zayıf', 'uzun', 'kısa', 'kalın', 'ince', 'geniş', 'dar', 'dolu', 'boş', 'tam', 'yarım', 'bütün', 'parça', 'tek', 'çift', 'ilk', 'son', 'önce', 'sonra', 'şimdi', 'dün', 'bugün', 'yarın', 'geçen', 'gelecek', 'her', 'hiç', 'bazen', 'hep', 'hiçbir', 'bazı', 'tüm', 'hepsi', 'kimse', 'herkes', 'hiçbir', 'biri', 'bazısı', 'çoğu', 'azı', 'tamamı', 'yarısı', 'üçte', 'dörtte', 'beşte', 'altıda', 'yedide', 'sekizde', 'dokuzda', 'onda', 'yüzde', 'binde', 'milyonda', 'trilyonda'
        }
        
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count word frequency
        word_count = {}
        for word in filtered_words:
            word_count[word] = word_count.get(word, 0) + 1
        
        # Get top 5 most frequent words
        top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        tags = [word for word, count in top_words if count > 1]
        scores = [count / len(filtered_words) for word, count in top_words if count > 1]
        
        return {
            "tags": tags,
            "confidence_scores": scores,
            "model": "fallback_keywords"
        }
    
    async def semantic_search(self, query: str, notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform semantic search using Hugging Face sentence transformers."""
        if len(query) < 3:
            return {
                "query": query,
                "results": [],
                "total_matches": 0,
                "model": "fallback_short_query"
            }
        
        # Try Hugging Face sentence transformers first
        sentence_models = [
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        ]
        
        for model in sentence_models:
            try:
                # Prepare documents for similarity search
                documents = []
                for note in notes:
                    content = f"{note.get('title', '')} {note.get('content', '')}"
                    documents.append({
                        "id": note.get("id"),
                        "title": note.get("title"),
                        "content": content[:500],  # Limit content length
                        "full_content": content
                    })
                
                logger.info(f"Trying semantic search with model: {model}")
                logger.info(f"Query: {query}, Documents count: {len(documents)}")
                
                # Use Hugging Face for semantic similarity
                payload = {
                    "inputs": {
                        "source_sentence": query,
                        "sentences": [doc["content"] for doc in documents]
                    }
                }
                
                result = await self._make_request(f"{model}", payload)
                
                if "error" not in result and isinstance(result, list):
                    # Calculate similarities
                    similarities = result[0] if result else []
                    
                    results = []
                    for i, similarity in enumerate(similarities):
                        if similarity > 0.3:  # Minimum similarity threshold
                            results.append({
                                "note_id": documents[i]["id"],
                                "title": documents[i]["title"],
                                "similarity_score": float(similarity),
                                "matched_content": documents[i]["content"][:100] + "...",
                                "model": model
                            })
                    
                    if results:
                        # Sort by similarity score
                        results.sort(key=lambda x: x["similarity_score"], reverse=True)
                        
                        return {
                            "query": query,
                            "results": results[:10],  # Top 10 results
                            "total_matches": len(results),
                            "model": model
                        }
                        
            except Exception as e:
                logger.warning(f"Semantic search failed with model {model}: {e}")
                continue
        
        # Fallback to keyword matching
        return self._fallback_semantic_search(query, notes)
    
    def _fallback_semantic_search(self, query: str, notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback semantic search using enhanced keyword matching with semantic categories."""
        logger.info(f"Using fallback semantic search for query: {query}")
        logger.info(f"Notes count: {len(notes)}")
        
        query_words = set(re.findall(r'\b[a-zA-ZçğıöşüÇĞIÖŞÜ]{2,}\b', query.lower()))
        logger.info(f"Query words: {query_words}")
        
        # Use simple but effective keyword similarity
        # Instead of hardcoded categories, use word similarity patterns
        
        # Enhanced keyword matching with Turkish support
        results = []
        for note in notes:
            content = f"{note.get('title', '')} {note.get('content', '')}"
            content_words = set(re.findall(r'\b[a-zA-ZçğıöşüÇĞIÖŞÜ]{2,}\b', content.lower()))
            
            similarity = 0
            matched_words = []
            
            # 1. Direct word overlap
            intersection = query_words.intersection(content_words)
            if intersection:
                similarity += len(intersection) / len(query_words)
                matched_words.extend(list(intersection))
            
            # 2. Boost score for title matches
            title_words = set(re.findall(r'\b[a-zA-ZçğıöşüÇĞIÖŞÜ]{2,}\b', note.get('title', '').lower()))
            title_intersection = query_words.intersection(title_words)
            if title_intersection:
                similarity += len(title_intersection) * 0.5
                matched_words.extend(list(title_intersection))
            
            # 3. Word similarity patterns (more strict matching)
            for query_word in query_words:
                for content_word in content_words:
                    # More strict similarity check
                    if (len(query_word) > 4 and len(content_word) > 4 and 
                        (query_word in content_word or content_word in query_word or
                         self._word_similarity(query_word, content_word) > 0.8)):
                        similarity += 0.4  # Lower bonus
                        matched_words.append(content_word)
                        logger.info(f"Found word similarity: {query_word} <-> {content_word}")
            
            # 4. Partial matches (contains)
            content_lower = content.lower()
            query_lower = query.lower()
            if query_lower in content_lower:
                similarity += 0.8
                matched_words.append(query_lower)
            
            logger.info(f"Note: {note.get('title', '')}, Similarity: {similarity}, Matched: {matched_words}")
            
            if similarity > 0.3:  # Higher threshold for better results
                results.append({
                    "note_id": note.get("id"),
                    "title": note.get("title"),
                    "similarity_score": similarity,
                    "matched_words": list(set(matched_words)),
                    "model": "enhanced_keyword_matching"
                })
        
        # Sort by similarity score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        logger.info(f"Fallback results: {len(results)}")
        
        return {
            "query": query,
            "results": results[:10],  # Top 10 results
            "total_matches": len(results),
            "model": "enhanced_keyword_matching"
        }
    
    def _word_similarity(self, word1: str, word2: str) -> float:
        """Calculate simple word similarity based on common characters."""
        if not word1 or not word2:
            return 0.0
        
        # Convert to lowercase
        w1, w2 = word1.lower(), word2.lower()
        
        # If one word contains the other
        if w1 in w2 or w2 in w1:
            return 0.8
        
        # Calculate character overlap
        set1, set2 = set(w1), set(w2)
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        if not union:
            return 0.0
        
        # Jaccard similarity
        jaccard = len(intersection) / len(union)
        
        # Boost for same length and similar characters
        length_similarity = 1.0 - abs(len(w1) - len(w2)) / max(len(w1), len(w2))
        
        return (jaccard * 0.7 + length_similarity * 0.3)
    
    def _fallback_summarize(self, content: str) -> Dict[str, Any]:
        """Intelligent fallback summarization using sentence scoring."""
        original_length = len(content)
        
        # Split into sentences
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        if len(sentences) <= 2:
            summary = content
        else:
            # Score sentences by length and keyword frequency
            word_freq = {}
            all_words = []
            
            for sentence in sentences:
                words = sentence.lower().split()
                all_words.extend(words)
            
            # Count word frequency
            for word in all_words:
                if len(word) > 3:  # Only meaningful words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Score sentences
            scored_sentences = []
            for sentence in sentences:
                words = sentence.lower().split()
                score = 0
                
                # Length bonus
                score += len(sentence) * 0.1
                
                # Keyword frequency bonus
                for word in words:
                    if len(word) > 3 and word in word_freq:
                        score += word_freq[word] * 2
                
                scored_sentences.append((score, sentence))
            
            # Sort by score and take top sentences
            scored_sentences.sort(key=lambda x: x[0], reverse=True)
            
            # Take top 2-3 sentences, but not more than 50% of original
            max_sentences = min(3, len(sentences) // 2)
            top_sentences = [s[1] for s in scored_sentences[:max_sentences]]
            
            summary = '. '.join(top_sentences) + '.'
        
        # Ensure reasonable length
        if len(summary) > original_length * 0.6:  # Don't be too long
            summary = summary[:int(original_length * 0.4)] + "..."
        
        return {
            "summary": summary,
            "model": "intelligent_fallback",
            "original_length": original_length,
            "summary_length": len(summary),
            "compression_ratio": len(summary) / original_length if original_length > 0 else 1.0
        }
    
    def _fallback_categorize(self, title: str, content: str) -> Dict[str, Any]:
        """Fallback categorization using keyword matching."""
        text = f"{title} {content}".lower()
        
        categories = []
        scores = []
        
        # Simple keyword-based categorization
        if any(word in text for word in ['work', 'job', 'meeting', 'project', 'task', 'business']):
            categories.append("work")
            scores.append(0.8)
        
        if any(word in text for word in ['study', 'learn', 'education', 'school', 'university', 'course']):
            categories.append("education")
            scores.append(0.7)
        
        if any(word in text for word in ['personal', 'life', 'family', 'friend', 'home']):
            categories.append("personal")
            scores.append(0.6)
        
        if any(word in text for word in ['idea', 'creative', 'design', 'art', 'inspiration']):
            categories.append("creative")
            scores.append(0.7)
        
        if not categories:
            categories = ["general"]
            scores = [0.5]
        
        return {
            "categories": categories,
            "confidence_scores": scores,
            "model": "fallback_keywords"
        }
    
    async def process_note_ai(self, content: str) -> Dict[str, Any]:
        """Process note with all AI features: summarize, categorize, and extract tags."""
        try:
            # Run all AI tasks concurrently
            summary_task = self.summarize_note(content)
            tags_task = self.extract_tags(content)
            category_task = self.categorize_note("", content)  # Empty title for categorization
            
            # Wait for all tasks to complete
            summary_result, tags_result, category_result = await asyncio.gather(
                summary_task, tags_task, category_task
            )
            
            return {
                "summary": summary_result.get("summary", ""),
                "summary_model": summary_result.get("model", ""),
                "categories": category_result.get("categories", []),
                "category_scores": category_result.get("confidence_scores", []),
                "category_model": category_result.get("model", ""),
                "tags": tags_result.get("tags", []),
                "tag_scores": tags_result.get("confidence_scores", []),
                "tag_model": tags_result.get("model", ""),
                "processing_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            return {
                "summary": content[:100] + "..." if len(content) > 100 else content,
                "summary_model": "fallback",
                "categories": ["general"],
                "category_scores": [0.5],
                "category_model": "fallback",
                "tags": [],
                "tag_scores": [],
                "tag_model": "fallback",
                "processing_status": "failed",
                "error": str(e)
            }

# Global AI service instance
ai_service = HuggingFaceAIService()
