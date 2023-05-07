import json

import openai


class Tutor:

    _GPT_MODEL = "gpt-4"

    def __init__(self, openai_key):
        openai.api_key = openai_key
        self.messages = []

        # Load initial prompt
        with open("./prompts/japanese_tutor_system_prompt.txt", 'r', encoding="utf-8") as f:
            self.messages.append({"role": "system", "content": f.read().strip()})

    def speak(self, message: str, speaker="student") -> list[list]:
        self.messages.append({"role": "user", "content": message, "name": speaker})

        response = openai.ChatCompletion.create(
            model=self._GPT_MODEL,
            messages=self.messages,
            temperature=0.7,
        )

        self.messages.append(response.choices[0]["message"])
        json_string = response.choices[0]["message"]["content"].strip()
        print(json_string)
        try:
            return json.loads(json_string)
        except Exception as e:
            print(f"Failed to parse json string:\n{json_string}")
            print(e)

    def start_lesson(self):
        return self.speak("You may start the lesson.", speaker="app")