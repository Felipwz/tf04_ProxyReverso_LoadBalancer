# Backend API para E-commerce com Load Balancer
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import time
import uuid
from datetime import datetime
import logging
from config import get_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(instance_id)s] - %(message)s'
)

app = Flask(__name__)
CORS(app)

# Carregar configurações
config = get_config()
app.config.from_object(config)

# ID único da instância
INSTANCE_ID = os.getenv('INSTANCE_ID', f'backend-{str(uuid.uuid4())[:8]}')

# Adicionar instance_id ao contexto de logging
old_factory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.instance_id = INSTANCE_ID
    return record

logging.setLogRecordFactory(record_factory)

logger = logging.getLogger(__name__)

# Simular dados de produtos
PRODUTOS = [
    {"id": 1, "nome": "Smartphone Pro", "preco": 1299.99, "categoria": "Eletrônicos"},
    {"id": 2, "nome": "Notebook Gamer", "preco": 2599.99, "categoria": "Computadores"},
    {"id": 3, "nome": "Headset Wireless", "preco": 299.99, "categoria": "Áudio"},
    {"id": 4, "nome": "Smartwatch Sport", "preco": 899.99, "categoria": "Wearables"},
    {"id": 5, "nome": "Tablet 10\"", "preco": 699.99, "categoria": "Eletrônicos"},
    {"id": 6, "nome": "Camera 4K", "preco": 1899.99, "categoria": "Fotografia"},
]

# Contador de requisições para esta instância
request_count = 0
start_time = time.time()

@app.before_request
def before_request():
    global request_count
    request_count += 1
    logger.info(f"Request {request_count}: {request.method} {request.path}")

@app.route('/health')
def health_check():
    """Health check endpoint para o load balancer"""
    return jsonify({
        'status': 'healthy',
        'instance_id': INSTANCE_ID,
        'timestamp': datetime.utcnow().isoformat(),
        'uptime_seconds': int(time.time() - start_time),
        'request_count': request_count
    }), 200

@app.route('/api/info')
def api_info():
    """Informações da instância da API"""
    return jsonify({
        'instance_id': INSTANCE_ID,
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'request_count': request_count,
        'uptime_seconds': int(time.time() - start_time),
        'environment': os.getenv('FLASK_ENV', 'development')
    })

@app.route('/api/stats')
def api_stats():
    """Estatísticas da instância"""
    return jsonify({
        'instance_id': INSTANCE_ID,
        'stats': {
            'total_requests': request_count,
            'uptime_seconds': int(time.time() - start_time),
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'current_time': datetime.utcnow().isoformat(),
            'memory_usage': 'simulation_only',
            'cpu_usage': 'simulation_only'
        }
    })

@app.route('/api/produtos')
def get_produtos():
    """Lista todos os produtos"""
    logger.info(f"Listando {len(PRODUTOS)} produtos")

    # Simular diferentes tempos de resposta para demonstrar load balancing
    import random
    delay = random.uniform(0.1, 0.5)
    time.sleep(delay)

    return jsonify({
        'produtos': PRODUTOS,
        'total': len(PRODUTOS),
        'instance_id': INSTANCE_ID,
        'response_time': delay
    })

@app.route('/api/produtos/<int:produto_id>')
def get_produto(produto_id):
    """Obtém um produto específico"""
    produto = next((p for p in PRODUTOS if p['id'] == produto_id), None)

    if not produto:
        return jsonify({'error': 'Produto não encontrado', 'instance_id': INSTANCE_ID}), 404

    return jsonify({
        'produto': produto,
        'instance_id': INSTANCE_ID
    })

@app.route('/api/produtos', methods=['POST'])
def create_produto():
    """Adiciona um novo produto (simulação)"""
    data = request.get_json()

    if not data or not all(key in data for key in ['nome', 'preco', 'categoria']):
        return jsonify({'error': 'Dados inválidos', 'instance_id': INSTANCE_ID}), 400

    novo_produto = {
        'id': max([p['id'] for p in PRODUTOS]) + 1,
        'nome': data['nome'],
        'preco': float(data['preco']),
        'categoria': data['categoria']
    }

    PRODUTOS.append(novo_produto)
    logger.info(f"Produto criado: {novo_produto}")

    return jsonify({
        'produto': novo_produto,
        'message': 'Produto criado com sucesso',
        'instance_id': INSTANCE_ID
    }), 201

@app.route('/api/carrinho', methods=['POST'])
def add_to_cart():
    """Simula adição ao carrinho"""
    data = request.get_json()

    if not data or 'produto_id' not in data:
        return jsonify({'error': 'produto_id é obrigatório', 'instance_id': INSTANCE_ID}), 400

    quantidade = data.get('quantidade', 1)

    # Simular processamento
    time.sleep(0.2)

    return jsonify({
        'message': 'Produto adicionado ao carrinho',
        'produto_id': data['produto_id'],
        'quantidade': quantidade,
        'instance_id': INSTANCE_ID
    })

@app.route('/api/load-test')
def load_test():
    """Endpoint para testar carga computacional"""
    # Simular diferentes cargas de trabalho
    instance_num = int(INSTANCE_ID.split('-')[-1]) if '-' in INSTANCE_ID else 1

    # Cada instância tem uma "personalidade" diferente
    if instance_num == 1:
        # Instância rápida
        delay = 0.1
        workload = "light"
    elif instance_num == 2:
        # Instância média
        delay = 0.3
        workload = "medium"
    else:
        # Instância mais lenta (para demonstrar least_conn)
        delay = 0.5
        workload = "heavy"

    time.sleep(delay)

    return jsonify({
        'instance_id': INSTANCE_ID,
        'workload': workload,
        'processing_time': delay,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint não encontrado',
        'instance_id': INSTANCE_ID
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Erro interno do servidor',
        'instance_id': INSTANCE_ID
    }), 500

if __name__ == '__main__':
    logger.info(f"Iniciando instância {INSTANCE_ID}")

    # Executar apenas em modo desenvolvimento direto
    # Em produção, usar gunicorn via Dockerfile
    app.run(
        debug=config.DEBUG,
        host='0.0.0.0',
        port=config.INSTANCE_PORT
    )