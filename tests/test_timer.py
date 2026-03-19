from datetime import datetime
from utilities.timers import Timer
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def run_manual_tests():
    test_cases = [
        (datetime(2026, 2, 8, 10, 15, 0), 15, 2, True,"Exact Boundary"),   # exact boundary
        (datetime(2026, 2, 8, 10, 15, 1), 15, 2, True,"Within Tolerance"),   # within tolerance
        (datetime(2026, 2, 8, 10, 15, 5), 15, 2, False,"Outside Tolerance"),  # outside tolerance
        (datetime(2026, 2, 8, 10, 10, 0), 5, 2, True,"5-min Mark"),    # 5-min mark
        (datetime(2026, 2, 8, 10, 10, 0), 3, 2, False,"Not a 3-min Mark"),   # not a 3-min mark
    ]
    passed=0
    for ts, interval, tol, expected,test_type in test_cases:
        result = Timer.is_n_min_mark(ts, interval_in_minutes=interval, tolerance=tol)
        if result==expected:
            passed+=1
            logging.info(f"Test Case : {test_type:<20} → PASSED")
        else:
            logging.info(f"Test Case : {test_type:<20} → FAILED")
    logging.info(f"{passed}/{len(test_cases)} Tests Passed")

if __name__ == "__main__":
    run_manual_tests()