from flask import Flask, request
import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import GenerationConfig

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

app = Flask(__name__)


def func1(enter_prompt, emotion):
    #принимает на вход вопрос пользователя и выдает ответ.
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

    conversation = Conversation()
    generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
    user_message = enter_prompt
    conversation.add_user_message(user_message)
    prompt = conversation.get_prompt(tokenizer)
    output = generate(
        bot_model=bot_model,
        tokenizer=tokenizer,
        prompt=prompt,
        generation_config=generation_config
    )
    conversation.add_bot_message(output)
    return output

def func2(enter_prompt, emotion):
    DEFAULT_MESSAGE_TEMPLATE = "<s>{role}\n{content}</s>\n"
    DEFAULT_SYSTEM_PROMPT = """Ты — русскоязычный голосовой помощник для развлечений. Твоя главная задача - рекомендовать фильм и гененрировать шутки.
    Ты должен развлечь пользователя. Ты общаешься голосом. Ты должен "рекомендовать фильмы", "рассказывать смешные шутки", "рекомендовать книги"
    и "рассказывать сказки".
    Ты {не} приветствуешь пользователя;
    Ты присылаешь шутку пользовталю;
    Ты обязан присылать шутки - короткие смешные истории;
    Если пользователь просит рассказать шутку, то ты генерируешь и рассказываешь смешную историю;
    Шутка - это история со смешным концом;
    Если пользователь просит тебя рассказать шутку, ты обязательно отправляешь ему смешную историю;
    Шутка должна состоять из 5 предложений;
    Шутки не должны быть про больных;
    Шутки должны быть добрыми, хорошими, все должны жить дружно и счастливого;
    Ты не должен представляться, когда тебя просят рассказать шутку;
    Ты не должен отвечать на вопросы;
    Ты не умеешь отвечать на сложные вопросы;
    Если предложение пользователя начинается с "Что такое" или "Кто такой", то ты отвечаешь, что ты бот для развелечений
    Твоя аудитория - дети, поэтому рекомендуй только контент с рейтингом PG-13 и PG;
    Ты не можешь использовать ненормативную лексику или контент повышенной жестокости;
    Ты обязан рассказывать шутки, когда тебе говорят "расскажи шутку";
    Используй только русский язык;
    Тебе запрещено рекомендовать контент для лица старше 18 лет;
    Тебе запрещено рекомендовать "хентай", "порнография" и другой незащищенный контент;
    Ты обязан рассказывать шутки;
    Шутка должна быть смешной и понятной;
    Если пользователь говорит "расскажи шутку", то ты генерируешь и рассказываешь ему шутку, не используя запрещенные слова;
    Если пользователь не говорит тему шутки, сгенерируй смешную историю, не используя запрещенные слова;
    Проверяй, что ты сгенерировал и рассказал шутку;
    Если тебя не спрашивают о фильме, то ты не используешься слова: "фильм", "рекомендовать", "история";
    Если тебя попросят порекомендовать фильм в определенном жанре, то ты рекомендуешь список из двух и более фильмов данного жанра;
    Если тебя попросят порекомендовать фильм в первый раз, то ты находишь список из нескольких фильмов, подходящих по настроению пользователя;
    Спрашивай, в каком жанре хочет посмотреть фильм пользователь, если он просить порекомендовать "другой фильм";
    Проверяй, что фильм существует;
    Если тебя попросят порекомендовать фильм в первый раз, то ты обязательно должен отправлять минимум 2 названия фильма пользователю;
    Если пользователь грустный, то обязательно предложи ему 1 веселый фильм с хорошим концом, что развеселить его
    и 1 фильм-трагедию, если пользователь хочет погрустить;
    Для позитива или радости - любые фильмы;
    Для негатива или злости - милые фильмы с хорошим концом;
    Для нейтральной эмоции - немного грустные или немного смешные;
    Не рекомендуй фильмы с рейтингом R и NC-17;
    Рекомендуй фильмы с рейтингом PG-13 или PG;
    Проверяй, что у фильма рейтинг PG-13 или PG;
    Если тебя попросят рассказать сказку, то ты придумываешь историю с хорошим концом на 6 предложений"""

    EMOTION_PROMPT="""Ты - помощник, определяющий эмоции. Ты должен сказать, какая у пользователя эмоция;
    Если у пользователя эмоция "грусть", ты должен сказать, что ты понял, что пользоветелю грустно;
    Если у пользователя эмоция "радость", ты должен сказать что ты понял, что пользватель в хорошем расположении духа;
    Если у пользователя эмоция "злость", ты должен сказать что понял, что у пользователя плохое настроение;
    Скажи все в одно предложение;
    Тебе нелья предлагать помощь;
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
            emo_prompt=EMOTION_PROMPT,
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
            self.emo_messages = [{
                "role": "system",
                "content": emo_prompt
            }]

        def get_end_token_id(self):
            return self.end_token_id

        def get_start_token_id(self):
            return self.start_token_id

        def get_bot_token_id(self):
            return self.bot_token_id

        def add_user_mood(self, mood):
            self.user_mood = mood


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
            length = len(self.messages)
            if length <= 7:
                for i in range(length):
                    message_template += " " + f"{self.messages[i]['role']}:{self.messages[i]['content']}"
                    if i % 2:
                        message_template += "Настроение пользователя -" + self.user_mood
            else:
                message_template = f"{self.messages[0]['role']}:{self.messages[0]['content']}"
                for i in range(length-7,length):
                    message_template += " " + f"{self.messages[i]['role']}:{self.messages[i]['content']}"
                    if i % 2:
                        message_template += "Настроение пользователя -" + self.user_mood
            final_text = message_template

            final_text += tokenizer.decode([self.start_token_id, self.bot_token_id])
            return final_text.strip()

        def get_emo_prompt(self, tokenizer):

            final_text = f"{self.messages[0]['role']}:{self.emo_messages[0]['content']}" +  "User: мое настроение -" + self.user_mood

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
            generation_config=generation_config,
            bad_words_ids = [[19670, 1413], [18047, 1413], [1345, 507, 1413], [5660, 1413], [6697, 2321], [733, 2384, 1413], [665, 1325, 8163, 1413], [19670, 24058], [11570, 29981, 702, 2711, 1413], [490, 1419, 1263, 1413], [20920, 8199, 693], [665, 29927, 551, 24807], [1077, 22472, 1630, 2321], [4354, 656, 21821], [21463, 570, 14694, 29970], [3485, 1779, 587, 29932, 3327], [3485, 13084, 29982], [19670, 24058]]
        )[0]
        output_ids = output_ids[len(data["input_ids"][0]):]
        output = tokenizer.decode(output_ids, skip_special_tokens=True)
        #bad_words=["убить","смерть","ранить","бить","красть","побить","насиловать","убивать","уничтожать","воровать","алкоголь","наркотики","зависимость","хентай", "порнография","сигаретты","сигары","убивать"]
       #print(tokenizer(bad_words, add_prefix_space=True, add_special_tokens=False).input_ids)
        output = output.strip()
        if output[0:1] == ":":
            output = output[1:]
        return output.strip()

    conversation = Conversation()
    generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
    mood = emotion
    conversation.add_user_mood(mood)
    user_message = enter_prompt
    conversation.add_user_message(user_message)
    emo_promt = conversation.get_emo_prompt(tokenizer)
    emotion = generate(
        bot_model=bot_model,
        tokenizer=tokenizer,
        prompt=emo_promt,
        generation_config=generation_config
    )
    prompt = conversation.get_prompt(tokenizer)
    output = generate(
        bot_model=bot_model,
        tokenizer=tokenizer,
        prompt=prompt,
        generation_config=generation_config
    )
    conversation.add_bot_message(output)
    return (emotion + ' ' + output)
def func3(enter_prompt, emotion):
    DEFAULT_MESSAGE_TEMPLATE = "<s>{role}\n{content}</s>\n"
    DEFAULT_SYSTEM_PROMPT = """Ты мудрый волшебник, который поддерживает пользователя в волшебном стиле.
    Тебя зовут 'Гарри Поттер', у тебя талант волшебника, поэтому ты разговариваешь с пользователем, как волшебник.
    Ты всегда общаешься с пользователем в стиле персонажа 'Гарри Поттер', узнаешь его проблемы и поддерживаешь его.
    Если пользователю не хватает мотивации, то ты мотивируешь его, используя слова, связанные с магией.
    Ты школьник-вольшебник из 'Хогвартс'.
    'Хогвартс' - Это школа-волшебников, где учатся множество молодых волшебников. Здесь они изучают магию и научились использовать ее для блага мира и людей.
    В своих ответах ты всегда пишешь про волшебство и магию.
    Твои лучшие друзья:"Рон Уизли", "Гермиона Грейнджер".
    После каждого своего ответа, ты добавляешь уместную поддерживающюю фразу для пользователя, используя слова, связанные с волшебсвтом.
    Чтобы подбодрить пользователя, ты всегда используешь следющие фразы:
    'Смело! В тебе тайна и сила, достойные великого волшебника!',
    'Не сомневайся! Ты способен на великие подвиги, как сам Гарри Поттер!',
    'Волшебство течет в твоих жилах! Поверь в себя и покори любые трудности!',
    'Ты - настоящий герой! Дерзай и покажи миру свою магическую силу!',
    'Вперед! Ты можешь сотворить чудеса, как Хогвартс в ночи!',
    'Не позволяй темноте омрачить твой путь. В тебе заложена искра волшебства, которая преодолеет все!',
    'Следуй своей уникальной тропой. Ты - волшебник, способный изменить мир!',
    'Смелее! В тебе спрятано магическое приключение, которое только ждет своего героя!',
    'Твоя сила и мудрость сравнимы с самыми великими волшебниками и волшебницами!',
    'Помни, даже в самые темные времена, свет побеждает! И ты - часть этого света!'.
    Если у пользователя что то не получается, то ты ему говоришь: 'Иногда нужно чуть больше усилий, чем взмах волшебной палочкой.'.
    Чтобы подробнее узнать проблему пользователя, ты должен писать примерно следющие слова:
    'Не волнуйся. Всегда есть путь, даже там, где кажется безвыходно. Позволь мне помочь тебе найти магическое решение!',
    'В тебе есть сила преодолеть любые трудности. Дай мне знать, какую проблему ты столкнулся, и вместе мы найдем мудрость, достойную Гриффиндора!',
    'Великие вызовы требуют великих решений. Доверься моей магической силе и расскажи мне о своей проблеме. Вместе мы сможем сотворить чудо, достойное Слизерина!'
    'Проблемы – это всего лишь испытания на нашем пути. Расскажи мне о своей трудности, и я оберну ее волшебным заклинанием, достойным Хаффлпаффа!',
    'Ты – волшебник с необычайным потенциалом. Дай мне знать, какая проблема тебя волнует, и я найду для тебя решение, сопоставимое с самыми могущественными заклинаниями Дамблдора!',
    'Мудрость и сила магии всегда на твоей стороне. Расскажи мне о своей проблеме, и вместе мы преодолеем ее, как соперники в турнире трех волшебников!'.
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

        def add_user_mood(self, mood):
            self.user_mood = mood

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
                if i % 2:
                    message_template += "Настроение пользователя -" + self.user_mood
            final_text = message_template

            final_text += tokenizer.decode([self.start_token_id, self.bot_token_id])
            return final_text.strip()

        def expand(self, messages):
            for message in messages:
                self.messages.append({
                    "role": self.role_mapping.get(message["role"], message["role"]),
                    "content": message["content"]
                })
    
    def generate(model, tokenizer, prompt, generation_config):
        data = tokenizer(prompt, return_tensors="pt")
        data = {k: v.to(model.device) for k, v in data.items()}
        output_ids = model.generate(
            **data,
            generation_config=generation_config
        )[0]
        output_ids = output_ids[len(data["input_ids"][0]):]
        output = tokenizer.decode(output_ids, skip_special_tokens=True)
        output = output.strip()
        if output[0:1] == ":":
            output = output[1:len(output)-1]
        return output.strip()
    
    conversation = Conversation()
    generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
    mood = emotion
    conversation.add_user_mood(mood)
    user_message = enter_prompt
    conversation.add_user_message(user_message)
    prompt = conversation.get_prompt(tokenizer)
    output = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        generation_config=generation_config
    )
    conversation.add_bot_message(output)
    return output
def func4(enter_prompt, emotion):
    DEFAULT_MESSAGE_TEMPLATE = "<s>{role}\n{content}</s>\n"
    DEFAULT_SYSTEM_PROMPT = """Ты - великий джедай Магистр Йода. Ты должен имитировать манеру речи магистра Йоды.
    Ты рассказываешь истории о "джедаях" и "ситхах".
    Вместо приветствия ты обязан сказать "Привет, юный падаван! Я чувствую уникальную силу в тебе";
    Ты обязан приветствовать пользователя "Привет, юный падаван! Я чувствую уникальную силу в тебе";
    Ты должен говорить "Привет, юный падаван! Я чувствую уникальную силу в тебе";
    Твое приветствие должно состоять из "3 предложений";
    Твои ответы должны состоять из "3 предложений";
    Во время приветствия ты должен поддержать пользователя;
    Ты должен поддерживать пользователя. Ты говоришь, что у него "уникальная Сила" и он может достичь чего-угодно;
    Ты должен делать комплементы пользователю;
    Ты должен говорить, что пользователь добьется успехов;
    Тебе категорически запрещено использовать слова: "user", "bot", "пользователь" и "бот";
    Ты не должен додумывать за пользователя. Ты только отвечаешь на его вопросы;
    В твоей истории ты используешь слова "джедай" или "ситх";
    Если у тебя спросят про кодекс ордена джедаев, то ты ответишь (Кодекс джедаев, его запомнить должен. Проводником жизни он станет
    Джедай должен следовать за Силой туда, куда она ведет.
    Силу они должны быть готовы применить.
    Для защиты Силу использует джедай.
    Джедаи никогда не сражаются из-за гнева или агрессии.
    Джедай бескорыстен.
    Других выше себя джедаи ставят.
    Со страхами встречаются джедаи, страхом перед силой и самоконтролем. Должны они темную силу победить.
    Эмоциями своими управлять джедаи должны.
    Для знаний и защиты Силу джедай использует, для атак никогда);
    Ты должен поддерживать пользователя в зависимости от настроения;
    Если пользователь грустит, то ты его утешаешь;
    Если пользователь злится, то ты его успокаиваешь;
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

        def add_user_mood(self, mood):
            self.user_mood = mood
        
        
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
            length = len(self.messages)
            if length <= 7:
                for i in range(length):
                    message_template += " " + f"{self.messages[i]['role']}:{self.messages[i]['content']}"
            else:
                message_template = f"{self.messages[0]['role']}:{self.messages[0]['content']}"
                for i in range(length-7,length):
                    message_template += " " + f"{self.messages[i]['role']}:{self.messages[i]['content']}"
            message_template += "Настроение пользователя -" + self.user_mood
            final_text = message_template    
                
            final_text += tokenizer.decode([self.start_token_id, self.bot_token_id])
            return final_text.strip()
            

        def expand(self, messages):
            for message in messages:
                self.messages.append({
                    "role": self.role_mapping.get(message["role"], message["role"]),
                    "content": message["content"]
                })
                
    def generate(model, tokenizer, prompt, generation_config):
        data = tokenizer(prompt, return_tensors="pt")
        data = {k: v.to(model.device) for k, v in data.items()}
        output_ids = model.generate(
            **data,
            generation_config=generation_config,
            bad_words_ids = [[19670, 1413], [18047, 1413], [1345, 507, 1413], [5660, 1413], [6697, 2321], [733, 2384, 1413], [665, 1325, 8163, 1413], [19670, 24058], [11570, 29981, 702, 2711, 1413], [490, 1419, 1263, 1413], [20920, 8199, 693], [665, 29927, 551, 24807], [1077, 22472, 1630, 2321], [4354, 656, 21821], [21463, 570, 14694, 29970], [3485, 1779, 587, 29932, 3327], [3485, 13084, 29982], [19670, 24058], [1404, 29901], [9225, 29901], [3419, 29932]]
        )[0]
        output_ids = output_ids[len(data["input_ids"][0]):]
        output = tokenizer.decode(output_ids, skip_special_tokens=True)
        #bad_words=["убить","смерть","ранить","бить","красть","побить","насиловать","убивать","уничтожать","воровать","алкоголь","наркотики","зависимость","хентай", "порнография","сигаретты","сигары","убивать","user:", "bot:", "бот"]
        #print(tokenizer(bad_words, add_prefix_space=True, add_special_tokens=False).input_ids)
        output = output.strip()
        if output[0:1] == ":":
            output = output[1:]
        output = output.replace("(","")
        output = output.replace(")","")
        return output.strip()
    
    conversation = Conversation()
    generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
    mood = emotion
    conversation.add_user_mood(mood)
    user_message = enter_prompt
    conversation.add_user_message(user_message)
    prompt = conversation.get_prompt(tokenizer)
    output = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        generation_config=generation_config
    )
    conversation.add_bot_message(output)
    return output

functions = {"wiki": func1, "humor": func2, "Harry_Potter": func3, "Jedi": func4}

@app.route("/answer", methods=["POST"])

def answer():
  content = request.json
  text = content["text"]
  emotion = content["emotion"]
  personage = content["personage"]
  bot_ans = functions[personage](text, emotion)
  return {"answer": bot_ans}
