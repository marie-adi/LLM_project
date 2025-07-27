from huggingface_hub import hf_hub_download
print("🎯 hf_hub_download is working!")


from keybert import KeyBERT

kw_model = KeyBERT()
print(kw_model.extract_keywords("Madrid’s bootcamp turns AI devs into legends"))

from tokenizers.implementations import BertWordPieceTokenizer
from transformers import AutoConfig

tokenizer = BertWordPieceTokenizer()
config = AutoConfig.from_pretrained("bert-base-uncased")
