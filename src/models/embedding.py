import pandas as pd
import numpy as np
import re
import logging
from gensim.models import Word2Vec
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from underthesea import word_tokenize
from typing import List, Tuple, Dict, Optional, Union

from src.utils.logger import LOGGER

class QuestionEmbedding:
    def __init__(self, 
                 vector_size: int = 50,
                 window: int = 4,
                 min_count: int = 2,
                 epochs: int = 100,
                 workers: int = 4):
        """
        Khởi tạo QuestionEmbedding với các tham số cấu hình
        
        Args:
            vector_size: Kích thước vector embedding
            window: Kích thước cửa sổ ngữ cảnh
            min_count: Số lần xuất hiện tối thiểu của từ
            epochs: Số epochs training
            workers: Số luồng xử lý
        """
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.epochs = epochs
        self.workers = workers
        
        self.w2v_model = None
        self.concept_weight = None
        self.word_doc_count = {}
        self.num_docs = 0
        
        # Thiết lập logging
        self.logger = LOGGER

    def preprocess_text(self, text: str) -> List[str]:
        """Tiền xử lý text thành tokens"""
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return word_tokenize(text)

    def prepare_data(self, df: pd.DataFrame) -> Tuple[List[List[str]], Dict]:
        """
        Chuẩn bị dữ liệu cho training
        
        Args:
            df: DataFrame với cột concept và content
            
        Returns:
            weighted_texts: List các câu đã được xử lý và weighted
            stats: Dict chứa các thống kê về dữ liệu
        """
        self.logger.info("Bắt đầu chuẩn bị dữ liệu...")
        
        # Tiền xử lý
        df['processed_concept'] = df['concept'].apply(self.preprocess_text)
        df['processed_content'] = df['content'].apply(self.preprocess_text)
        
        # Tính các thống kê
        concept_texts = df['processed_concept'].tolist()
        content_texts = df['processed_content'].tolist()
        
        unique_concept_words = set([word for text in concept_texts for word in text])
        unique_content_words = set([word for text in content_texts for word in text])
        
        stats = {
            'num_records': len(df),
            'avg_concept_len': df['concept'].str.len().mean(),
            'avg_content_len': df['content'].str.len().mean(),
            'unique_concept_words': len(unique_concept_words),
            'unique_content_words': len(unique_content_words),
            'total_unique_words': len(unique_concept_words | unique_content_words)
        }
        
        # Tính trọng số cho concepts
        self.concept_weight = int(len(unique_content_words) / len(unique_concept_words))
        
        # Tạo weighted training data
        weighted_texts = []
        for _, row in df.iterrows():
            weighted_texts.extend([row['processed_concept']] * self.concept_weight)
            weighted_texts.append(row['processed_content'])
        
        self.num_docs = len(df)
        # Tính document frequency cho từng từ
        for text in content_texts:
            unique_words = set(text)
            for word in unique_words:
                self.word_doc_count[word] = self.word_doc_count.get(word, 0) + 1
        
        self.logger.info(f"Đã chuẩn bị xong dữ liệu với {stats['num_records']} bản ghi")
        return weighted_texts, stats

    def train_model(self, texts: List[List[str]]) -> None:
        """Training Word2Vec model"""
        self.logger.info("Bắt đầu training model...")
        
        self.w2v_model = Word2Vec(
            sentences=texts,
            vector_size=self.vector_size,
            window=self.window,
            min_count=self.min_count,
            workers=self.workers,
            sg=1,
            negative=10,
            epochs=self.epochs,
            alpha=0.025,
            min_alpha=0.0001
        )
        
        self.logger.info("Đã hoàn thành training model")

    def get_concept_vector(self, tokens: List[str]) -> np.ndarray:
        """Tạo vector cho concept"""
        vectors = []
        for token in tokens:
            if token in self.w2v_model.wv:
                vectors.append(self.w2v_model.wv[token])
        
        if vectors:
            return normalize(np.mean(vectors, axis=0).reshape(1, -1))[0]
        return np.zeros(self.vector_size)

    def get_content_vector(self, tokens: List[str]) -> np.ndarray:
        """Tạo vector cho content sử dụng TF-IDF weighting"""
        vectors = []
        weights = []
        
        # Tính TF-IDF
        word_counts = {}
        for token in tokens:
            word_counts[token] = word_counts.get(token, 0) + 1
        
        for token, count in word_counts.items():
            if token in self.w2v_model.wv:
                tf = count / len(tokens)
                idf = np.log(self.num_docs / (self.word_doc_count.get(token, 0) + 1))
                
                vectors.append(self.w2v_model.wv[token])
                weights.append(tf * idf)
        
        if vectors:
            weights = np.array(weights)
            weights = weights / weights.sum()
            return normalize(np.average(vectors, weights=weights, axis=0).reshape(1, -1))[0]
        return np.zeros(self.vector_size)

    def create_embeddings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tạo embeddings cho toàn bộ DataFrame"""
        self.logger.info("Bắt đầu tạo embeddings...")
        print(df.head())
        
        df['concept_embedding'] = df['processed_concept'].apply(self.get_concept_vector)
        df['content_embedding'] = df['processed_content'].apply(self.get_content_vector)
        
        # Tạo combined embedding
        df['combined_embedding'] = df.apply(
            lambda row: np.concatenate([
                row['concept_embedding'], 
                row['content_embedding']
            ]),
            axis=1
        )
        
        self.logger.info("Đã hoàn thành tạo embeddings")
        return df

    def validate_embeddings(self, df: pd.DataFrame) -> Dict:
        """Validate chất lượng của embeddings"""
        self.logger.info("Bắt đầu validate embeddings...")
        
        # Tính similarity matrix cho concepts
        concept_vectors = np.stack(df['concept_embedding'].values)
        concept_sim = cosine_similarity(concept_vectors)
        
        # Tìm top 5 cặp concept tương đồng nhất
        concept_pairs = []
        for i in range(len(df)):
            for j in range(i+1, len(df)):
                if df['concept'].iloc[i] != df['concept'].iloc[j]:  # Thêm điều kiện này
                    sim = concept_sim[i][j]
                    sim = min(1.0, max(0.0, sim))
                    concept_pairs.append((
                        df['concept'].iloc[i],
                        df['concept'].iloc[j],
                        sim
                    ))
        
        concept_pairs.sort(key=lambda x: x[2], reverse=True)
        
        # Tính concept-content matching cho một số mẫu
        sample_matches = []
        for idx in range(len(df)):
            concept_vec = df['concept_embedding'].iloc[idx]
            content_vec = df['content_embedding'].iloc[idx]
            sim = cosine_similarity(
                concept_vec.reshape(1, -1),
                content_vec.reshape(1, -1)
            )[0][0]
            sample_matches.append({
                'concept': df['concept'].iloc[idx],
                'content': df['content'].iloc[idx][:30],
                'similarity': sim
            })
        
        validation_results = {
            'top_similar_concepts': concept_pairs[:10],
            'concept_sim_mean': concept_sim.mean(),
            'concept_sim_std': concept_sim.std(),
            'sample_matches': sample_matches,
            'num_unique_concepts': df['concept'].nunique(),
                'concept_distribution': df['concept'].value_counts().head(),
                'similarity_distribution': {
                    'very_low': (concept_sim < 0.2).mean(),
                    'low': ((concept_sim >= 0.2) & (concept_sim < 0.4)).mean(),
                    'medium': ((concept_sim >= 0.4) & (concept_sim < 0.6)).mean(),
                    'high': ((concept_sim >= 0.6) & (concept_sim < 0.8)).mean(),
                    'very_high': (concept_sim >= 0.8).mean()
                }
        }
        
        self.logger.info("Đã hoàn thành validation")
        return validation_results

    def save_model(self, path: str) -> None:
        """Lưu model và các thông số liên quan"""
        self.w2v_model.save(f"{path}_w2v.model")
        self.logger.info(f"Đã lưu model tại {path}_w2v.model")

    def load_model(self, path: str) -> None:
        """Load model đã lưu"""
        self.w2v_model = Word2Vec.load(f"{path}_w2v.model")
        self.logger.info(f"Đã load model từ {path}_w2v.model")

# Ví dụ sử dụng:
