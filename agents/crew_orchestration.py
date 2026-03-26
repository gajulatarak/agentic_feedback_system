"""
CrewAI Agent Orchestration System
Defines agent classes with specific responsibilities and task workflows
"""

from crewai import Agent, Task, Crew, Process
from typing import List, Dict
from agents.nlp_classifier import get_classifier
from utils.logger import logger


class ClassifierAgent:
    """
    Agent responsible for classifying feedback into categories and priorities
    Uses NLP-based classification with confidence scoring
    """
    
    def __init__(self):
        self.agent = Agent(
            role='Feedback Classification Specialist',
            goal='Accurately classify customer feedback into categories and assign appropriate priorities based on urgency and impact',
            backstory="""You are an expert customer support analyst with years of experience 
            in triaging feedback. You excel at quickly identifying the nature of customer issues,
            whether they are bugs, feature requests, praise, or complaints. You understand the 
            technical implications and can assess the urgency and business impact of each piece 
            of feedback. Your classifications help support teams respond faster and more effectively.""",
            verbose=True,
            allow_delegation=False
        )
        self.classifier = get_classifier()
        logger.info("ClassifierAgent initialized")
    
    def create_task(self, feedback_data: Dict) -> Task:
        """Create a classification task for a piece of feedback"""
        return Task(
            description=f"""Classify the following customer feedback:
            
            Source: {feedback_data.get('source_id', 'Unknown')}
            Text: {feedback_data.get('text', '')}
            Rating: {feedback_data.get('rating', 'N/A')}
            
            Determine:
            1. Category (Bug, Feature Request, Praise, Complaint, General)
            2. Priority (Critical, High, Medium, Low)
            3. Confidence score for the classification
            4. Sentiment analysis
            """,
            agent=self.agent,
            expected_output="Classification with category, priority, and confidence scores"
        )
    
    def classify(self, text: str, rating=None) -> Dict:
        """Classify feedback using NLP engine"""
        logger.info(f"Classifying feedback: {text[:50]}...")
        result = self.classifier.classify(text, rating)
        logger.info(f"Classification complete: {result['category']} ({result['priority']}) - Confidence: {result['confidence']}")
        return result


class TicketCreatorAgent:
    """
    Agent responsible for creating structured support tickets
    Generates clear, actionable tickets with proper formatting
    """
    
    def __init__(self):
        self.agent = Agent(
            role='Support Ticket Creation Specialist',
            goal='Create well-structured, detailed support tickets that contain all necessary information for efficient resolution',
            backstory="""You are a meticulous support operations specialist who excels at 
            creating clear, actionable support tickets. You know how to extract key information 
            from customer feedback and format it in a way that makes it easy for support engineers 
            and product teams to understand and act upon. Your tickets include clear titles, 
            detailed descriptions, proper categorization, and all relevant metadata.""",
            verbose=True,
            allow_delegation=False
        )
        logger.info("TicketCreatorAgent initialized")
    
    def create_task(self, feedback_data: Dict, classification: Dict) -> Task:
        """Create a ticket creation task"""
        return Task(
            description=f"""Create a support ticket for the following classified feedback:
            
            Source: {feedback_data.get('source_id', 'Unknown')}
            Category: {classification.get('category', 'General')}
            Priority: {classification.get('priority', 'Medium')}
            Confidence: {classification.get('confidence', 0.0)}
            Description: {feedback_data.get('text', '')}
            
            Generate:
            1. Clear, actionable ticket title
            2. Structured description with key details
            3. Proper metadata (status, timestamps, etc.)
            4. Technical details if applicable
            """,
            agent=self.agent,
            expected_output="Complete structured ticket with all fields populated"
        )
    
    def create_ticket(self, source_id: str, classification: Dict, text: str, 
                     source_type: str = "feedback") -> Dict:
        """Create a structured ticket"""
        import uuid
        from datetime import datetime
        
        logger.info(f"Creating ticket for {source_id}")
        
        # Generate clear, actionable title
        category = classification['category']
        priority = classification['priority']
        confidence = classification['confidence']
        
        title = self._generate_title(text, category, priority, source_id)
        
        ticket = {
            "ticket_id": str(uuid.uuid4())[:8],
            "source_id": source_id,
            "source_type": source_type,
            "category": category,
            "priority": priority,
            "confidence": confidence,
            "sentiment": classification.get('sentiment', 'neutral'),
            "title": title,
            "description": text,
            "technical_details": self._extract_technical_details(text),
            "status": "Open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "assigned_to": None,
            "resolution": None
        }
        
        logger.info(f"Ticket created: {ticket['ticket_id']} - {title}")
        return ticket
    
    def _generate_title(self, text: str, category: str, priority: str, source_id: str) -> str:
        """Generate a clear, actionable ticket title"""
        text_lower = text.lower()
        
        # Extract key phrases
        if "crash" in text_lower:
            return f"{priority}: App Crash - {self._extract_context(text, 'crash')}"
        elif "login" in text_lower or "sign in" in text_lower:
            return f"{priority}: Login Issue - {source_id}"
        elif "error" in text_lower:
            return f"{priority}: Error - {self._extract_context(text, 'error')}"
        elif category == "Feature Request":
            feature = self._extract_feature_name(text)
            return f"{priority}: Feature Request - {feature}"
        elif category == "Praise":
            return f"{priority}: Positive Feedback - {source_id}"
        else:
            # Generic title with first few words
            words = text.split()[:6]
            return f"{priority}: {category} - {' '.join(words)}..."
    
    def _extract_context(self, text: str, keyword: str) -> str:
        """Extract context around a keyword"""
        words = text.split()
        for i, word in enumerate(words):
            if keyword in word.lower():
                # Get 3 words before and after
                start = max(0, i - 2)
                end = min(len(words), i + 4)
                return ' '.join(words[start:end])
        return text[:40]
    
    def _extract_feature_name(self, text: str) -> str:
        """Extract feature name from feature request"""
        text_lower = text.lower()
        if "dark mode" in text_lower:
            return "Dark Mode"
        elif "export" in text_lower and "pdf" in text_lower:
            return "PDF Export"
        elif "notification" in text_lower:
            return "Notifications"
        else:
            words = text.split()[:5]
            return ' '.join(words)
    
    def _extract_technical_details(self, text: str) -> str:
        """Extract technical details like device info, versions, etc."""
        import re
        
        technical_patterns = [
            r'(iPhone|Android|iOS|Samsung|Google Pixel)[\s\w\d]*',
            r'(version|v\.?)\s*[\d\.]+',
            r'(Step[s]?:.*?)(?=\.|$)',
        ]
        
        details = []
        for pattern in technical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            details.extend([m if isinstance(m, str) else m[0] for m in matches])
        
        return '; '.join(details) if details else 'N/A'


class FeedbackProcessingCrew:
    """
    Orchestrates the multi-agent feedback processing workflow
    Manages the complete pipeline from raw feedback to structured tickets
    """
    
    def __init__(self):
        self.classifier_agent = ClassifierAgent()
        self.ticket_creator_agent = TicketCreatorAgent()
        logger.info("FeedbackProcessingCrew initialized with 2 agents")
    
    def process_feedback(self, feedback_data: Dict) -> Dict:
        """
        Process a single piece of feedback through the agent pipeline
        
        Args:
            feedback_data: Dict containing 'source_id', 'text', 'rating' (optional), 'source_type'
        
        Returns:
            Dict: Structured ticket with confidence breakdown
        """
        try:
            # Step 1: Classify feedback
            classification = self.classifier_agent.classify(
                feedback_data['text'],
                feedback_data.get('rating')
            )
            
            # Step 2: Create ticket
            ticket = self.ticket_creator_agent.create_ticket(
                feedback_data['source_id'],
                classification,
                feedback_data['text'],
                feedback_data.get('source_type', 'feedback')
            )
            
            # Add confidence breakdown to ticket for logging
            ticket['bug_confidence'] = classification['confidence_breakdown'].get('bug_confidence', 0)
            ticket['feature_confidence'] = classification['confidence_breakdown'].get('feature_confidence', 0)
            ticket['category_confidence'] = classification['confidence_breakdown'].get('category_confidence', 0)
            ticket['priority_confidence'] = classification['confidence_breakdown'].get('priority_confidence', 0)
            ticket['sentiment_confidence'] = classification['confidence_breakdown'].get('sentiment_confidence', 0)
            
            logger.info(f"Successfully processed feedback {feedback_data['source_id']}")
            return ticket
            
        except Exception as e:
            logger.error(f"Error processing feedback {feedback_data.get('source_id')}: {e}", exc_info=True)
            raise
    
    def process_batch(self, feedback_list: List[Dict]) -> List[Dict]:
        """
        Process multiple pieces of feedback
        
        Args:
            feedback_list: List of feedback data dicts
        
        Returns:
            List[Dict]: List of structured tickets
        """
        logger.info(f"Processing batch of {len(feedback_list)} feedback items")
        tickets = []
        
        for feedback in feedback_list:
            try:
                ticket = self.process_feedback(feedback)
                tickets.append(ticket)
            except Exception as e:
                logger.error(f"Failed to process {feedback.get('source_id')}: {e}")
                continue
        
        logger.info(f"Batch processing complete: {len(tickets)} tickets created")
        return tickets
