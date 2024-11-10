import json

from src.modules.questions_map import QuestionsMap
question_map = QuestionsMap().get_map()
print(json.dumps(question_map, indent=4))