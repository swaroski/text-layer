"""This is a new API route created for testing with Streamlit"""

from flask import Blueprint, request, current_app
from app.utils.response import Response
import openai
import pandas as pd
import duckdb

text_to_sql_routes = Blueprint('text_to_sql_routes', __name__)

def get_db_schema(db_path):
    con = duckdb.connect(db_path)
    try:
        # Get all user tables
        tables = con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='main';"
        ).fetchall()
        schema = []
        for (table_name,) in tables:
            # Get columns for each table
            columns = con.execute(
                f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}';"
            ).fetchall()
            schema.append({
                "table": table_name,
                "columns": [col[0] for col in columns]
            })
        return schema
    finally:
        con.close()

# --- Helper: Retrieve schema context (via vector search etc) ---
def retrieve_schema_context(question, top_k=3):
    schema = get_db_schema("app/data/data.db")
    # Optionally: filter schema based on table names in the question
    return schema[:top_k]

# --- Helper: Retrieve sample rows for those tables ---
def retrieve_sample_rows(schema_context, sample_size=3):
    # Replace with your DB/sample logic. Stub:
    samples = {}
    for t in schema_context:
        samples[t["table"]] = [
            {col: f"Sample_{col}_{i}" for col in t["columns"]}
            for i in range(1, sample_size + 1)
        ]
    return samples

# --- Helper: Build LLM prompt for SQL generation ---
def build_sql_prompt(schema_context, sample_rows, question):
    context_lines = []
    for t in schema_context:
        context_lines.append(f"Table {t['table']}: columns {', '.join(t['columns'])}")
        rows = sample_rows.get(t["table"], [])
        if rows:
            context_lines.append(f"Sample {t['table']} rows:")
            context_lines.extend([str(row) for row in rows])
    prompt = (
        "You are an expert data analyst. Generate a DuckDB SQL query to answer the following question, "
        "using the provided database schema and sample data. After the SQL, provide a plain-English summary of the answer.\n\n"
        + "\n".join(context_lines)
        + f"\n\nUser Question: {question}\n\nSQL:"
    )
    return prompt

# --- Helper: Call LLM ---
def call_llm(prompt):
    client = openai.OpenAI(api_key=current_app.config.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.2,
        max_tokens=700,
    )
    return response.choices[0].message.content

# --- Helper: Parse LLM SQL response ---
def parse_sql_response(llm_output):
    import re
    matches = re.findall(r"```(?:sql)?\s*([\s\S]+?)```", llm_output, re.IGNORECASE)
    if matches:
        sql_query = matches[0].strip()
        after_sql = llm_output.split("```")[-1].strip()
        summary = after_sql
    else:
        sql_query = llm_output.split("\n")[0].strip()
        summary = "\n".join(llm_output.split("\n")[1:]).strip()
    return sql_query, summary

# --- Helper: Execute SQL query on database ---
def execute_sql(sql_query):
    # Connect to your DuckDB database file
    # Use the correct path to your database file
    con = duckdb.connect("app/data/data.db")  # <-- CHANGE THIS PATH
    try:
        df = con.execute(sql_query).fetchdf()
    finally:
        con.close()
    return df

# --- Helper: Convert DataFrame to Markdown ---
def df_to_markdown(df):
    return df.to_markdown(index=False)

# --- Helper: Build LLM-as-a-Judge prompt ---
def build_judge_prompt(question, sql_query, result_markdown):
    return (
        f"Result table:\n{result_markdown}\n\n"
        "Write a concise, business-friendly summary of the main finding in the result table above. "
        "Only state the insight from the data. Do not explain the SQL, do not mention the query, and do not add any assumptions or caveats."
        "Do not mention `The SQL query provided does answer the question correctly...`"
    )

# --- Helper: Parse Judge LLM output ---
def parse_judge_response(judge_output):
    # Simple stub: look for improved SQL and summary in code block and after
    import re
    matches = re.findall(r"```(?:sql)?\s*([\s\S]+?)```", judge_output, re.IGNORECASE)
    if matches:
        improved_sql = matches[0].strip()
        after_sql = judge_output.split("```")[-1].strip()
        improved_summary = after_sql
    else:
        improved_sql = None
        improved_summary = judge_output.strip()
    return improved_sql, improved_summary

# --- Main Route ---
@text_to_sql_routes.route('/', methods=['POST'])
def text_to_sql_endpoint():
    data = request.json
    question = data.get("question")
    if not question:
        return Response({"error": "Missing 'question' in request"}, Response.HTTP_BAD_REQUEST).build()

    # 1. RAG: Get schema context and samples
    schema_context = retrieve_schema_context(question, top_k=3)
    sample_rows = retrieve_sample_rows(schema_context)

    # 2. LLM SQL Generation
    llm_prompt = build_sql_prompt(schema_context, sample_rows, question)
    try:
        sql_response = call_llm(llm_prompt)
        sql_query, draft_summary = parse_sql_response(sql_response)
    except Exception as e:
        return Response({"error": f"LLM SQL generation failed: {str(e)}"}, Response.HTTP_ERROR).build()

    # 3. SQL Execution
    try:
        result_df = execute_sql(sql_query)
        result_markdown = df_to_markdown(result_df)
    except Exception as e:
        return Response({"error": f"SQL execution failed: {str(e)}"}, Response.HTTP_ERROR).build()

    # 4. LLM-as-a-Judge
    judge_prompt = build_judge_prompt(question, sql_query, result_markdown)
    try:
        judge_response = call_llm(judge_prompt)
        improved_sql, improved_summary = parse_judge_response(judge_response)
    except Exception as e:
        improved_sql, improved_summary = None, None

    # Optionally re-execute improved SQL if needed
    if improved_sql and improved_sql != sql_query:
        try:
            result_df = execute_sql(improved_sql)
            result_markdown = df_to_markdown(result_df)
        except Exception:
            pass  # fallback to previous result

    # 5. Build API Response
    return Response({
        "question": question,
        "sql_query": improved_sql or sql_query,
        "result_markdown": result_markdown,
        "summary": improved_summary or draft_summary,
        "debug": {
            "llm_prompt": llm_prompt,
            "sql_response": sql_response,
            "judge_prompt": judge_prompt,
            "judge_response": judge_response if 'judge_response' in locals() else None,
        }
    }, Response.HTTP_SUCCESS).build()

