import faiss
import numpy as np
from typing import List
from openai import OpenAI, OpenAIError

SCHEMA_DESCRIPTIONS = [
    "Table account: Columns are Key, ParentId, Name, AccountType, CalculationMethod, DebitCredit, LineItemRequired, NonLeafInput, NumericFormat, PreventDataEntry, TCMethod, TCFormulaMDX, ProceduralCalc, CurrencyConversionMethod.",
    "Table customer: Columns are Key, ParentId, Name, Channel, Industry, Location, Sales Manager, Salesperson.",
    "Table other: Columns are Key, ParentId, Name.",
    "Table product: Columns are Key, ParentId, Name, Product Line.",
    "Table time: Columns are Name, Month, StartPeriod, EndPeriod, Year, Quarter, FiscalQuarterNumber, FiscalMonthNumber, MonthAbbreviation, FiscalMonthAbbreviationWithYear, MonthWithYear.",
    "Table time_perspective: Columns are Key, ParentId, Name, CalculationMethod, MemberType.",
    "Table version: Columns are Key, ParentId, Name, VersionType, Status, RuleSet, StartPeriod, EndPeriod, CarryForward, CalculationMethod, ReferenceVersion, TimeLevel.",
]

client = OpenAI()

def embed_texts(texts: List[str]) -> np.ndarray:
    """Get OpenAI embeddings for a list of texts."""
    try:
        response = client.embeddings.create(
            input=texts,
            model="text-embedding-ada-002"
        )
        return np.array([e.embedding for e in response.data], dtype="float32")
    except OpenAIError as e:
        return np.zeros((len(texts), 1536), dtype="float32")  # 1536 is the ada-002 dimension

# Precompute embeddings for all schemas
schema_embeddings = embed_texts(SCHEMA_DESCRIPTIONS)
dimension = schema_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(schema_embeddings)

def retrieve_schema_context(user_question: str, top_k: int = 3) -> List[str]:
    """Retrieve the most relevant schema descriptions for a user's question."""
    q_emb = embed_texts([str(user_question)])
    D, I = index.search(q_emb, top_k)
    return [SCHEMA_DESCRIPTIONS[i] for i in I[0]]

