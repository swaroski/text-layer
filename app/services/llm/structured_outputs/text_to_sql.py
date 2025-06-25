from pydantic import BaseModel, Field

class SqlQuery(BaseModel):
    query: str = Field(..., title="A generated SQL query for retrieving data from the table.")
    result_markdown: str = Field("", title="The result of the SQL query as a markdown table.")
    explanation: str = Field("", title="Plain English explanation of the result.")