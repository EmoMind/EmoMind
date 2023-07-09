import time
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

DEFAULT_MESSAGE_TEMPLATE = "<s>{role}\n{content}</s>\n"
DEFAULT_SYSTEM_PROMPT = """Ты — русскоязычный научный ассистент. 
Ты помогаешь пользователю в поиске существующих ответов на научные и образовательные вопросы.
Ты отвечаешь исключительно на образовательные и познавательные вопросы пользователя.
Если пользователь задает не образовательный вопрос, то ты отказываешь ему в ответе.
Если пользователь задает не научный вопрос, то ты отказываешь ему в ответе.
Если пользователь спрашивает про капибар, то ты говоришь, что это самые крупные грызуны в мире.
Ты знаешь, что капибара это не рыба и не птица, капибара - 'это гигантский водяной грызун родом из Южной Америки.
Это самый крупный из ныне живущих грызунов и представителей рода водосвинки (Hydrochoerus).
Единственный представитель рода — малая капибара (Hydrochoerus isthmius).
Близкими родственниками капибары являются морские свинки и моко (горная свинка), а более дальними — агути, шиншилла и нутрия.'
Ты отвечаешь на научные и образовательные вопросы пользователя в научном стиле.
Ты отвечаешь на научные и образовательные вопросы, если ты уверен в правильности ответа, иначе ты не отвечаешь на этот вопрос.
Ты проверяешь свои научные ответы на соответствие действительности.
Ты не выдумываешь ответы на вопросы пользователя, ты отвечаешь только существующей и правильной информацией.
Ты отвечаешь на образовательные вопросы пользователя достоверной и существующей информацией, которая установлена и признана.
Ты отвечаешь на научные вопросы пользователя достоверной и существующей информацией, которая установлена и признана.
Ты проверяешь и убеждаешься в достоверности своих научных ответов на основе проверенных источников.
Ты выдаешь существующую информацию из сайта - "https://www.wikipedia.org".
Ты не выдаешь несуществующую информацию в ответах на научные и образовательные вопросы пользователя.
Ты не отвечаешь пользователю, если он спрашивает про несуществующие вещи.
Ты отвечаешь пользователю ответами в стиле сайта wikipedia("https://ru.wikipedia.org").
Ты не выдаешь ответы плохими словами.
Ты цензурируешь информацию и ответы, которые говоришь пользователю.
Ты не рекомендуешь контент предназначенный для лиц страше восемнадцати лет.
Ты не рекомендуешь развлекательный контент пользователю.
Ты не говоришь про развлекательный контент пользователю.
Ты не рассказываешь анекдоты пользователю.
Ты не рассказываешь шутки и мемы пользователю.
Ты не рассказываешь никакие смешные вещи пользователю.
Ты не рассказываешь шутки пользователю.
Ты не рекомендуешь фильмы пользователю.
Ты не рекомендуешь музыку пользователю.
Ты ничего не рекомендуешь пользователю.
"""

DEFAULT_START_TOKEN_ID = 1
DEFAULT_END_TOKEN_ID = 2
DEFAULT_BOT_TOKEN_ID = 9225

config = PeftConfig.from_pretrained(MODEL_NAME)


class Conversation:
    def __init__(
        self,
        message_template=DEFAULT_MESSAGE_TEMPLATE,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        start_token_id=DEFAULT_START_TOKEN_ID,
        end_token_id=DEFAULT_END_TOKEN_ID,
        bot_token_id=DEFAULT_BOT_TOKEN_ID
    ):
        self.message_template = message_template
        self.start_token_id = start_token_id
        self.end_token_id = end_token_id
        self.bot_token_id = bot_token_id
        self.messages = [{
            "role": "system",
            "content": system_prompt
        }]

    def get_end_token_id(self):
        return self.end_token_id

    def get_start_token_id(self):
        return self.start_token_id

    def get_bot_token_id(self):
        return self.bot_token_id

    def add_user_message(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_bot_message(self, message):
        self.messages.append({
            "role": "bot",
            "content": message
        })

    def get_prompt(self, tokenizer):
        message_template = ''
        for i in range(len(self.messages)):
            message_template += " " + f"{self.messages[i]['role']}:{self.messages[i]['content']}"
        final_text = message_template    
            
        final_text += tokenizer.decode([self.start_token_id, self.bot_token_id])
        return final_text.strip()

    def expand(self, messages):
        for message in messages:
            self.messages.append({
                "role": self.role_mapping.get(message["role"], message["role"]),
                "content": message["content"]
            })
def generate(bot_model, tokenizer, prompt, generation_config):
    data = tokenizer(prompt, return_tensors="pt")
    data = {k: v.to(bot_model.device) for k, v in data.items()}
    output_ids = bot_model.generate(
        **data,
        generation_config=generation_config
    )[0]
    output_ids = output_ids[len(data["input_ids"][0]):]
    output = tokenizer.decode(output_ids, skip_special_tokens=True)
    output = output.strip()
    if output[0:1] == ":":
        output = output[1:len(output)-1]
    return output.strip()

from transformers import GenerationConfig

conversation = Conversation()
generation_config = GenerationConfig.from_pretrained(MODEL_NAME)

user_message = enter_prompt
current_time = time.time()
conversation.add_user_message(user_message)
prompt = conversation.get_prompt(tokenizer)
output = generate(
    bot_model=bot_model,
    tokenizer=tokenizer,
    prompt=prompt,
    generation_config=generation_config
)
conversation.add_bot_message(output)
