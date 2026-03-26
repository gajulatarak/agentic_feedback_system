"""
Main entry point for the Agentic Feedback System
Processes customer feedback using CrewAI agents with error handling and logging
"""

import pandas as pd
import os
import time
from agents.crew_orchestration import FeedbackProcessingCrew
from config import DATA_PATHS, CREWAI_CONFIG
from utils.logger import logger, log_exception
from utils.processing_logger import ProcessingLogger, MetricsCollector


def process_feedback():
    """
    Process all feedback sources and generate tickets
    Uses CrewAI multi-agent system for orchestration
    """
    try:
        logger.info("=" * 60)
        logger.info("Starting Agentic Feedback Processing System")
        logger.info("=" * 60)
        
        # Initialize the multi-agent crew
        crew = FeedbackProcessingCrew()
        logger.info("Multi-agent crew initialized successfully")
        
        # Initialize processing logger and metrics collector
        proc_logger = ProcessingLogger()
        metrics = MetricsCollector()
        
        tickets = []
        processed_count = 0
        error_count = 0
        confidences = []
        
        # Process app store reviews
        try:
            logger.info(f"Loading reviews from {DATA_PATHS['app_store_reviews']}")
            reviews = pd.read_csv(DATA_PATHS["app_store_reviews"])
            logger.info(f"Found {len(reviews)} reviews to process")
            
            for idx, row in reviews.iterrows():
                try:
                    logger.info(f"Processing review {idx + 1}/{len(reviews)}: {row['review_id']}")
                    
                    # Track processing time
                    start_time = time.time()
                    
                    # Prepare feedback data for agent processing
                    feedback_data = {
                        'source_id': row['review_id'],
                        'text': row['review_text'],
                        'rating': row['rating'],
                        'source_type': 'review'
                    }
                    
                    # Process through agent pipeline
                    ticket = crew.process_feedback(feedback_data)
                    
                    # Get classification from ticket
                    classification = {
                        'category': ticket['category'],
                        'priority': ticket['priority'],
                        'confidence': ticket['confidence'],
                        'sentiment': ticket['sentiment'],
                        'confidence_breakdown': {
                            'bug_confidence': ticket.get('bug_confidence', 0),
                            'feature_confidence': ticket.get('feature_confidence', 0),
                            'category_confidence': ticket.get('category_confidence', 0),
                            'priority_confidence': ticket.get('priority_confidence', 0),
                            'sentiment_confidence': ticket.get('sentiment_confidence', 0)
                        }
                    }
                    
                    processing_time = time.time() - start_time
                    
                    # Log processing details
                    proc_logger.log_processing(
                        row['review_id'], 
                        'review', 
                        classification, 
                        ticket, 
                        processing_time
                    )
                    
                    tickets.append(ticket)
                    confidences.append(ticket['confidence'])
                    processed_count += 1
                    
                except Exception as e:
                    error_count += 1
                    proc_logger.log_error(row.get('review_id', 'unknown'), 'review', str(e))
                    log_exception(logger, e, f"Error processing review {row.get('review_id', 'unknown')}")
                    
        except Exception as e:
            log_exception(logger, e, "Error loading or processing reviews")
        
        # Process support emails
        try:
            logger.info(f"Loading emails from {DATA_PATHS['support_emails']}")
            emails = pd.read_csv(DATA_PATHS["support_emails"])
            logger.info(f"Found {len(emails)} emails to process")
            
            for idx, row in emails.iterrows():
                try:
                    logger.info(f"Processing email {idx + 1}/{len(emails)}: {row['email_id']}")
                    
                    # Track processing time
                    start_time = time.time()
                    
                    # Prepare feedback data for agent processing
                    text = row["subject"] + " " + row["body"]
                    feedback_data = {
                        'source_id': row['email_id'],
                        'text': text,
                        'rating': None,
                        'source_type': 'email'
                    }
                    
                    # Process through agent pipeline
                    ticket = crew.process_feedback(feedback_data)
                    
                    # Get classification from ticket
                    classification = {
                        'category': ticket['category'],
                        'priority': ticket['priority'],
                        'confidence': ticket['confidence'],
                        'sentiment': ticket['sentiment'],
                        'confidence_breakdown': {
                            'bug_confidence': ticket.get('bug_confidence', 0),
                            'feature_confidence': ticket.get('feature_confidence', 0),
                            'category_confidence': ticket.get('category_confidence', 0),
                            'priority_confidence': ticket.get('priority_confidence', 0),
                            'sentiment_confidence': ticket.get('sentiment_confidence', 0)
                        }
                    }
                    
                    processing_time = time.time() - start_time
                    
                    # Log processing details
                    proc_logger.log_processing(
                        row['email_id'], 
                        'email', 
                        classification, 
                        ticket, 
                        processing_time
                    )
                    
                    tickets.append(ticket)
                    confidences.append(ticket['confidence'])
                    processed_count += 1
                    
                except Exception as e:
                    error_count += 1
                    proc_logger.log_error(row.get('email_id', 'unknown'), 'email', str(e))
                    log_exception(logger, e, f"Error processing email {row.get('email_id', 'unknown')}")
                    
        except Exception as e:
            log_exception(logger, e, "Error loading or processing emails")
        
        # Save tickets to CSV
        if tickets:
            try:
                df = pd.DataFrame(tickets)
                output_path = DATA_PATHS["output_tickets"]
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                df.to_csv(output_path, index=False)
                logger.info(f"Successfully saved {len(tickets)} tickets to {output_path}")
                
                # Save processing logs
                log_count, elapsed = proc_logger.save("outputs/processing_log.csv")
                logger.info(f"Saved {log_count} processing log entries to outputs/processing_log.csv")
                
                # Generate and save metrics
                summary = proc_logger.get_summary()
                metrics.update_from_summary(summary)
                metrics.update_confidence_range(confidences)
                metrics.save("outputs/metrics.csv")
                logger.info(f"Saved metrics to outputs/metrics.csv")
                
                # Print summary
                print(f"\n{'='*60}")
                print(f"Processing complete!")
                print(f"Total processed: {processed_count}")
                print(f"Errors encountered: {error_count}")
                print(f"Tickets saved to: {output_path}")
                print(f"Processing log: outputs/processing_log.csv")
                print(f"Metrics: outputs/metrics.csv")
                print(f"{'='*60}\n")
                
                # Print metrics summary
                metrics.print_summary()
                
            except Exception as e:
                log_exception(logger, e, "Error saving output files")
                raise
        else:
            logger.warning("No tickets were generated")
            print("Warning: No tickets were generated. Check logs for details.")
            
    except Exception as e:
        log_exception(logger, e, "Critical error in process_feedback")
        raise


if __name__ == "__main__":
    try:
        process_feedback()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\nProcess interrupted by user")
    except Exception as e:
        logger.error("Fatal error during processing")
        print(f"\nFatal error: {e}")
        print("Check logs/app.log for details")
        exit(1)
