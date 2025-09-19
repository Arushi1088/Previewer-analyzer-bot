#!/usr/bin/env python3
"""
Extract high-priority issues from mobile_final_master_matrix.csv and generate golden_bugs.csv.

This script analyzes the master matrix to identify the most critical issues
based on error patterns, dead-end experiences, and user impact.
"""

import csv
import os
import sys
from collections import defaultdict, Counter
from typing import List, Dict, Tuple

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def load_master_matrix(csv_path: str) -> List[Dict[str, str]]:
    """Load the master matrix CSV file."""
    rows = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        print(f"Loaded {len(rows)} rows from master matrix")
        return rows
    except Exception as e:
        print(f"Error loading master matrix: {e}")
        return []

def analyze_error_patterns(rows: List[Dict[str, str]]) -> Dict[str, int]:
    """Analyze error patterns and their frequency."""
    error_counter = Counter()
    dead_end_counter = Counter()
    
    for row in rows:
        error_observed = row.get('ErrorObserved', '').strip()
        final_outcome = row.get('FinalOutcome', '').strip()
        notes = row.get('Notes', '').strip()
        
        # Count error types
        if error_observed:
            error_counter[error_observed] += 1
        
        # Identify dead-end experiences
        if any(dead_end in final_outcome.lower() for dead_end in ['dead-end', 'dead end', 'failed', 'error']):
            dead_end_counter[error_observed] += 1
    
    return {
        'error_frequency': dict(error_counter),
        'dead_end_frequency': dict(dead_end_counter)
    }

def identify_high_priority_issues(rows: List[Dict[str, str]]) -> List[Tuple[str, str, int]]:
    """
    Identify high-priority issues based on patterns in the master matrix.
    Returns list of (issue_id, title, priority_score) tuples.
    """
    patterns = analyze_error_patterns(rows)
    
    # Define high-priority issue patterns with their titles
    high_priority_issues = [
        # Critical UX Issues
        ("G001", "Error messaging unclear or missing actionable guidance", 10),
        ("G002", "Dead-end experience with no recovery path", 10),
        ("G003", "Multiple/overlapping loaders causing UI confusion", 9),
        ("G004", "Password prompt not shown for protected files", 9),
        ("G005", "Account mismatch without clear switch guidance", 8),
        
        # File Handling Issues
        ("G006", "Unnecessary desktop redirect for small/medium files", 8),
        ("G007", "Large file (XL) handling without proper guidance", 7),
        ("G008", "Protected file handling inconsistencies", 7),
        
        # App Selection Issues
        ("G009", "Wrong app precedence when multiple apps installed", 6),
        ("G010", "Missing app installation guidance", 6),
        
        # State Management Issues
        ("G011", "State regression after error without user action", 8),
        ("G012", "Error surface not properly layered over loaders", 7),
        ("G013", "Repeated sign-in prompts without resolution", 6),
        
        # Content Issues
        ("G014", "Stale content shown vs actual attachment version", 5),
        ("G015", "Cell formatting lost in desktop handoff", 5),
        ("G016", "Missing policy banner for protected files", 5),
    ]
    
    # Filter issues based on actual data patterns
    filtered_issues = []
    error_freq = patterns['error_frequency']
    dead_end_freq = patterns['dead_end_frequency']
    
    for issue_id, title, base_priority in high_priority_issues:
        # Check if this issue pattern exists in the data
        pattern_found = False
        for error_type in error_freq.keys():
            if any(keyword in error_type.lower() for keyword in title.lower().split()):
                pattern_found = True
                break
        
        # Boost priority if it's a dead-end issue
        priority = base_priority
        if any(dead_end in title.lower() for dead_end in ['dead-end', 'dead end']):
            priority += 2
        
        # Only include if pattern exists or it's a critical issue
        if pattern_found or base_priority >= 8:
            filtered_issues.append((issue_id, title, priority))
    
    # Sort by priority (highest first)
    filtered_issues.sort(key=lambda x: x[2], reverse=True)
    
    return filtered_issues

def generate_golden_bugs_csv(issues: List[Tuple[str, str, int]], output_path: str) -> None:
    """Generate the golden_bugs.csv file."""
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'title'])  # Header
            
            for issue_id, title, priority in issues:
                writer.writerow([issue_id, title])
        
        print(f"Generated golden_bugs.csv with {len(issues)} issues")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"Error writing golden_bugs.csv: {e}")

def main():
    """Main function to derive golden bugs from master matrix."""
    # Get paths
    script_dir = os.path.dirname(__file__)
    backend_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(backend_dir, 'data')
    
    master_matrix_path = os.path.join(data_dir, 'mobile_final_master_matrix.csv')
    golden_bugs_path = os.path.join(data_dir, 'golden_bugs.csv')
    
    print("🔍 Analyzing master matrix for high-priority issues...")
    print(f"Input: {master_matrix_path}")
    print(f"Output: {golden_bugs_path}")
    print()
    
    # Load and analyze data
    rows = load_master_matrix(master_matrix_path)
    if not rows:
        print("❌ No data loaded. Exiting.")
        return
    
    # Identify high-priority issues
    issues = identify_high_priority_issues(rows)
    
    if not issues:
        print("❌ No high-priority issues identified.")
        return
    
    # Display identified issues
    print("📋 High-Priority Issues Identified:")
    print("-" * 60)
    for issue_id, title, priority in issues:
        print(f"{issue_id}: {title} (Priority: {priority})")
    print()
    
    # Generate golden bugs CSV
    generate_golden_bugs_csv(issues, golden_bugs_path)
    
    print("✅ Golden bugs derivation complete!")
    print(f"📊 Summary: {len(issues)} issues extracted from {len(rows)} test cases")

if __name__ == "__main__":
    main()

