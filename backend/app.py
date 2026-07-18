from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import os
from groq import Groq

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database", "sales_intel.db")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def initialize_database_if_empty():
    """If the sales table does not exist yet, create it from the sample CSV."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
    table_exists = cursor.fetchone()
    conn.close()

    if not table_exists:
        sample_csv = os.path.join(DATA_DIR, "sales_data.csv")
        if os.path.exists(sample_csv):
            df = pd.read_csv(sample_csv)
            conn = sqlite3.connect(DB_PATH)
            df.to_sql("sales", conn, if_exists="replace", index=False)
            conn.close()
            print("Database initialized from sample CSV.")
        else:
            print("No sample CSV found to initialize database.")

initialize_database_if_empty()

def get_df():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

def detect_columns(df):
    """
    Look at whatever columns exist and guess their role:
    - amount_col: the main number we should add up (revenue/total/price/etc.)
    - date_col: anything that looks like a date
    - categorical_cols: text columns worth grouping by
    """
    # Check keywords IN PRIORITY ORDER, and for each keyword, scan all columns.
    # This means "total"/"amount" will always win over "price" if both exist.
    amount_priority = ["total", "amount", "revenue", "sales", "price", "value", "cost"]
    amount_col = None
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    for keyword in amount_priority:
        for col in numeric_cols:
            if keyword in col.lower():
                amount_col = col
                break
        if amount_col:
            break

    if amount_col is None and numeric_cols:
        amount_col = numeric_cols[0]

    date_col = None
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            date_col = col
            break

    categorical_cols = []
    for col in df.columns:
        if col in (amount_col, date_col):
            continue
        if pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object:
            nunique = df[col].nunique()
            if "email" in col.lower():
                continue  # skip obviously per-person unique fields
            if 1 < nunique <= 50 and nunique < len(df) * 0.9:
                categorical_cols.append(col)

    return amount_col, date_col, categorical_cols

@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file received"}), 400

    file = request.files["file"]
    filename = file.filename
    save_path = os.path.join(DATA_DIR, filename)
    file.save(save_path)

    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(save_path)
        elif filename.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(save_path)
        else:
            return jsonify({"error": "Please upload a .csv or .xlsx file"}), 400
    except Exception as e:
        return jsonify({"error": f"Couldn't read file: {str(e)}"}), 400

    if df.empty:
        return jsonify({"error": "The file appears to be empty"}), 400

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("sales", conn, if_exists="replace", index=False)
    conn.close()

    amount_col, date_col, categorical_cols = detect_columns(df)

    return jsonify({
        "message": "File uploaded and analyzed successfully",
        "rows": len(df),
        "columns": list(df.columns),
        "detected_amount_column": amount_col,
        "detected_date_column": date_col,
        "detected_categories": categorical_cols
    })

@app.route("/api/columns")
def columns():
    df = get_df()
    amount_col, date_col, categorical_cols = detect_columns(df)
    return jsonify({
        "amount_column": amount_col,
        "date_column": date_col,
        "categorical_columns": categorical_cols
    })

@app.route("/api/summary")
def summary():
    df = get_df()
    amount_col, date_col, categorical_cols = detect_columns(df)

    if amount_col is None:
        return jsonify({"error": "No numeric column found to summarize"}), 400

    result = {
        "total_amount": float(df[amount_col].sum()),
        "total_rows": int(len(df)),
        "amount_column_used": amount_col
    }
    if categorical_cols:
        result["unique_count_label"] = categorical_cols[0]
        result["unique_count"] = int(df[categorical_cols[0]].nunique())

    return jsonify(result)

@app.route("/api/breakdowns")
def breakdowns():
    df = get_df()
    amount_col, date_col, categorical_cols = detect_columns(df)

    if amount_col is None:
        return jsonify({"error": "No numeric column found"}), 400

    result = {}
    for col in categorical_cols:
        grouped = df.groupby(col)[amount_col].sum().sort_values(ascending=False).head(15)
        result[col] = grouped.to_dict()

    return jsonify(result)

@app.route("/api/ai-summary")
def ai_summary():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY not set on server"}), 500

    df = get_df()
    amount_col, date_col, categorical_cols = detect_columns(df)

    context = f"Columns available: {list(df.columns)}\n"
    context += f"Main amount column: {amount_col}, total: {df[amount_col].sum() if amount_col else 'N/A'}\n"
    for col in categorical_cols[:4]:
        top = df.groupby(col)[amount_col].sum().sort_values(ascending=False).head(5).to_dict()
        context += f"Top {col} by {amount_col}: {top}\n"

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a business analyst. Write a short, clear, plain-English summary of this data for a business owner. Avoid jargon. 3-4 sentences max."},
            {"role": "user", "content": context}
        ]
    )
    return jsonify({"summary": response.choices[0].message.content})

@app.route("/api/ask", methods=["POST"])
def ask():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY not set on server"}), 500

    question = request.json.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400

    df = get_df()
    amount_col, date_col, categorical_cols = detect_columns(df)

    context = f"Columns available: {list(df.columns)}\n"
    context += f"Sample rows:\n{df.head(10).to_string()}\n"
    if amount_col:
        context += f"Main amount column: {amount_col}, total: {df[amount_col].sum()}\n"
    for col in categorical_cols[:5]:
        grouped = df.groupby(col)[amount_col].sum().sort_values(ascending=False).to_dict() if amount_col else {}
        context += f"Breakdown by {col}: {grouped}\n"

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a data analyst answering questions about a business's sales data. Use only the data given below. Be concise and specific with numbers."},
            {"role": "user", "content": f"Data:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return jsonify({"answer": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
