import os
import litellm

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # AWS
    ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID')
    SECRET_ACCESS_KEY = os.environ.get('SECRET_ACCESS_KEY')
    REGION = os.environ.get('REGION')

    # Elasticsearch
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    ELASTICSEARCH_USER = os.environ.get('ELASTICSEARCH_USER')
    ELASTICSEARCH_PASSWORD = os.environ.get('ELASTICSEARCH_PASSWORD')

    # Elasticsearch Indices

    # Langfuse
    LANGFUSE_PUBLIC_KEY = os.environ.get('LANGFUSE_PUBLIC_KEY')
    LANGFUSE_SECRET_KEY = os.environ.get('LANGFUSE_SECRET_KEY')
    LANGFUSE_HOST = os.environ.get('LANGFUSE_HOST')

    if all([LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST]):
        litellm.success_callback = ["langfuse"]
        litellm.failure_callback = ["langfuse"]
    else:
        litellm.success_callback = ["default"]
        litellm.failure_callback = ["default"]

    # LLM
    KNN_EMBEDDING_DIMENSION = int(os.environ.get('KNN_EMBEDDING_DIMENSION', 1536))

    # Environment
    ENV_VARS = []  # List of environment variables to pass to the container/batch

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    FLASK_CONFIG = 'DEV'
    TESTING = True
    DEBUG = True


class TestingConfig(Config):
    FLASK_CONFIG = 'TEST'
    TESTING = True
    DEBUG = True


class StagingConfig(Config):
    FLASK_CONFIG = 'STAGING'
    TESTING = False
    DEBUG = False


class ProductionConfig(Config):
    FLASK_CONFIG = 'PROD'
    TESTING = False
    DEBUG = False


config = {
    'DEV': DevelopmentConfig,
    'TEST': TestingConfig,
    'STAGING': StagingConfig,
    'PROD': ProductionConfig,
}