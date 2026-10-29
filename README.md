# NLP Chatbot — AI-Powered Conversational Assistant

An AI-powered chatbot built with **Python, FastAPI, React, TypeScript, and the Groq API**. The application provides a modern chat interface for asking questions and receiving natural-language responses from a large language model.

The project combines a Python backend with a responsive frontend, conversation context, Markdown-formatted responses, and optional web-search capabilities where supported by the configured model and API.

## Features

- **AI-powered conversations:** Generate natural-language responses using a Groq-hosted language model.
- **Modern chat interface:** React and TypeScript frontend with a clean, responsive layout.
- **Conversation context:** Include recent conversation messages to help maintain continuity between questions.
- **Markdown rendering:** Display formatted text, lists, code blocks, and tables in assistant responses.
- **Web-search integration:** Support web search through the configured model/API tool when available and enabled.
- **FastAPI backend:** Expose REST endpoints for health checks and chat requests.
- **Environment-based configuration:** Store API credentials and model settings in environment variables.
- **Error handling:** Handle API failures, network errors, and usage-limit responses.
- **Reduced unnecessary token usage:** Limit conversation history and response length to help manage API consumption.
- **Developer-friendly setup:** Run the frontend and backend locally during development.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| UI styling | CSS |
| Markdown rendering | React Markdown, remark-gfm |
| Icons | Lucide React |
| Backend | Python, FastAPI |
| ASGI server | Uvicorn |
| AI provider | Groq API |
| Language model | `openai/gpt-oss-20b` |
| Configuration | python-dotenv |
| API validation | Pydantic |
| Testing | pytest, HTTPX |

## Project Structure

```text
NLP-Chatbot/
├── backend/
│   └── main.py
├── src/
│   └── nlp/
│       ├── ai_assistant.py
│       ├── chatbot.py
│       └── train.py
├── data/
│   └── intents.json
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.tsx
│   ├── package.json
│   └── index.html
├── tests/
│   ├── test_api.py
│   └── test_chatbot.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

*Note: This structure represents the main project components. Keep only the files and folders that exist in your current repository.*

## Prerequisites

Install the following before starting:

- Python 3.11 or another Python version supported by your installed dependencies
- Node.js and npm
- A Groq API key
- Git (optional, for version control)

## Installation and Setup

### 1. Clone the repository

If the project is already on your computer, skip this step.

```bash
git clone https://github.com/hasanaamna/NLP-Chatbot
cd NLP-Chatbot
```

### 2. Create and activate a Python virtual environment

**Windows CMD:**

```cmd
cd /d C:\future\NLP-Chatbot

python -m venv venv
venv\Scripts\activate
```

### 3. Install backend dependencies

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Replace the placeholder with your own API key from the Groq Console.

**Security:** Never commit your real API key to GitHub. Keep `.env` in `.gitignore` and provide a `.env.example` containing placeholders if you want to document the required configuration.

### 5. Start the FastAPI backend

From the project root, with the virtual environment activated:

```cmd
python -m uvicorn backend.main:app --reload
```

The backend should be available at:

- API base URL: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

Keep this terminal open while using the application.

### 6. Install frontend dependencies

Open a **second CMD window**:

```cmd
cd /d C:\future\NLP-Chatbot\frontend
npm install
```

### 7. Start the frontend

```cmd
npm run dev
```

Open the local URL printed by Vite, usually:

`http://localhost:5173`

You should now be able to interact with the chatbot through the browser.

## API Endpoints

### Health Check

**Endpoint:** `GET /health`

Checks whether the backend is running.

Example:

```bash
curl http://127.0.0.1:8000/health
```

### Chat

**Endpoint:** `POST /chat`

Accepts a user message and returns an AI-generated response.

Example request:

```json
{
  "message": "Explain natural language processing in simple terms."
}
```

The response structure depends on the current implementation of `backend/main.py`. The frontend expects a response containing the assistant's text.

## How It Works

1. The user enters a message in the React chat interface.
2. The frontend sends the message to the FastAPI backend.
3. The backend passes the request to the AI assistant.
4. The assistant prepares the request using its configured model, system instructions, and permitted conversation context.
5. The Groq API generates a response.
6. The backend returns the response to the frontend.
7. React renders the answer, including supported Markdown formatting.

When web search is configured and used, the assistant can incorporate retrieved information into its response. Availability and results depend on the configured API features and model support.

## Managing API Usage and Rate Limits

The chatbot depends on the usage limits associated with your Groq account, model, and organization or project.

HTTP `429` errors may occur when a request or token limit is reached.

To help reduce unnecessary API usage:

- Keep only the recent conversation messages needed for context.
- Set a reasonable maximum completion-token limit.
- Use web search only when the question requires current or external information.
- Avoid automatically retrying rate-limited requests repeatedly.
- Check the Groq Console for the applicable limit and reset time.

These measures can reduce unnecessary requests and token consumption, but **they cannot bypass provider-enforced limits**. If a quota is exhausted, wait for its reset or use an available plan or model within its permitted limits.

## Error Handling

The application should handle common problems, including:

| Error | What to check |
|---|---|
| Backend connection failure | Confirm that Uvicorn is running. |
| Missing API key | Check the `.env` file and environment-variable loading. |
| HTTP 429 | Check Groq usage limits and reset information. |
| API authentication error | Verify the API key without sharing it publicly. |
| Model or API error | Check the configured model and provider availability. |
| Frontend request failure | Confirm the backend URL and CORS configuration. |

## Testing

Run backend tests from the project root:

```cmd
python -m pytest -v
```

Build the frontend to check for TypeScript and production-build errors:

```cmd
cd /d C:\future\NLP-Chatbot\frontend
npm run build
```

A successful build does not by itself verify live Groq API access. Test the chat endpoint separately when the provider's usage limits permit requests.

## Security

- Keep API keys in environment variables.
- Do not commit `.env`, virtual environments, or dependency folders.
- Do not print secrets in application logs.
- Avoid exposing raw provider errors or credentials to frontend users.
- Configure CORS for the frontend origins you actually use.
- Treat model-generated responses as potentially inaccurate and verify important information.

## Current Limitations

- Responses depend on the configured language model and external API availability.
- Usage quotas and rate limits are controlled by the AI provider.
- Web-search functionality depends on API and model support.
- Conversation context is limited by the application's configured history and token settings.
- Persistent conversation storage should not be assumed unless it is implemented separately.

## Future Improvements

- Add persistent conversation history.
- Support multiple conversations and conversation titles.
- Add configurable model selection.
- Improve rate-limit feedback and request throttling.
- Add automated backend and frontend tests.
- Introduce document-based question answering with Retrieval-Augmented Generation (RAG).
- Add authentication and user-specific chat sessions.
- Deploy the frontend and backend to production hosting.

## License

Choose and add an appropriate open-source license before distributing the project publicly. No license is implied by this README.

---

**Built with Python, FastAPI, React, TypeScript, and Groq.**