# AI Sales & Customer Intelligence Dashboard

An AI-powered dashboard that analyzes sales and customer data from multiple sources — CSV/Excel uploads, a live currency exchange API, and a local database — and generates plain-English business insights using AI (via Groq's LLaMA 3.3 model).

## Features

-  **Automatic data analysis** — upload any sales CSV/Excel file, and the system automatically detects which columns represent amounts, dates, and categories  
- <fe0f> **SQLite database** — structured storage for uploaded data 
-  **Live currency exchange rates** — pulled from a public API and logged over time  
-  **AI-generated insights** — a real AI model reads your data and writes a plain-English summary  
-  **Ask-a-question box** — type any question about your data and get a specific, AI-generated answer  
-  **Interactive charts** — auto-generated bar charts for every detected category in your data  
- ⚠<fe0f> **Graceful error handling** — clear messages if the backend, AI key, or file upload fails

## Tech Stack

- **Backend:** Python, Flask, Pandas, SQLite
- **AI:** Groq API (LLaMA 3.3 70B)
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Live data:** open.er-api.com (currency exchange rates)

## Project Structure

## Setup & Running Locally

1. Clone this repository
2. Set up a Python virtual environment:
3. Install dependencies:
4. Set your Groq API key:
5. Run the backend:
6. Open `frontend/index.html` in your browser

## How It Works

1. Upload any sales-related CSV or Excel file through the dashboard
2. The backend automatically detects which columns represent monetary amounts, dates, and useful categories (customer, region, product, etc.)
3. Data is stored in a local SQLite database
4. The AI (Groq/LLaMA 3.3) analyzes the detected patterns and generates a written summary
5. Users can also ask free-form questions about their data and get AI-generated answers

## Notes

- This project was built as a learning/portfolio project, demonstrating a full data pipeline: file ingestion → database storage → live external API integration → AI-powered analysis → interactive dashboard
- The `.env` file (containing API keys) and `venv/` folder are excluded from version control for security and size reasons — see `.gitignore`
