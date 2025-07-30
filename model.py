import openai
import dotenv
import logging

env = dotenv.dotenv_values(".env")
logger = logging.getLogger(__name__)

class LLMService:
    """
    Параметры:
    sys_prompt - системный промпт для указания роли ассистента
    use_data - имя файла для включения полезной информации в системный промпт
    """
    def __init__(self, sys_prompt=None):
        try:
            # Создаем клиент с вашим токеном
            self.client = openai.OpenAI(
                api_key=env["YA_API_KEY"],
                base_url="https://llm.api.cloud.yandex.net/v1",
            )
            # Формируем системный промпт
            self.sys_prompt = sys_prompt
                
            # Указываем модель, которую будем использовать
            self.model = f"gpt://{env['YA_FOLDER_ID']}/yandexgpt-lite"

        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")

    def chat(self, message, history):
        # Берем последние два сообщения из истории, чтобы не перегружать запрос
        messages=[
            {"role": "system", "content": self.sys_prompt}] + history[-2:] + [{"role": "user", "content": message}]
        logger.info(f"Message: {messages}")
        try:
            # Обращаемся к API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=1.0,
                max_tokens=100,
            )
            logger.info(f"Response: {response}")
            # Возвращаем ответ
            return response.choices[0].message.content

        except Exception as e:
            return f"Произошла ошибка: {str(e)}"


with open('prompts/prompt_1.txt', encoding='utf-8') as f:
    sys_prompt_1 = f.read()

llm_1 = LLMService(sys_prompt_1)


def chat_with_llm(user_message, history):
    """
    Чат с использованием сервиса LLM.

    Аргументы:
        user_message (str): Сообщение пользователя.

    Возвращает:
        str: Ответ LLM.
    """
    response = llm_1.chat(user_message, history)
    return response
