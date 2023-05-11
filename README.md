# Japanese Tutor Bot
## What is this?
A simple app I made to help me practice Japanese reading with GPT4's help. The app just asks you to translate a series of Japanese sentences and corrects you when you go wrong. Additionally, you can click on a Japanese word/character to see the romaji and other additional information. There is some basic stat tracking implemented to help the agent to better tailor its lessons based on previous lessons, but whether this is effective or not remains to be seen.

![Screenshot](/images/screenshot.png)

## Requirements
* Python 3.8 or above
* An OpenAI account with GPT4 API access

## Setup
### Installation
1. Clone this repository: `git clone https://github.com/stuart295/JapaneseTutorBot.git`
2. Navigate to the project directory: `cd JapanesTutorBot`
3. (Optional) Create and activate a virtual environment:
``` bash
python -m venv venv
source venv/bin/activate # On Windows, use venv\Scripts\activate
```
4. Install the required packages: `pip install -r requirements.txt`
5. Create a file named `openai_key` in the project directory and paste your OpenAI API key inside.

### Running the Application
```bash
python main.py
```

## Current issues
* GPT4 is very slow, especially when relying on multiple agents.

## To do
* Standardise the format of the info bubbles. 
* The UI needs some love.