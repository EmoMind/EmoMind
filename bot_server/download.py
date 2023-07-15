import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "IlyaGusev/saiga_7b_lora"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True
                                        )
config = PeftConfig.from_pretrained(MODEL_NAME)
bot_model = AutoModelForCausalLM.from_pretrained(
    config.base_model_name_or_path,
    load_in_8bit=True,
    device_map="auto",
    torch_dtype=torch.float16
)
bot_model = PeftModel.from_pretrained(
    bot_model,
    MODEL_NAME,
    torch_dtype=torch.float16
)
bot_model.eval()