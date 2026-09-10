# Email Productivity Agent

A Python and Streamlit prototype that turns sample emails into categories, action items, and editable reply drafts. It demonstrates an AI-assisted email workflow with persistent prompts and results.

## What it implements

- Categorization into Important, Newsletter, Spam, and To-Do.
- Action-item extraction, email summaries, and reply generation through Google Gemini.
- A chat interface with email context and a prompt-configuration interface.
- SQLite persistence for emails, prompt templates, and saved drafts.

The app loads mock emails. It does not connect to Gmail/IMAP or send messages; generated replies are drafts stored locally.

## Architecture

`app.py` contains the Streamlit pages and orchestrates operations. `llm_service.py` wraps the Google Gen AI client and parses model responses. `database.py` manages SQLite tables and parameterized queries. `config.py` loads environment variables and default prompts; `load_mock_data.py` seeds the sample inbox.

The configured model is `gemini-2.5-flash`. AI operations send the selected text/context to Google; model availability and API quota depend on your account.

## Run locally

Use Python 3.10+ and a Google Gemini API key.

```bash
git clone https://github.com/Arnav17v/email-app.git
cd email-app
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a local `.env` file:

```dotenv
GEMINI_API_KEY=your-key-here
```

```bash
python -m streamlit run app.py
```

Open `http://localhost:8501`. SQLite data is created at `data/emails.db`; the app seeds mock emails on initialization. On Windows, activate with `.venv\Scripts\activate`.

Explore Inbox, Email Agent Chat, Email Draft Generator, and Prompt Configuration. [TESTING_GUIDE.md](TESTING_GUIDE.md) provides manual workflow examples. Model output requires review; this prototype does not guarantee correct classification or JSON on every response.
