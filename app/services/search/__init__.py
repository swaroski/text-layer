from typing import Optional

from elasticsearch import Elasticsearch, ConnectionError as ESConnectionError
from flask import current_app

from app import logger


def opensearch_session() -> Optional[Elasticsearch]:
    """
    Creates and returns an OpenSearch/Elasticsearch session.

    Ensures the necessary configuration values are set before attempting to
    connect. Logs errors if connection fails or if configuration is missing.

    Returns:
        Optional[Elasticsearch]: A configured Elasticsearch session if successful, otherwise None.
    """
    try:
        # Retrieve necessary configurations
        es_url = current_app.config.get("ELASTICSEARCH_URL")
        es_user = current_app.config.get("ELASTICSEARCH_USER")
        es_password = current_app.config.get("ELASTICSEARCH_PASSWORD")

        if not es_url or not es_user or not es_password:
            logger.error("Missing OpenSearch/Elasticsearch configuration values.")
            return None

        session = Elasticsearch([es_url], http_auth=(es_user, es_password))
        logger.info(f"Connected to OpenSearch/Elasticsearch at {es_url}")
        return session

    except ESConnectionError as err:
        logger.error(f"Failed to connect to OpenSearch/Elasticsearch: {err}")
    except Exception as err:
        logger.error(f"Unexpected error while creating OpenSearch/Elasticsearch session: {err}")

    return None