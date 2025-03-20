from typing import Any, Dict, List, Optional, Tuple, Union

from elasticsearch import Elasticsearch, helpers, RequestError
from elasticsearch.exceptions import ConnectionError as ESConnectionError

from app import logger


def create_entry(
    session: Elasticsearch,
    index: str,
    body: Dict[str, Any],
    document_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Create or update a document in OpenSearch/Elasticsearch.

    Args:
        session (Elasticsearch): The Elasticsearch session.
        index (str): The index where the document will be stored.
        body (Dict[str, Any]): The document body.
        document_id (Optional[str], optional): The document ID. If None, Elasticsearch auto-generates one.

    Returns:
        Optional[Dict[str, Any]]: The created/updated document response if successful, otherwise None.
    """
    try:
        response = session.index(index=index, id=document_id, body=body)
        logger.info(f"Document {'updated' if document_id else 'created'} in index '{index}' (ID: {document_id or response['_id']}).")
        return response
    except RequestError as err:
        logger.error(f"Failed to create/update document in index '{index}' (ID: {document_id}): {err}")
    except ESConnectionError as err:
        logger.error(f"Elasticsearch connection error while creating/updating document in index '{index}': {err}")
    return None


def bulk_create_entries(
    session: Elasticsearch,
    documents: List[Dict[str, Any]],
    index: str,
    request_timeout: int = 180
) -> Optional[Tuple[int, List[Any]]]:
    """
    Bulk insert multiple documents into OpenSearch/Elasticsearch.

    Args:
        session (Elasticsearch): The Elasticsearch session.
        documents (List[Dict[str, Any]]): List of documents to insert.
        index (str): The index where the documents will be stored.
        request_timeout (int, optional): Timeout for the bulk operation. Defaults to 180 seconds.

    Returns:
        Optional[Tuple[int, List[Any]]]: A tuple containing the number of successfully inserted documents
        and a list of any errors encountered. Returns None on failure.
    """
    if not documents:
        logger.warning(f"No documents provided for bulk insert into index '{index}'.")
        return None

    bulk_actions = [
        {"_index": index, "_id": doc["id"], "_source": doc} if "id" in doc else {"_index": index, "_source": doc}
        for doc in documents
    ]

    try:
        success_count, errors = helpers.bulk(session, bulk_actions, request_timeout=request_timeout)
        logger.info(f"Bulk insert: {success_count} documents added to index '{index}'.")

        if errors:
            logger.warning(f"Bulk insert into '{index}' completed with {len(errors)} errors.")
        return success_count, errors
    except RequestError as err:
        logger.error(f"Bulk insert failed for index '{index}': {err}")
    except ESConnectionError as err:
        logger.error(f"Elasticsearch connection error during bulk insert into index '{index}': {err}")
    return None