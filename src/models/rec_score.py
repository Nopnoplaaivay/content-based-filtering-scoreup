import numpy as np
import pandas as pd

from src.utils.time_utils import TimeUtils

class RecScore:
    NEVER_ATTEMPTED = 0 # Never attempted
    FREQUENTLY_WRONG = 1 # Frequently wrong (correct_ratio < 0.3)
    OCCASIONALLY_WRONG = 2 # Occasionally wrong (0.3 <= correct_ratio < 0.5)
    CORRECT = 3 # Correct (0.5 <= correct_ratio < 0.7)
    FREQUENTLY_CORRECT = 4 # Frequently correct (correct_ratio >= 0.7)

    # Define the review intervals for each box
    REVIEW_INTERVALS = {
        NEVER_ATTEMPTED: 1, # 1 day
        FREQUENTLY_WRONG: 2, # 2 day
        OCCASIONALLY_WRONG: 4, # 4 days
        CORRECT: 8, # 8 days
        FREQUENTLY_CORRECT: 16 # 16 days
    }

    # Define the score thresholds for each box
    ATTEMPT_THRESHOLD = 3  # Minimum number of attempts to be considered for review
    CORRECT_RATIO_THRESHOLD = 0.7  # Correct ratio threshold to be considered "frequently correct"
    WRONG_RATIO_THRESHOLD = 0.7  # Wrong ratio threshold to be considered "frequently wrong"

    def __init__(self, group_df):
        self.group_df = group_df
        self.leitner_score = self.leitner()

    # Forgetting curve score
    def forgetting_curve_score(self):
        max_created_at = self.group_df['created_at'].max()
        # print(f"Max created_at: {max_created_at}")
        time_diff = (TimeUtils.vn_current_time() - max_created_at).total_seconds() / 3600

        return 1 - np.exp(-time_diff / 24)
    
    def leitner(self):
        question_stats = self.group_df.agg({
            'score': ['count', 'mean', 'std'],
            'created_at': 'max'
        }).round(3)
    
        current_box = None

        # Determine current box 
        if question_stats['score']['count'] == 0:
            current_box = RecScore.NEVER_ATTEMPTED
        elif question_stats['score']['count'] < RecScore.ATTEMPT_THRESHOLD:
            if question_stats['score']['mean'] < 0.5:
                current_box = RecScore.OCCASIONALLY_WRONG 
            else:
                current_box = RecScore.CORRECT
        else:
            if question_stats['score']['mean'] >= RecScore.CORRECT_RATIO_THRESHOLD:
                current_box = RecScore.FREQUENTLY_CORRECT
            elif question_stats['score']['mean'] <= RecScore.WRONG_RATIO_THRESHOLD:
                current_box = RecScore.FREQUENTLY_WRONG
            else:
                current_box = RecScore.OCCASIONALLY_WRONG

        days_since_last_attempt = (TimeUtils.vn_current_time() - question_stats['created_at']['max']).days
        next_review_days = RecScore.REVIEW_INTERVALS[current_box]

        srs_score = max(0, min(days_since_last_attempt / next_review_days, 5))

        return srs_score