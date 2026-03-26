"""
Processing Logger for detailed decision tracking
Logs all classification decisions and processing steps
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List
import os


class ProcessingLogger:
    """
    Logs detailed processing history and decisions for audit trail
    """
    
    def __init__(self):
        self.logs = []
        self.start_time = datetime.now()
    
    def log_processing(self, source_id: str, source_type: str, 
                      classification: Dict, ticket: Dict, 
                      processing_time: float):
        """
        Log a single processing event
        
        Args:
            source_id: ID of the feedback source
            source_type: Type of source (review/email)
            classification: Classification results with confidence
            ticket: Generated ticket data
            processing_time: Time taken to process (seconds)
        """
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'source_id': source_id,
            'source_type': source_type,
            'category': classification['category'],
            'priority': classification['priority'],
            'confidence': classification['confidence'],
            'sentiment': classification['sentiment'],
            'bug_confidence': classification['confidence_breakdown'].get('bug_confidence', 0),
            'feature_confidence': classification['confidence_breakdown'].get('feature_confidence', 0),
            'category_confidence': classification['confidence_breakdown'].get('category_confidence', 0),
            'priority_confidence': classification['confidence_breakdown'].get('priority_confidence', 0),
            'sentiment_confidence': classification['confidence_breakdown'].get('sentiment_confidence', 0),
            'ticket_id': ticket['ticket_id'],
            'ticket_title': ticket['title'],
            'processing_time_ms': round(processing_time * 1000, 2),
            'status': 'success'
        }
        self.logs.append(log_entry)
    
    def log_error(self, source_id: str, source_type: str, error: str):
        """Log a processing error"""
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'source_id': source_id,
            'source_type': source_type,
            'category': 'ERROR',
            'priority': 'N/A',
            'confidence': 0.0,
            'sentiment': 'N/A',
            'bug_confidence': 0,
            'feature_confidence': 0,
            'category_confidence': 0,
            'priority_confidence': 0,
            'sentiment_confidence': 0,
            'ticket_id': 'N/A',
            'ticket_title': f"Error: {error[:50]}",
            'processing_time_ms': 0,
            'status': 'error'
        }
        self.logs.append(log_entry)
    
    def save(self, filepath: str = "outputs/processing_log.csv"):
        """Save logs to CSV file"""
        if not self.logs:
            return
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df = pd.DataFrame(self.logs)
        df.to_csv(filepath, index=False)
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return len(self.logs), elapsed
    
    def get_summary(self) -> Dict:
        """Get processing summary statistics"""
        if not self.logs:
            return {}
        
        df = pd.DataFrame(self.logs)
        
        summary = {
            'total_processed': len(df),
            'successful': len(df[df['status'] == 'success']),
            'errors': len(df[df['status'] == 'error']),
            'avg_confidence': df[df['status'] == 'success']['confidence'].mean(),
            'avg_processing_time_ms': df[df['status'] == 'success']['processing_time_ms'].mean(),
            'total_time_seconds': (datetime.now() - self.start_time).total_seconds(),
            'category_distribution': df['category'].value_counts().to_dict(),
            'priority_distribution': df['priority'].value_counts().to_dict(),
            'sentiment_distribution': df['sentiment'].value_counts().to_dict()
        }
        
        return summary


class MetricsCollector:
    """
    Collects and generates performance and accuracy metrics
    """
    
    def __init__(self):
        self.metrics = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_processed': 0,
            'successful_classifications': 0,
            'failed_classifications': 0,
            'avg_confidence': 0.0,
            'min_confidence': 1.0,
            'max_confidence': 0.0,
            'avg_processing_time_ms': 0.0,
            'total_processing_time_seconds': 0.0,
            'throughput_items_per_second': 0.0,
            'bugs_detected': 0,
            'features_detected': 0,
            'praise_detected': 0,
            'complaints_detected': 0,
            'critical_priority': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'low_priority': 0,
            'positive_sentiment': 0,
            'negative_sentiment': 0,
            'neutral_sentiment': 0
        }
    
    def update_from_summary(self, summary: Dict):
        """Update metrics from processing summary"""
        self.metrics['total_processed'] = summary.get('total_processed', 0)
        self.metrics['successful_classifications'] = summary.get('successful', 0)
        self.metrics['failed_classifications'] = summary.get('errors', 0)
        self.metrics['avg_confidence'] = round(summary.get('avg_confidence', 0), 3)
        self.metrics['avg_processing_time_ms'] = round(summary.get('avg_processing_time_ms', 0), 2)
        self.metrics['total_processing_time_seconds'] = round(summary.get('total_time_seconds', 0), 2)
        
        if self.metrics['total_processing_time_seconds'] > 0:
            self.metrics['throughput_items_per_second'] = round(
                self.metrics['total_processed'] / self.metrics['total_processing_time_seconds'], 2
            )
        
        # Category distribution
        categories = summary.get('category_distribution', {})
        self.metrics['bugs_detected'] = categories.get('Bug', 0)
        self.metrics['features_detected'] = categories.get('Feature Request', 0)
        self.metrics['praise_detected'] = categories.get('Praise', 0)
        self.metrics['complaints_detected'] = categories.get('Complaint', 0)
        
        # Priority distribution
        priorities = summary.get('priority_distribution', {})
        self.metrics['critical_priority'] = priorities.get('Critical', 0)
        self.metrics['high_priority'] = priorities.get('High', 0)
        self.metrics['medium_priority'] = priorities.get('Medium', 0)
        self.metrics['low_priority'] = priorities.get('Low', 0)
        
        # Sentiment distribution
        sentiments = summary.get('sentiment_distribution', {})
        self.metrics['positive_sentiment'] = sentiments.get('positive', 0)
        self.metrics['negative_sentiment'] = sentiments.get('negative', 0)
        self.metrics['neutral_sentiment'] = sentiments.get('neutral', 0)
    
    def update_confidence_range(self, confidences: List[float]):
        """Update min/max confidence from list"""
        if confidences:
            self.metrics['min_confidence'] = round(min(confidences), 3)
            self.metrics['max_confidence'] = round(max(confidences), 3)
    
    def save(self, filepath: str = "outputs/metrics.csv"):
        """Save metrics to CSV file"""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Convert to DataFrame with single row
        df = pd.DataFrame([self.metrics])
        
        # Check if file exists to append or create new
        if os.path.exists(filepath):
            existing = pd.read_csv(filepath)
            df = pd.concat([existing, df], ignore_index=True)
        
        df.to_csv(filepath, index=False)
    
    def print_summary(self):
        """Print metrics summary to console"""
        print("\n" + "="*70)
        print("PERFORMANCE METRICS")
        print("="*70)
        print(f"Total Processed: {self.metrics['total_processed']}")
        print(f"Successful: {self.metrics['successful_classifications']}")
        print(f"Failed: {self.metrics['failed_classifications']}")
        print(f"Success Rate: {(self.metrics['successful_classifications']/max(self.metrics['total_processed'],1)*100):.1f}%")
        print(f"\nAverage Confidence: {self.metrics['avg_confidence']:.3f}")
        print(f"Confidence Range: {self.metrics['min_confidence']:.3f} - {self.metrics['max_confidence']:.3f}")
        print(f"\nProcessing Time: {self.metrics['total_processing_time_seconds']:.2f}s")
        print(f"Average per Item: {self.metrics['avg_processing_time_ms']:.2f}ms")
        print(f"Throughput: {self.metrics['throughput_items_per_second']:.2f} items/sec")
        print(f"\nCategory Distribution:")
        print(f"  Bugs: {self.metrics['bugs_detected']}")
        print(f"  Features: {self.metrics['features_detected']}")
        print(f"  Praise: {self.metrics['praise_detected']}")
        print(f"  Complaints: {self.metrics['complaints_detected']}")
        print(f"\nPriority Distribution:")
        print(f"  Critical: {self.metrics['critical_priority']}")
        print(f"  High: {self.metrics['high_priority']}")
        print(f"  Medium: {self.metrics['medium_priority']}")
        print(f"  Low: {self.metrics['low_priority']}")
        print("="*70 + "\n")
