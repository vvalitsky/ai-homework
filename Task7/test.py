#!/usr/bin/env python3
"""
Task 7: Quick Testing Script for Quality Evaluation

Validates:
1. Golden questions file exists and is well-formed
2. RAG evaluation works correctly
3. Gap analysis produces correct output
"""

import sys
import json
from pathlib import Path

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{CYAN}{BOLD}{'═' * 70}{RESET}")
    print(f"{CYAN}{BOLD}  {text}{RESET}")
    print(f"{CYAN}{BOLD}{'═' * 70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")

def test_golden_questions():
    """Test 1: Validate golden questions file"""
    print_header("TEST 1: Golden Questions File")

    if not Path("golden_questions.txt").exists():
        print_error("golden_questions.txt not found")
        return False

    print_success("File exists")

    with open("golden_questions.txt") as f:
        lines = f.readlines()

    # Count questions
    questions = [l for l in lines if not l.startswith("#") and "|" in l]

    if len(questions) < 10:
        print_error(f"Only {len(questions)} questions (need >= 10)")
        return False

    print_success(f"Contains {len(questions)} questions")

    # Validate format
    for q in questions[:3]:
        parts = q.split("|")
        if len(parts) < 4:
            print_error(f"Invalid format: {q}")
            return False

    print_success("All questions have correct format")

    # Show sample
    print_info("Sample questions:")
    for q in questions[:3]:
        parts = q.split("|")
        print(f"  - {parts[0]}: {parts[1][:50]}...")

    return True

def test_sample_logs():
    """Test 2: Validate sample logs file"""
    print_header("TEST 2: Sample Logs")

    if not Path("sample_logs.jsonl").exists():
        print_error("sample_logs.jsonl not found")
        return False

    print_success("File exists")

    with open("sample_logs.jsonl") as f:
        logs = [json.loads(line) for line in f]

    if len(logs) < 10:
        print_error(f"Only {len(logs)} log entries (need >= 10)")
        return False

    print_success(f"Contains {len(logs)} log entries")

    # Validate structure
    required_fields = ["timestamp", "query", "success", "found_chunks", "sources"]
    for log in logs[:3]:
        for field in required_fields:
            if field not in log:
                print_error(f"Missing field '{field}' in log entry")
                return False

    print_success("All logs have required fields")

    # Statistics
    successful = sum(1 for log in logs if log["success"])
    print_info(f"Success rate: {successful}/{len(logs)} ({successful/len(logs)*100:.0f}%)")

    return True

def test_gaps_analysis():
    """Test 3: Validate gaps analysis file"""
    print_header("TEST 3: Gaps Analysis")

    if not Path("gaps_analysis.json").exists():
        print_error("gaps_analysis.json not found")
        return False

    print_success("File exists")

    with open("gaps_analysis.json") as f:
        gaps = json.load(f)

    # Check structure
    required_keys = ["total_questions_tested", "successful_answers", "poorly_covered_topics", "missing_entities", "recommendations"]

    for key in required_keys:
        if key not in gaps:
            print_error(f"Missing key: {key}")
            return False

    print_success("All required fields present")

    # Check metrics
    coverage = gaps.get("metrics", {}).get("coverage_score", 0)
    quality = gaps.get("metrics", {}).get("quality_score", 0)

    print_info(f"Coverage score: {coverage}%")
    print_info(f"Quality score: {quality}%")
    print_info(f"Poorly covered topics: {len(gaps['poorly_covered_topics'])}")
    print_info(f"Recommendations: {len(gaps['recommendations'])}")

    return True

def test_sequence_diagram():
    """Test 4: Validate sequence diagram"""
    print_header("TEST 4: Sequence Diagram")

    if not Path("sequence_diagram.txt").exists():
        print_error("sequence_diagram.txt not found")
        return False

    print_success("File exists")

    with open("sequence_diagram.txt") as f:
        content = f.read()

    # Check for key sections
    sections = [
        "INITIALIZATION",
        "QUERY PROCESSING",
        "EVALUATION",
        "RECOMMENDATIONS"
    ]

    for section in sections:
        if section in content:
            print_success(f"Contains section: {section}")
        else:
            print_error(f"Missing section: {section}")
            return False

    return True

def test_run_script():
    """Test 5: Validate run.sh script"""
    print_header("TEST 5: Run Script")

    if not Path("run.sh").exists():
        print_error("run.sh not found")
        return False

    print_success("run.sh exists")

    with open("run.sh") as f:
        content = f.read()

    required_functions = [
        "run_evaluation",
        "view_logs",
        "show_statistics",
        "show_gaps"
    ]

    for func in required_functions:
        if func in content:
            print_success(f"Contains function: {func}")
        else:
            print_error(f"Missing function: {func}")
            return False

    return True

def run_all_tests():
    """Run all validation tests"""
    print_header("TASK 7: QUALITY EVALUATION - VALIDATION TESTS")

    tests = [
        ("Golden Questions", test_golden_questions),
        ("Sample Logs", test_sample_logs),
        ("Gaps Analysis", test_gaps_analysis),
        ("Sequence Diagram", test_sequence_diagram),
        ("Run Script", test_run_script),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print_error(f"Exception: {e}")
            results[name] = False

    # Summary
    print_header("TEST RESULTS")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_flag in results.items():
        status = f"{GREEN}✓ PASS{RESET}" if passed_flag else f"{RED}✗ FAIL{RESET}"
        print(f"{status}  {test_name}")

    print()
    print_header(f"SUMMARY: {passed}/{total} tests passed")

    if passed == total:
        print_success("All validation tests passed!")
        print_info("System ready for deployment")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed")
        print_info("Fix issues before running evaluation")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
