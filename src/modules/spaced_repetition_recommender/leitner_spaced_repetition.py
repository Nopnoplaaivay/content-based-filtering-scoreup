import numpy as np
import pandas as pd

from src.utils.time_utils import TimeUtils

class LeitnerSpacedRepetition:
    NEVER_ATTEMPTED = 0 # Never attempted
    FREQUENTLY_WRONG = 1 # Frequently wrong (correct_ratio < 0.3)
    OCCASIONALLY_WRONG = 2 # Occasionally wrong (0.3 <= correct_ratio < 0.5)
    CORRECT = 3 # Correct (0.5 <= correct_ratio < 0.7)
    FREQUENTLY_CORRECT = 4 # Frequently correct (correct_ratio >= 0.7)
    # MASTERED
    # 100% CORRECT
    # BOOKMARKEDz

    # NEVER_ATTEMPTED_MESSAGE = "This cluster was never attempted, and it is recommended to start practicing these questions."
    # FREQUENTLY_WRONG_MESSAGE = "Your performance in this field has been frequently incorrect, so focused practice is highly recommended."
    # OCCASIONALLY_WRONG_MESSAGE = "Your performance in this field has been occasionally incorrect, indicating a need for improvement."
    # CORRECT_MESSAGE = "You have performed well in this field, but consistent review is important to maintain your understanding."
    # FREQUENTLY_CORRECT_MESSAGE = "You have frequently answered questions in this field correctly. A periodic review is recommended to retain knowledge."

    NEVER_ATTEMPTED_MESSAGE = "Nhóm câu hỏi này chưa từng được bạn thử, và chúng tôi khuyến nghị bạn nên bắt đầu luyện tập ngay."
    FREQUENTLY_WRONG_MESSAGE = "Hiệu suất của bạn trong lĩnh vực này thường xuyên sai, do đó, cần tập trung luyện tập."
    OCCASIONALLY_WRONG_MESSAGE = "Hiệu suất của bạn trong lĩnh vực này thỉnh thoảng không tốt, cho thấy cần cải thiện thêm."
    CORRECT_MESSAGE = "Bạn đã làm tốt trong lĩnh vực này, nhưng việc ôn tập thường xuyên là rất quan trọng để duy trì sự hiểu biết."
    FREQUENTLY_CORRECT_MESSAGE = "Bạn thường xuyên trả lời đúng các câu hỏi trong lĩnh vực này. Việc ôn tập định kỳ được khuyến nghị để duy trì kiến thức."

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

    @classmethod
    def leitner_score(cls, group_df):
        question_stats = group_df.agg({
            'score': ['count', 'mean', 'std'],
            'created_at': 'max'
        }).round(3)
    
        current_box = None

        # Determine current box 
        if question_stats['score']['count'] == 0:
            current_box = cls.NEVER_ATTEMPTED
        elif question_stats['score']['count'] < cls.ATTEMPT_THRESHOLD:
            if question_stats['score']['mean'] < 0.5:
                current_box = cls.OCCASIONALLY_WRONG
            else:
                current_box = cls.CORRECT
        else:
            if question_stats['score']['mean'] >= cls.CORRECT_RATIO_THRESHOLD:
                current_box = cls.FREQUENTLY_CORRECT
            elif question_stats['score']['mean'] <= cls.WRONG_RATIO_THRESHOLD:
                current_box = cls.FREQUENTLY_WRONG
            else:
                current_box = cls.OCCASIONALLY_WRONG

        days_since_last_attempt = (TimeUtils.vn_current_time() - question_stats['created_at']['max']).days
        next_review_days = cls.REVIEW_INTERVALS[current_box]

        leitner_score = max(0, min(days_since_last_attempt / next_review_days, 5))

        message = None
        # Generate a reason based on the current box
        if current_box == cls.NEVER_ATTEMPTED:
            message = cls.NEVER_ATTEMPTED_MESSAGE
        elif current_box == cls.FREQUENTLY_WRONG:
            message = cls.FREQUENTLY_WRONG_MESSAGE
        elif current_box == cls.OCCASIONALLY_WRONG:
            message = cls.OCCASIONALLY_WRONG_MESSAGE
        elif current_box == cls.CORRECT:
            message = cls.CORRECT_MESSAGE
        elif current_box == cls.FREQUENTLY_CORRECT:
            message = cls.FREQUENTLY_CORRECT_MESSAGE

        return leitner_score, message