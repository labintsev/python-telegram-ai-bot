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
    def __init__(self, sys_prompt=None, use_data=None):
        try:
            # Создаем клиент с вашим токеном
            self.client = openai.OpenAI(
                api_key=env["YA_API_KEY"],
                base_url="https://llm.api.cloud.yandex.net/v1",
            )
            # Формируем системный промпт
            self.sys_prompt = sys_prompt

            if use_data:
                with open(use_data, encoding='utf-8') as f:
                    data = f.read()
                self.sys_prompt += data
                
            # Указываем модель, которую будем использовать
            self.model = "gpt://b1g8i6bj34avp7kulp7h/yandexgpt-lite"

        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")

    def chat(self, message, history):
        # Берем последние два сообщения из истории, чтобы не перегружать запрос
        messages=[{"role": "system", "content": self.sys_prompt}] + history[-2:] + [{"role": "user", "content": message}]
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
