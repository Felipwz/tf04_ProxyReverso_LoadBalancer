# Configurações da aplicação backend
import os

class Config:
    """Configurações base da aplicação"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'ecommerce-secret-key-tf04')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Configurações da instância
    INSTANCE_ID = os.getenv('INSTANCE_ID', 'backend-default')
    INSTANCE_PORT = int(os.getenv('INSTANCE_PORT', 5000))

    # Configurações de timeouts
    REQUEST_TIMEOUT = 30
    HEALTH_CHECK_INTERVAL = 10

    # Configurações de rate limiting (se necessário)
    RATELIMIT_STORAGE_URL = "memory://"

    # Configurações de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False

# Configuração ativa baseada na variável de ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retorna a configuração ativa"""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])