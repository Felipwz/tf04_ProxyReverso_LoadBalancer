# Load Balancing - TF04

## Algoritmo: Least Connections

### Conceito
O algoritmo `least_conn` distribui requisições para o servidor que possui o menor número de conexões ativas no momento.

```nginx
upstream ecommerce_backend {
    least_conn;  # Algoritmo de balanceamento

    server ecommerce-backend1:5000;
    server ecommerce-backend2:5000;
    server ecommerce-backend3:5000;
}
```

### Por que Least Connections?

**Vantagens:**
- Distribuição mais justa para requisições de duração variável
- Evita sobrecarga de uma instância específica
- Ideal para APIs com processamento assíncrono
- Melhor para workloads heterogêneos

**Comparação com outros algoritmos:**

| Algoritmo | Uso ideal | Desvantagem |
|-----------|-----------|-------------|
| `round-robin` | Requisições uniformes | Ignora carga atual |
| `least_conn` | Requisições variáveis | Overhead de tracking |
| `ip_hash` | Sessões sticky | Distribuição desigual |

## Demonstração de Funcionamento

### Teste 1: Distribuição Normal
```bash
for i in {1..10}; do
  curl -s http://localhost/api/info | jq -r .instance_id
done
```

**Resultado esperado:**
```
backend-instance-1
backend-instance-2
backend-instance-3
backend-instance-1
backend-instance-2
...
```

### Teste 2: Carga Diferenciada
```bash
# Gerar carga na instância 1
curl http://localhost/api/load-test &
curl http://localhost/api/load-test &

# Novas requisições irão para instâncias 2 e 3
for i in {1..5}; do
  curl -s http://localhost/api/info
done
```

O algoritmo detecta que instância 1 está ocupada e distribui para outras.

## Health Checks

### Configuração no Docker Compose
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s
```

### Configuração no Nginx
```nginx
server ecommerce-backend1:5000 max_fails=3 fail_timeout=30s;
```

**Funcionamento:**
1. Nginx detecta falhas (timeout, 5xx)
2. Após 3 falhas consecutivas, marca instância como `down`
3. Aguarda 30 segundos antes de tentar novamente
4. Health check do Docker verifica a cada 30s

### Endpoint de Health Check
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'instance_id': INSTANCE_ID,
        'uptime_seconds': int(time.time() - start_time),
        'request_count': request_count
    }), 200
```

## Failover Automático

### Configuração
```nginx
proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
proxy_next_upstream_tries 3;
proxy_next_upstream_timeout 10s;
```

### Cenários de Failover

**1. Backend Down:**
```bash
# Parar instância
docker stop ecommerce-backend1

# Requisições automaticamente vão para backend2 e backend3
curl http://localhost/api/info
# Retorna: backend-instance-2 ou backend-instance-3
```

**2. Backend Lento (Timeout):**
```bash
# Se backend1 não responder em 10s
# Nginx automaticamente tenta backend2
```

**3. Backend com Erro 500:**
```bash
# Backend1 retorna 500
# Nginx tenta próximo backend automaticamente
```

### Fluxo de Failover
```
Request → nginx
    ↓
Try backend1 → timeout/error
    ↓
Try backend2 → success
    ↓
Response to client
```

**Tempo máximo:** 10s × 3 tentativas = 30s

## Distribuição de Carga

### Métricas Observáveis

**1. Via Logs:**
```bash
docker-compose logs nginx | grep "upstream:"
```

Exemplo de log:
```
upstream: ecommerce-backend1:5000 upstream_status: 200 request_time: 0.123
```

**2. Via API:**
```bash
# Estatísticas de cada instância
curl http://localhost/api/stats
```

**3. Via Nginx Status:**
```bash
curl http://localhost/nginx-status
```

Retorna:
```
Active connections: 5
Reading: 0 Writing: 1 Waiting: 4
```

### Simulação de Carga

**Teste de distribuição uniforme:**
```bash
#!/bin/bash
for i in {1..30}; do
  curl -s http://localhost/api/info | jq -r .instance_id
  sleep 0.1
done | sort | uniq -c
```

**Resultado esperado:**
```
  10 backend-instance-1
  10 backend-instance-2
  10 backend-instance-3
```

**Teste de failover:**
```bash
# Terminal 1: monitorar logs
docker-compose logs -f nginx

# Terminal 2: parar instância
docker stop ecommerce-backend2

# Terminal 3: fazer requisições
for i in {1..10}; do curl http://localhost/api/info; done

# Verificar que nenhuma requisição falhou
```

## Connection Pooling

### Keepalive
```nginx
keepalive 32;
```

**Benefícios:**
- Reutiliza conexões TCP
- Reduz latência de handshake
- Diminui overhead de CPU

**Como funciona:**
1. Nginx mantém até 32 conexões abertas com cada backend
2. Requisições reutilizam conexões existentes
3. Conexões idle são fechadas após timeout

## Performance e Otimizações

### Buffer Configuration
```nginx
proxy_buffering on;
proxy_buffer_size 4k;
proxy_buffers 8 4k;
```

- Armazena resposta do backend em memória
- Libera backend mais rapidamente
- Cliente pode ser mais lento sem bloquear backend

### Timeouts
```nginx
proxy_connect_timeout 10s;   # Conexão inicial
proxy_send_timeout 10s;      # Envio de dados
proxy_read_timeout 30s;      # Leitura de resposta
```

**Tuning recomendado:**
- APIs rápidas: 5-10s
- APIs com processamento pesado: 30-60s
- APIs com streaming: aumentar read_timeout

## Rate Limiting

### Configuração por Zona
```nginx
# 10 requisições/segundo para API
limit_req zone=api burst=10 nodelay;
```

**Comportamento:**
- Taxa base: 10 req/s
- Burst: permite até 10 requisições extras
- `nodelay`: processa burst imediatamente

### Teste de Rate Limiting
```bash
# Disparar 50 requisições rapidamente
for i in {1..50}; do
  curl -w "%{http_code}\n" http://localhost/api/info &
done | sort | uniq -c
```

**Resultado esperado:**
```
  20 200  # Permitidas
  30 503  # Rate limited
```

## Monitoramento de Load Balancing

### Logs Estruturados
```bash
# Ver distribuição de carga
docker-compose logs nginx | grep upstream_addr | \
  awk '{print $NF}' | sort | uniq -c

# Ver tempos de resposta
docker-compose logs nginx | grep request_time | \
  awk '{print $(NF-1)}' | sort -n
```

### Dashboard Simples
```bash
# Script de monitoramento contínuo
watch -n 1 'curl -s http://localhost/nginx-status'
```

### Métricas por Instância
```bash
# Comparar request count de cada backend
curl -s http://localhost/api/stats | jq .stats.total_requests
```

## Troubleshooting

### Problema: Uma instância recebe todas as requisições
**Causa:** Outras instâncias estão down ou unhealthy

**Solução:**
```bash
# Verificar health de cada backend
docker-compose ps
curl http://localhost/health
docker-compose logs ecommerce-backend2
```

### Problema: Requisições falhando (502/504)
**Causa:** Todas as instâncias estão down ou sobrecarregadas

**Solução:**
```bash
# Verificar se backends estão rodando
docker-compose ps | grep backend

# Verificar logs de erro
docker-compose logs nginx | grep error

# Restart backends
docker-compose restart ecommerce-backend1 ecommerce-backend2 ecommerce-backend3
```

### Problema: Distribuição desigual
**Causa:** Uma instância processa requisições mais rápido

**Solução:** Isso é esperado com `least_conn`. A instância mais rápida receberá mais requisições porque libera conexões mais rapidamente.

## Boas Práticas

1. **Health Checks:**
   - Sempre implemente endpoints de health
   - Configure timeouts adequados
   - Use checks leves (não teste todo o sistema)

2. **Failover:**
   - Configure max_fails e fail_timeout
   - Use proxy_next_upstream
   - Teste regularmente parando instâncias

3. **Logging:**
   - Sempre logue upstream_addr
   - Monitore request_time e upstream_response_time
   - Use estrutura consistente

4. **Capacidade:**
   - Mantenha sempre N+1 redundância
   - Teste com carga realista
   - Configure resource limits no Docker

5. **Gradual Rollout:**
   - Use weights para rollout gradual
   - Monitore métricas durante deploy
   - Mantenha possibilidade de rollback rápido
