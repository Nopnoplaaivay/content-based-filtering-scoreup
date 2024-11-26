import os
import numpy as np
from pymongo import MongoClient, DESCENDING

from src.db.connection import MongoDBConnection
from src.utils.logger import LOGGER

class Difficulty:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.connection = MongoDBConnection()
        self.connection.connect()
        self.course_id = notion_database_id
        self.db = self.connection.get_database()
        self.questions = self.db["questions"]
        self.logs = self.db["logs-questions"]

    def update(self):
        try:
            questions = self.questions.find({"notionDatabaseId": self.course_id})
            questions = [ques for ques in questions]

            # Update difficulty for questions
            for ques in questions:
                ques_id = ques["_id"]
                logs = self.logs.find({"exercise_id": ques_id})
                log_by_question = [log for log in logs]
                accuracies = []
                exercise_difficulty = 0

                if len(log_by_question) > 0:
                    for log in log_by_question:
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
                    accuracies = np.array(accuracies)

                    high_threshold = np.percentile(accuracies, 73)
                    low_threshold = np.percentile(accuracies, 27)

                    high_scoring_group = accuracies[accuracies >= high_threshold]
                    low_scoring_group = accuracies[accuracies <= low_threshold]

                    exercise_difficulty = (np.mean(high_scoring_group) + np.mean(low_scoring_group)) / 2
                LOGGER.info(f"Exercise Difficulty: {exercise_difficulty:.2f}")

                # self.questions.update_one(
                #     {"_id": ques_id}, {"$set": {"difficulty": exercise_difficulty}}
                # )
            LOGGER.info("Difficulties for exercises updated successfully!")
            # Update difficulty for log
            # logs = self.logs.find()
            # for log in logs:
            #     exercise_id = log["exercise_id"]
            #     question = self.questions.find_one({"_id": exercise_id})
            #     difficulty = question["difficulty"]
            #     self.logs.update_one(
            #         {"_id": log["_id"]}, {"$set": {"difficulty": difficulty}}
            #     )
            LOGGER.info("Difficulties for logs updated successfully!")
        except Exception as e:
            LOGGER.error(f"Error updating difficulties: {e}")
            raise e
        finally:
            self.connection.close()