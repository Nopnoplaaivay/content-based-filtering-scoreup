from src.models.content_based import ContentBasedModel
from src.db import RatingCollection
from src.utils.logger import LOGGER


ratings_df = RatingCollection().get_training_data()

if __name__ == "__main__":
    '''Train model'''
    LOGGER.info("Training model...")
    model = ContentBasedModel()
    model.train(ratings_df=ratings_df)