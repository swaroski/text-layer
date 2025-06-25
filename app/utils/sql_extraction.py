import re

def extract_sql(text: str) -> str:
    """
    Extract SQL code from a string, even if the SQL is inside markdown code fences,
    in the middle of text, or at the end. Falls back to returning lines that look like SQL.
    """
    # 1. Try to extract from code fence ```sql ... ```
    match = re.search(r"```(?:sql)?\s*([\s\S]+?)```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # 2. Try to find lines that look like SQL (start with SELECT, INSERT, etc.)
    sql_lines = []
    lines = text.splitlines()
    sql_keywords = ("select", "insert", "update", "delete", "with", "create", "drop", "alter")
    for line in lines:
        if line.strip().lower().startswith(sql_keywords):
            sql_lines.append(line)
    if sql_lines:
        return "\n".join(sql_lines).strip()
    # 3. Fallback: return everything (could be just the SQL)
    return text.strip()