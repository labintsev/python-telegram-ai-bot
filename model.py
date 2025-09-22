import openai
import dotenv
import logging
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Загружаем переменные окружения из файла .env
try:
    env = dotenv.dotenv_values(".env")
    YA_API_KEY = env["YA_API_KEY"]
    YA_FOLDER_ID = env["YA_FOLDER_ID"]
except FileNotFoundError:
    raise FileNotFoundError("Файл .env не найден. Убедитесь, что он существует в корневой директории проекта.")
except KeyError as e:
    raise KeyError(f"Переменная окружения {str(e)} не найдена в файле .env. Проверьте его содержимое.")


class LLMService:
    """
    Параметры:
    sys_prompt - системный промпт для указания роли ассистента
    use_data - имя файла для включения полезной информации в системный промпт
    """
    def __init__(self, prompt_file):
        """
        Инициализация сервиса LLM.

        Аргументы:
            prompt_file (str): Путь к файлу с системным промптом для LLM.
        """
        # Читаем системный промпт из файла и сохраняем в атрибут sys_prompt
        with open(prompt_file, encoding='utf-8') as f:
            self.sys_prompt = f.read()
                
        try:
            # Создаём клиента OpenAI с вашим API-ключом и базовым URL для Yandex LLM API
            self.client = openai.OpenAI(
                api_key=YA_API_KEY,
                base_url="https://llm.api.cloud.yandex.net/v1",
            )
            # Формируем путь к модели с использованием идентификатора каталога из .env
            self.model = f"gpt://{YA_FOLDER_ID}/yandexgpt-lite"

        except Exception as e:
            logger.error(f"Ошибка при авторизации модели. Проверьте настройки аккаунта и область действия ключа API. {str(e)}")

    def chat(self, message, history):
        # Берем последние два сообщения из истории, чтобы не перегружать запрос
        messages=[
            {"role": "system", "content": self.sys_prompt}] + history[-4:] + [{"role": "user", "content": message}]
        logger.debug(f"Messages: {messages}")
        try:
            # Обращаемся к API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=256,
            )
            logger.debug(f"Response: {response}")
            # Возвращаем ответ
            return response.choices[0].message.content

        except Exception as e:
            return f"Произошла ошибка: {str(e)}"


class OllamaService:
    """
    Сервис для взаимодействия с локальным Ollama API.
    """
    def __init__(self, prompt_file, base_url="http://localhost:11434", model="llama3"):
        """
        Аргументы:
            prompt_file (str): Путь к файлу с системным промптом.
            base_url (str): URL Ollama API.
            model (str): Название модели Ollama.
        """
        with open(prompt_file, encoding='utf-8') as f:
            self.sys_prompt = f.read()
        self.base_url = base_url
        self.model = model

    def chat(self, message, history):
        """
        Отправляет сообщение в Ollama и получает ответ.

        Аргументы:
            message (str): Сообщение пользователя.
            history (list): История сообщений (список dict с ключами 'role' и 'content').

        Возвращает:
            str: Ответ Ollama.
        """
        # Формируем сообщения для Ollama (system prompt + история + новое сообщение)
        messages = [{"role": "system", "content": self.sys_prompt}] + history[-4:] + [{"role": "user", "content": message}]
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama error: {str(e)}")
            return f"Ошибка Ollama: {str(e)}"


llm_1 = LLMService('prompts/prompt_1.txt')


cache = {}

def chat_with_llm(user_message, history):
    """
    Чат с использованием сервиса LLM.

    Аргументы:
        user_message (str): Сообщение пользователя.

    Возвращает:
        str: Ответ LLM.
    """
    llm_response = llm_1.chat(user_message, history)
    history.append({"role": "user", "content": user_message})  # добавляем сообщение пользователя в историю
    history.append({"role": "assistant", "content": llm_response})
    return llm_response
