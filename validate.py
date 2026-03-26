"""
Validation script to compare generated tickets against expected classifications
"""

import pandas as pd
from config import DATA_PATHS
from utils.logger import logger


def validate_classifications():
    """Compare generated tickets against expected classifications"""
    
    try:
        logger.info("Starting classification validation")
        
        # Load generated tickets
        tickets = pd.read_csv(DATA_PATHS["output_tickets"])
        logger.info(f"Loaded {len(tickets)} generated tickets")
        
        # Load expected classifications
        expected = pd.read_csv("data/expected_classifications.csv")
        logger.info(f"Loaded {len(expected)} expected classifications")
        
        # Merge on source_id
        comparison = expected.merge(
            tickets[["source_id", "category", "priority"]], 
            on="source_id", 
            suffixes=("_expected", "_actual")
        )
        
        # Calculate accuracy
        category_matches = (comparison["category_expected"] == comparison["category_actual"]).sum()
        priority_matches = (comparison["priority_expected"] == comparison["priority_actual"]).sum()
        
        total = len(comparison)
        category_accuracy = (category_matches / total) * 100
        priority_accuracy = (priority_matches / total) * 100
        
        # Display results
        print("\n" + "="*70)
        print("VALIDATION RESULTS")
        print("="*70)
        print(f"Total samples validated: {total}")
        print(f"\nCategory Accuracy: {category_accuracy:.1f}% ({category_matches}/{total})")
        print(f"Priority Accuracy: {priority_accuracy:.1f}% ({priority_matches}/{total})")
        print("="*70)
        
        # Show mismatches
        category_mismatches = comparison[comparison["category_expected"] != comparison["category_actual"]]
        if not category_mismatches.empty:
            print(f"\n{len(category_mismatches)} Category Mismatches:")
            print("-"*70)
            for _, row in category_mismatches.iterrows():
                print(f"  {row['source_id']}: Expected '{row['category_expected']}', Got '{row['category_actual']}'")
        
        priority_mismatches = comparison[comparison["priority_expected"] != comparison["priority_actual"]]
        if not priority_mismatches.empty:
            print(f"\n{len(priority_mismatches)} Priority Mismatches:")
            print("-"*70)
            for _, row in priority_mismatches.iterrows():
                print(f"  {row['source_id']}: Expected '{row['priority_expected']}', Got '{row['priority_actual']}'")
        
        print("\n" + "="*70 + "\n")
        
        logger.info(f"Validation complete - Category: {category_accuracy:.1f}%, Priority: {priority_accuracy:.1f}%")
        
        return category_accuracy, priority_accuracy
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        print(f"Error during validation: {e}")
        return None, None


if __name__ == "__main__":
    validate_classifications()
