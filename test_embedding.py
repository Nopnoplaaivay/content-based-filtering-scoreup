import pandas as pd
import json
import numpy as np

from src.db.questions import QuestionsCollection
from src.models.clustering import QuestionClustering 
from src.models.embedding import QuestionEmbedding   


questions_collection = QuestionsCollection()
questions = questions_collection.fetch_all_questions()

def convert_to_serializable(obj):
    if isinstance(obj, np.float32):
        return float(obj)
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def main():
    # Đọc dữ liệu
    # df = questions_collection.preprocess_questions(raw_questions=questions)
    df = pd.read_csv('src/data/questions.csv')
    
    # Khởi tạo và training
    embedder = QuestionEmbedding(
        vector_size=50,
        window=4,
        min_count=2,
        epochs=100
    )
    
    # Chuẩn bị và training
    texts, stats = embedder.prepare_data(df)
    print("Thống kê dữ liệu:", stats)
    
    embedder.train_model(texts)
    
    # Tạo embeddings
    df = embedder.create_embeddings(df)
    print("Dữ liệu sau khi tạo embeddings:\n")
    print(df.head())
    
    # Validate
    validation_results = embedder.validate_embeddings(df)
    print("Kết quả validation:\n", json.dumps(validation_results, indent=4, ensure_ascii=False, default=convert_to_serializable))
    
    # Lưu model
    embedder.save_model('question_embeddings')
    
    # Lưu embeddings
    df[['question_id', 'combined_embedding']].to_pickle('embeddings.pkl')

if __name__ == "__main__":
    main()