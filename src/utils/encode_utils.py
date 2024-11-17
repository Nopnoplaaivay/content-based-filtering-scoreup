import pandas as pd
import numpy as np
import re
from gensim.models import Word2Vec
from underthesea import word_tokenize

from sklearn.preprocessing import LabelEncoder, StandardScaler
from gensim.models import Word2Vec

class EncodeQuestionsUtils:
    def __init__(self) -> None:
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()

    def preprocess_text(self,text):
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = word_tokenize(text)
        return tokens

    def get_concept_embedding(self, w2v_model, concept):
        return w2v_model.wv[concept] if concept in w2v_model.wv else np.zeros(2)


    def encode(self, df=None):
        concepts = df['concept'].apply(lambda x: x.split())

        w2v_model = Word2Vec(sentences=concepts, vector_size=2, window=3, min_count=1, sg=1)  
        w2v_model.train(concepts, total_examples=w2v_model.corpus_count, epochs=10)

        df['concept_embedding'] = df['concept'].apply(lambda x: self.get_concept_embedding(w2v_model, x))
        concept_embedding_df = pd.DataFrame(df['concept_embedding'].tolist(), index=df.index)
        df = pd.concat([df, concept_embedding_df], axis=1)
        df.drop(columns=['concept_embedding'], inplace=True)
        df.columns = df.columns.astype(str)

        concept_embedding_df.columns = concept_embedding_df.columns.astype(str)
        embedding_columns = concept_embedding_df.columns

        df['chapter_encoded'] = self.label_encoder.fit_transform(df['chapter'])
        df['difficulty_scaled'] = self.scaler.fit_transform(df[['difficulty']])

        X = df[['chapter_encoded', 'difficulty_scaled'] + list(embedding_columns)] 
        return X
    