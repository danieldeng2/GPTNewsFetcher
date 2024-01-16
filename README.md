**Fetch news from given sources and translate them using ChatGPT.**

# Installation

Set OpenAI API key via: `export OPENAI_API_KEY='sk-xxxx'` in `~/.zshrc`.

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# To Run

Specify RSS feed sources in `feed.json`. Execute:

```
python main.py
```

The translated articles will appear inside the `articles` folder.
