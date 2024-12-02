import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from dns.e164 import query

from src.db.entities.questions import Questions
from src.db.entities.logs import Logs
from src.utils.logger import LOGGER

class Difficulty:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.questions = Questions(notion_database_id=notion_database_id)
        self.logs = Logs(notion_database_id=notion_database_id)

    @staticmethod
    def calculate_normality_metrics(data):
        """
        Calculate multiple metrics to assess normality
        """
        _, shapiro_p_value = stats.shapiro(data)
        skewness = stats.skew(data)
        kurtosis = stats.kurtosis(data)
        _, qq_data = stats.probplot(data, dist="norm")
        qq_correlation = np.corrcoef(qq_data[0], qq_data[1])[0, 1]
        
        return {
            'shapiro_p_value': shapiro_p_value,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'qq_correlation': qq_correlation
        }
    
    @classmethod
    def optimize_weights_for_normality(
        cls, 
        accuracy_difficulties, 
        time_difficulties, 
        max_iterations=100
    ):
        """
        Find weights that create a distribution closest to normal
        
        Args:
        accuracy_difficulties (array-like): Accuracy difficulty scores
        time_difficulties (array-like): Time difficulty scores
        max_iterations (int): Maximum number of weight combinations to try
        
        Returns:
        dict: Optimal weight configuration
        """
        # Convert to numpy arrays
        acc_diffs = np.array(accuracy_difficulties)
        time_diffs = np.array(time_difficulties)
        
        # Ensure difficulties are scaled similarly
        acc_diffs = (acc_diffs - acc_diffs.min()) / (acc_diffs.max() - acc_diffs.min())
        time_diffs = (time_diffs - time_diffs.min()) / (time_diffs.max() - time_diffs.min())
        
        # Initialize best configuration
        best_config = {
            'accuracy_weight': 0,
            'time_weight': 0,
            'normality_score': float('-inf'),
            'combined_difficulties': None,
            'normality_metrics': None
        }
        
        # Systematic search for optimal weights
        np.random.seed(42)  # For reproducibility
        for _ in range(max_iterations):
            # Generate random weights that sum to 1
            accuracy_weight = np.random.uniform(0, 1)
            time_weight = 1 - accuracy_weight
            
            # Calculate combined difficulties
            combined_difficulties = (
                accuracy_weight * acc_diffs + 
                time_weight * time_diffs
            )
            
            # Calculate normality metrics
            normality_metrics = cls.calculate_normality_metrics(combined_difficulties)
            
            # Compute a composite normality score
            # Higher is better, closer to normal distribution
            normality_score = (
                normality_metrics['shapiro_p_value'] *
                (1 - abs(normality_metrics['skewness'])) * 
                (1 - abs(normality_metrics['kurtosis']))
            )

            if np.isnan(normality_score):
                continue

            # Update best configuration if improved
            if normality_score > best_config['normality_score']:
                best_config = {
                    'accuracy_weight': accuracy_weight,
                    'time_weight': time_weight,
                    'normality_score': normality_score,
                    'combined_difficulties': combined_difficulties,
                    'normality_metrics': normality_metrics
                }
        
        return best_config
    
    @classmethod
    def visualize_distribution(cls, difficulties, title="Difficulty Distribution"):
        """
        Create comprehensive visualization of distribution
        """
        plt.figure(figsize=(15, 5))
        
        # Histogram
        plt.subplot(131)
        plt.hist(difficulties, bins='auto', density=True, alpha=0.7, color='skyblue')
        plt.title(f'{title}\nHistogram')
        plt.xlabel('Difficulty')
        plt.ylabel('Density')
        
        # Q-Q Plot
        plt.subplot(132)
        stats.probplot(difficulties, dist="norm", plot=plt)
        plt.title('Q-Q Plot')
        
        # Box Plot
        plt.subplot(133)
        plt.boxplot(difficulties)
        plt.title('Box Plot')
        
        plt.tight_layout()
        plt.show()
    
    @classmethod
    def full_analysis(cls, accuracy_difficulties, time_difficulties):
        """
        Comprehensive analysis of difficulty distribution
        """
        # Optimize weights
        result = cls.optimize_weights_for_normality(
            accuracy_difficulties, 
            time_difficulties
        )
        
        # # Print detailed results
        LOGGER.info("Optimal Weight Configuration:")
        LOGGER.info(f"  Accuracy Weight: {result['accuracy_weight']:.4f}")
        LOGGER.info(f"  Time Weight: {result['time_weight']:.4f}")
        LOGGER.info(f"  Normality Score: {result['normality_score']:.4f}")
        
        # Visualize distribution
        # cls.visualize_distribution(
        #     result['combined_difficulties'],
        #     title="Optimized Difficulty Distribution"
        # )
        
        return result
    
    def update(self):
        try:
            '''
            Optimizing weights for normality
            '''
            questions = self.questions.fetch_all()
            acc_diffs = []
            time_diffs = []
            for ques in questions:
                ques_id = ques["_id"]
                logs = self.logs.fetch_all({
                    "exercise_id": ques_id,
                    "time_cost": {"$gt": 1000}
                })

                if len(logs) > 0:
                    accuracies = []
                    time_costs = []
                    for log in logs:
                        total_answers = len(log["user_ans"])
                        correct_answers = sum(
                            [
                                1
                                for i in range(total_answers)
                                if log["correct_ans"][i] == log["user_ans"][i]
                            ]
                        )
                        accuracy = correct_answers / total_answers
                        accuracies.append(accuracy)
                        time_costs.append(log["time_cost"])

                    # Calculate normality metrics
                    accuracies = np.array(accuracies)
                    time_costs = np.array(time_costs)
                    min_time_costs = np.min(time_costs)
                    max_time_costs = np.max(time_costs)

                    # Calculate time difficulty
                    normalized_time_costs = (time_costs - min_time_costs) / (max_time_costs - min_time_costs)
                    time_costs_difficulty = np.mean(normalized_time_costs)

                    # Calculate accuracy difficulty
                    high_threshold = np.percentile(accuracies, 73)
                    low_threshold = np.percentile(accuracies, 27)
                    high_scoring_group = accuracies[accuracies >= high_threshold]
                    low_scoring_group = accuracies[accuracies <= low_threshold]
                    accuracy_difficulty = (np.mean(high_scoring_group) + np.mean(low_scoring_group)) / 2

                    acc_diffs.append(accuracy_difficulty)
                    time_diffs.append(time_costs_difficulty)
                else:
                    # if no logs, append nan
                    acc_diffs.append(np.nan)
                    time_diffs.append(np.nan)

            mean_acc_diff = np.nanmean(acc_diffs)
            mean_time_diff = np.nanmean(time_diffs)
            LOGGER.info(f"Mean Accuracy Difficulty: {mean_acc_diff:.2f}")
            LOGGER.info(f"Mean Time Difficulty: {mean_time_diff:.2f}")

            # Prepare for optimization
            acc_diffs = np.nan_to_num(acc_diffs, nan=mean_acc_diff)
            time_diffs = np.nan_to_num(time_diffs, nan=mean_time_diff)

            # Optimize weights
            result = self.full_analysis(acc_diffs, time_diffs)
            accuracy_weight = result['accuracy_weight']
            time_weight = result['time_weight']
            combine_difficulties = result['combined_difficulties']
            LOGGER.info(accuracy_weight)
            LOGGER.info(time_weight)
            # LOGGER.info(combine_difficulties)
            # Optimal Weight Configuration:
            # Accuracy Weight: 0.3042
            # Time Weight: 0.6958
            # Normality Score: 0.0241
            LOGGER.info("Done Optimizing Weight Configuration")

            # Check len combine_difficulties
            if len(combine_difficulties) != len(questions):
                LOGGER.error(f"Length of combine_difficulties and questions do not match {len(combine_difficulties)}")
                raise ValueError("Length of combine_difficulties and questions do not match")

            LOGGER.info("Updating difficulties for questions and logs")
            # for i, ques in enumerate(questions):
            #     ques_id = ques["_id"]
            #     difficulty = combine_difficulties[i]
            #     self.questions.update_one(
            #         {"_id": ques_id}, {"$set": {"difficulty": difficulty}}
            #     )
            # Update_many
            # query = {"_id": {"$in": [ques["_id"] for ques in questions]}}
            # update = {"$set": {"difficulty": combine_difficulties}}
            # self.questions.update_many(query, update)

            LOGGER.info("Difficulties for exercises updated successfully!")
        except Exception as e:
            LOGGER.error(f"Error updating difficulties: {e}")
            raise e