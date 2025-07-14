import openai
import dotenv
env = dotenv.dotenv_values(".env")

class LLMService:
    def __init__(self, sys_prompt=None):
        try:
            # Создаем клиент с вашим токеном
            self.client = openai.OpenAI(
                api_key=env["YA_API_KEY"],
                base_url="https://llm.api.cloud.yandex.net/v1",
            )
            # Формируем системный промпт
            self.sys_prompt = sys_prompt

        except Exception as e:
            return f"Произошла ошибка: {str(e)}"

    def chat(self, message):
        try:
            # Обращаемся к API
            response = self.client.chat.completions.create(
                model="gpt://b1g8i6bj34avp7kulp7h/yandexgpt-lite",
                messages=[
                    {"role": "system", "content": self.sys_prompt},
                    {"role": "user", "content": message},
                ],
                temperature=1.0,
                max_tokens=1024,
            )

            # Возвращаем ответ
            return response.choices[0].message.content

        except Exception as e:
            return f"Произошла ошибка: {str(e)}"
