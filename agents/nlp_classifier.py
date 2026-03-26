"""
NLP-based classification engine with confidence scoring
"""

import re
from typing import Tuple, Dict
from config import CLASSIFICATION_CONFIG, PRIORITY_CONFIG
from utils.logger import logger


class FeedbackClassifier:
    """
    NLP-based feedback classifier with confidence scoring
    Uses keyword matching, sentiment analysis, and pattern recognition
    """
    
    def __init__(self):
        self.bug_keywords = CLASSIFICATION_CONFIG["bug_keywords"]
        self.feature_keywords = CLASSIFICATION_CONFIG["feature_keywords"]
        self.critical_keywords = PRIORITY_CONFIG["critical_keywords"]
        self.high_keywords = PRIORITY_CONFIG["high_keywords"]
    
    def calculate_confidence(self, text: str, keywords: list) -> float:
        """
        Calculate confidence score based on keyword presence and frequency
        Returns a score between 0.0 and 1.0
        """
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        
        if matches == 0:
            return 0.0
        
        # Base confidence on number of matches
        base_confidence = min(matches / 3, 1.0)  # Cap at 1.0
        
        # Boost confidence for exact matches
        exact_matches = sum(1 for keyword in keywords if f" {keyword} " in f" {text_lower} ")
        if exact_matches > 0:
            base_confidence = min(base_confidence + 0.1, 1.0)
        
        return round(base_confidence, 2)
    
    def analyze_sentiment(self, text: str, rating: int = None) -> Tuple[str, float]:
        """
        Analyze sentiment to determine if feedback is positive or negative
        Returns (sentiment, confidence)
        """
        text_lower = text.lower()
        
        # Positive indicators
        positive_words = ["amazing", "love", "great", "excellent", "perfect", "awesome"]
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        # Negative indicators
        negative_words = ["crash", "error", "broken", "fail", "bad", "terrible", "awful"]
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Use rating if available
        sentiment_score = 0
        if rating is not None:
            if rating >= 4:
                sentiment_score += 0.5
            elif rating <= 2:
                sentiment_score -= 0.5
        
        # Add word-based sentiment
        sentiment_score += (positive_count * 0.2) - (negative_count * 0.3)
        
        if sentiment_score > 0.3:
            return "positive", min(0.6 + (sentiment_score / 2), 1.0)
        elif sentiment_score < -0.3:
            return "negative", min(0.6 + abs(sentiment_score) / 2, 1.0)
        else:
            return "neutral", 0.5
    
    def classify(self, text: str, rating: int = None) -> Dict:
        """
        Classify feedback with confidence scores
        
        Returns:
            dict: {
                'category': str,
                'priority': str,
                'confidence': float,
                'confidence_breakdown': dict,
                'sentiment': str
            }
        """
        try:
            text_lower = text.lower()
            
            # Calculate confidence for each category
            bug_confidence = self.calculate_confidence(text, self.bug_keywords)
            feature_confidence = self.calculate_confidence(text, self.feature_keywords)
            critical_confidence = self.calculate_confidence(text, self.critical_keywords)
            
            # Determine sentiment
            sentiment, sentiment_confidence = self.analyze_sentiment(text, rating)
            
            # Classify category - prioritize bugs with strong indicators
            category = "General"
            category_confidence = 0.3  # Default low confidence
            
            # Check for bugs first (higher priority than complaints)
            if bug_confidence > 0.3:  # Lowered threshold for better bug detection
                category = "Bug"
                category_confidence = bug_confidence
                priority = PRIORITY_CONFIG["bug_priority"]
                # Ensure crash/error issues get Critical priority
                if critical_confidence > 0.3:
                    priority = "Critical"
                logger.info(f"Classified as Bug with priority {priority}")
            elif feature_confidence > 0.4:
                category = "Feature Request"
                category_confidence = feature_confidence
                priority = PRIORITY_CONFIG["feature_priority"]
                logger.info(f"Classified as Feature Request with priority {priority}")
            elif rating is not None:
                rating_val = int(rating)
                if rating_val >= CLASSIFICATION_CONFIG["praise_rating_threshold"]:
                    category = "Praise"
                    category_confidence = 0.7 + (rating_val - 4) * 0.1
                    priority = PRIORITY_CONFIG["praise_priority"]
                    logger.info(f"Classified as Praise (rating: {rating_val})")
                elif rating_val <= CLASSIFICATION_CONFIG["complaint_rating_threshold"]:
                    category = "Complaint"
                    category_confidence = 0.7 + (3 - rating_val) * 0.1
                    priority = PRIORITY_CONFIG["complaint_priority"]
                    logger.info(f"Classified as Complaint (rating: {rating_val})")
                else:
                    category = "Complaint"
                    category_confidence = 0.5
                    priority = PRIORITY_CONFIG["default_priority"]
            else:
                # Default based on sentiment
                if sentiment == "negative":
                    category = "Complaint"
                    category_confidence = sentiment_confidence
                    priority = PRIORITY_CONFIG["complaint_priority"]
                else:
                    category = "General"
                    priority = PRIORITY_CONFIG["default_priority"]
            
            # Override priority for critical keywords (only if category is already determined)
            if critical_confidence > 0.5 and category != "Praise":
                priority = "Critical"
                logger.warning(f"Priority elevated to Critical due to keywords")
            
            # Overall confidence is average of category and priority confidence
            overall_confidence = round((category_confidence + min(critical_confidence + 0.3, 1.0)) / 2, 2)
            
            result = {
                'category': category,
                'priority': priority,
                'confidence': overall_confidence,
                'confidence_breakdown': {
                    'category_confidence': category_confidence,
                    'bug_confidence': bug_confidence,
                    'feature_confidence': feature_confidence,
                    'priority_confidence': critical_confidence,
                    'sentiment_confidence': sentiment_confidence
                },
                'sentiment': sentiment
            }
            
            logger.debug(f"Classification result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in classification: {e}", exc_info=True)
            return {
                'category': 'General',
                'priority': 'Medium',
                'confidence': 0.0,
                'confidence_breakdown': {},
                'sentiment': 'neutral'
            }


# Singleton instance
_classifier = None

def get_classifier() -> FeedbackClassifier:
    """Get or create the classifier singleton"""
    global _classifier
    if _classifier is None:
        _classifier = FeedbackClassifier()
    return _classifier
