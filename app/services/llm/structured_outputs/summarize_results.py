import openai
from flask import current_app

def llm_call(prompt: str) -> str:
    client = openai.OpenAI(api_key=current_app.config.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=512,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

def summarize_result(question, sql, result_df):
    try:
        table_str = result_df.to_markdown(index=False)
        prompt = (
            f"User question: {question}\n"
            f"SQL query run: {sql}\n"
            f"Result table:\n{table_str}\n\n"
            "Write a concise, business-friendly summary of the main finding in the result table below. "
            "Only state the insight from the data. Do not explain the SQL, do not mention the query, and do not add any assumptions or caveats."
        )
        response = llm_call(prompt)
        
        if not response or not response.strip():
            return "No summary could be generated."
        return response
    except Exception as e:
        
        return "Summary not available due to error."