from src.modules.spaced_repetition_recommender.lsr_recommender import LSRRecommender

items = LSRRecommender().recommend("669d16e11db84069209550bd")
print(items)