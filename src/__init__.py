from dotenv import load_dotenv
import warnings
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


load_dotenv()
warnings.filterwarnings('ignore')