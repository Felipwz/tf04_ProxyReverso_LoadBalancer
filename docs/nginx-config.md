# Configuração Nginx - TF04 E-commerce

## Visão Geral

Este documento detalha as configurações avançadas do Nginx implementadas para o projeto TF04, incluindo load balancing, SSL termination, rate limiting e monitoramento.

## Estrutura de Arquivos

```
nginx/
├── nginx.conf                 # Configuração principal
├── conf.d/
│   ├── load-balancer.conf    # Configuração do load balancer HTTP
│   └── ssl.conf              # Configuração SSL/HTTPS
└── ssl/
    ├── cert.pem              # Certificado SSL
    └── key.pem               # Chave privada SSL
```

## nginx.conf - Configuração Principal

### Workers e Performance
```nginx
worker_processes auto;
worker_connections 1024;
use epoll;
multi_accept on;
```

### Log Format Personalizado
```nginx
log_format upstream_log '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$http_referer" "$http_user_agent" '
                       'rt=$request_time uct="$upstream_connect_time" '
                       'uht="$upstream_header_time" urt="$upstream_response_time" '
                       'upstream_addr="$upstream_addr" upstream_status="$upstream_status"';
```

**Campos importantes:**
- `rt`: Request time total
- `uct`: Upstream connect time
- `uht`: Upstream header time
- `urt`: Upstream response time
- `upstream_addr`: Qual instância processou
- `upstream_status`: Status da resposta upstream

### Rate Limiting Zones
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=general:10m rate=50r/s;
limit_req_zone $binary_remote_addr zone=admin:10m rate=5r/s;
limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;
```

### Upstream Configuration
```nginx
upstream ecommerce_backend {
    least_conn;

    server ecommerce-backend1:5000 max_fails=3 fail_timeout=30s weight=1;
    server ecommerce-backend2:5000 max_fails=3 fail_timeout=30s weight=1;
    server ecommerce-backend3:5000 max_fails=3 fail_timeout=30s weight=1;

    keepalive 32;
}
```

**Parâmetros importantes:**
- `least_conn`: Algoritmo que direciona para o servidor com menos conexões ativas
- `max_fails=3`: Máximo 3 falhas antes de marcar como indisponível
- `fail_timeout=30s`: Tempo que o servidor fica marcado como indisponível
- `weight=1`: Peso igual para todas as instâncias
- `keepalive 32`: Pool de conexões persistentes

## load-balancer.conf - HTTP Configuration

### Server Block Principal
```nginx
server {
    listen 80;
    server_name localhost ecommerce.local;

    limit_req zone=general burst=20 nodelay;
    limit_conn conn_limit_per_ip 10;
}
```

### Location /api/ - Backend Load Balancing
```nginx
location /api/ {
    limit_req zone=api burst=10 nodelay;

    proxy_pass http://ecommerce_backend;

    # Headers de proxy
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $server_name;

    # Timeouts otimizados
    proxy_connect_timeout 10s;
    proxy_send_timeout 10s;
    proxy_read_timeout 30s;

    # Failover automático
    proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    proxy_next_upstream_tries 3;
    proxy_next_upstream_timeout 10s;

    # Headers informativos
    add_header X-Load-Balancer "nginx-least-conn" always;
    add_header X-Response-Time $request_time always;
}
```

### Health Check Endpoint
```nginx
location /health {
    proxy_pass http://ecommerce_backend;

    proxy_connect_timeout 5s;
    proxy_send_timeout 5s;
    proxy_read_timeout 5s;

    access_log off;  # Não logar health checks
}
```

### Nginx Status
```nginx
location /nginx-status {
    stub_status on;
    access_log off;
    add_header Content-Type text/plain;
}
```

## ssl.conf - HTTPS Configuration

### SSL/TLS Settings
```nginx
server {
    listen 443 ssl http2;
    server_name localhost ecommerce.local ssl.ecommerce.local;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
}
```

### Security Headers
```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Content-Type-Options nosniff always;
add_header X-Frame-Options DENY always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## Funcionalidades Avançadas

### 1. Load Balancing Inteligente

**Algoritmo least_conn:**
- Direciona requisições para o servidor com menos conexões ativas
- Mais eficiente que round-robin para cargas desiguais
- Adapta-se automaticamente à capacidade de cada instância

### 2. Health Checks Passivos

**Monitoramento automático:**
- `max_fails=3`: Número de tentativas antes de marcar como down
- `fail_timeout=30s`: Tempo de quarentena para servidores com falha
- Retry automático quando servidor volta a responder

### 3. Failover Automático

**Configuração proxy_next_upstream:**
```nginx
proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
proxy_next_upstream_tries 3;
proxy_next_upstream_timeout 10s;
```

### 4. Rate Limiting por Contexto

- **API:** 10 req/s por IP (proteção contra abuso)
- **Geral:** 50 req/s por IP (navegação normal)
- **Admin:** 5 req/s por IP (área sensível)

### 5. Connection Pooling

- `keepalive 32`: Pool de 32 conexões persistentes
- Reduz latência evitando handshakes TCP repetidos
- Melhora performance significativamente

## Monitoramento e Logs

### Métricas Nginx Status
```
Active connections: 291
server accepts handled requests
 16630948 16630948 31070465
Reading: 6 Writing: 179 Waiting: 106
```

### Log Analysis
```bash
# Requisições por instância
tail -f /var/log/nginx/access.log | grep -o 'upstream_addr="[^"]*"' | sort | uniq -c

# Tempos de resposta
awk '{print $NF}' /var/log/nginx/access.log | grep urt | head -100

# Códigos de status por upstream
grep "upstream_status" /var/log/nginx/access.log | awk '{print $9, $NF}' | sort | uniq -c
```

## Troubleshooting

### Problemas Comuns

1. **Upstream timeout:**
   - Aumentar `proxy_read_timeout`
   - Verificar saúde das instâncias backend

2. **Rate limiting muito restritivo:**
   - Ajustar valores `rate` e `burst`
   - Implementar whitelist para IPs confiáveis

3. **SSL handshake failures:**
   - Verificar certificados
   - Confirmar suporte TLS no cliente

4. **Load balancing desigual:**
   - Verificar configuração `weight`
   - Monitorar health das instâncias

### Comandos de Debug

```bash
# Testar configuração nginx
nginx -t

# Reload sem downtime
nginx -s reload

# Verificar upstreams ativos
curl localhost/nginx-status

# Monitor conexões ativas
watch 'curl -s localhost/nginx-status'
```

## Performance Tuning

### Otimizações Implementadas

1. **Worker optimization:**
   - `worker_processes auto`
   - `worker_connections 1024`

2. **TCP optimization:**
   - `tcp_nopush on`
   - `tcp_nodelay on`

3. **Compression:**
   - Gzip habilitado para texto/JSON
   - Nível 6 de compressão

4. **Buffering:**
   - `proxy_buffering on`
   - Buffers otimizados para 4k

### Recomendações Produção

1. **SSL:**
   - Usar certificados válidos (Let's Encrypt)
   - Habilitar OCSP stapling

2. **Security:**
   - Restringir `/nginx-status` por IP
   - Implementar fail2ban para rate limiting

3. **Monitoring:**
   - Integrar com Prometheus/Grafana
   - Alertas para upstreams down

4. **Caching:**
   - Implementar proxy_cache para static assets
   - Cache de sessões SSL otimizado