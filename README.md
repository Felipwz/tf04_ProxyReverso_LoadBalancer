# TF04 - E-commerce com Load Balancer Avançado

## Aluno
- **Nome:** [Seu Nome Completo]
- **RA:** [Seu RA]
- **Curso:** Análise e Desenvolvimento de Sistemas

## Arquitetura
- **Nginx:** Load balancer com SSL e rate limiting
- **Backend:** 3 instâncias da API para alta disponibilidade
- **Frontend:** Loja virtual estática
- **Admin:** Painel administrativo

## Funcionalidades Implementadas
- ✅ Load balancing com algoritmo least_conn
- ✅ Health checks automáticos
- ✅ Failover transparente
- ✅ SSL/TLS com certificado self-signed
- ✅ Rate limiting para proteção
- ✅ Logs detalhados com upstream info
- ✅ Compressão gzip
- ✅ Virtual hosts

## Como Executar

### Pré-requisitos
- Docker e Docker Compose
- OpenSSL (para gerar certificados SSL)

### Execução
```bash
git clone [URL_DO_SEU_REPO]
cd TF04

# Gerar certificados SSL
./scripts/generate-ssl.sh

# Subir todos os serviços
docker-compose up -d --build

# Verificar status
docker-compose ps
```

## Endpoints

- **Frontend:** http://localhost ou https://localhost
- **API:** http://localhost/api/
- **Admin:** http://localhost/admin/
- **Status:** http://localhost/nginx-status
- **Health:** http://localhost/health
- **Load Balancer Info:** http://localhost/lb-info

## Testes de Load Balancing

```bash
# Testar distribuição de carga
for i in {1..10}; do
  curl -s http://localhost/api/info | grep instance_id
done

# Simular falha de instância
docker stop ecommerce-backend1

# Verificar failover
curl http://localhost/api/info
```

## Monitoramento

- **Logs detalhados:** `docker-compose logs nginx`
- **Métricas:** http://localhost/nginx-status
- **Health checks automáticos** a cada 30s
- **Admin Dashboard:** http://localhost/admin/

## Demonstração das Funcionalidades

### 1. Load Balancer Inteligente
```bash
# Teste de distribuição com algoritmo least_conn
for i in {1..20}; do
  curl -s http://localhost/api/info | jq -r '.instance_id'
done | sort | uniq -c
```

### 2. Health Checks e Failover
```bash
# Parar uma instância e observar failover automático
docker stop ecommerce-backend2
curl -s http://localhost/api/info
docker start ecommerce-backend2
```

### 3. SSL/TLS
```bash
# Testar HTTPS
curl -k https://localhost/api/info
```

### 4. Rate Limiting
```bash
# Teste de rate limiting (irá falhar após limite)
for i in {1..15}; do
  curl -s http://localhost/api/produtos
done
```

## Estrutura do Projeto

```
TF04/
├── README.md
├── docker-compose.yml
├── scripts/
│   └── generate-ssl.sh
├── nginx/
│   ├── nginx.conf
│   ├── ssl/
│   │   ├── cert.pem
│   │   └── key.pem
│   └── conf.d/
│       ├── load-balancer.conf
│       └── ssl.conf
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   ├── produtos.html
│   ├── carrinho.html
│   └── css/style.css
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── config.py
├── admin/
│   ├── Dockerfile
│   ├── dashboard.html
│   └── css/admin.css
└── docs/
    ├── nginx-config.md
    └── load-balancing.md
```

## Configurações Técnicas Implementadas

### Nginx Load Balancer
- **Algoritmo:** least_conn para distribuição inteligente
- **Health Checks:** Verificação automática a cada 30s
- **Timeouts:** 10s conexão, 30s leitura
- **Retry:** 3 tentativas com timeout de 10s
- **SSL:** TLS 1.2/1.3 com certificado self-signed

### Rate Limiting
- **API:** 10 req/s com burst de 10
- **Geral:** 50 req/s com burst de 20
- **Admin:** 5 req/s com burst de 5

### Headers de Segurança
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (HSTS)

### Backend API
- **3 Instâncias** independentes
- **Health check endpoint** personalizado
- **Simulação de carga** variável
- **Logs estruturados** com informações de instância

## Validação

```bash
# Teste de load balancing
docker-compose up -d --build
for i in {1..6}; do curl -s http://localhost/api/info; done
docker-compose down
```

## Logs e Debugging

```bash
# Ver logs do nginx com informações de upstream
docker-compose logs nginx

# Ver logs de uma instância específica
docker-compose logs ecommerce-backend1

# Monitorar logs em tempo real
docker-compose logs -f nginx

# Status dos containers
docker-compose ps

# Verificar health checks
docker inspect ecommerce-backend1 | grep -A 10 Health
```

## Troubleshooting

### Problemas Comuns

1. **Certificados SSL não encontrados:**
   ```bash
   ./scripts/generate-ssl.sh
   ```

2. **Porta 80/443 ocupada:**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo netstat -tulpn | grep :443
   ```

3. **Containers não sobem:**
   ```bash
   docker-compose logs
   docker-compose ps
   ```

4. **Load balancer não distribui:**
   - Verificar se todas as 3 instâncias estão saudáveis
   - Checar logs do nginx para erros de upstream

## Funcionalidades de Demonstração

### Frontend Interativo
- **Teste de Load Balancing:** Botões para executar múltiplas requisições
- **Simulação de Failover:** Instruções para testar failover
- **Monitoramento em Tempo Real:** Exibição da instância atual

### Admin Dashboard
- **Status das Instâncias:** Monitoramento em tempo real
- **Métricas de Performance:** CPU, memória, conexões
- **Logs do Sistema:** Visualização de logs em tempo real
- **Controles de Teste:** Botões para simular carga e verificar saúde

### API Endpoints Demonstrativos
- `GET /api/info` - Informações da instância atual
- `GET /api/produtos` - Lista de produtos com load balancing
- `GET /api/stats` - Estatísticas da instância
- `GET /api/heavy` - Operação pesada para teste de carga
- `GET /health` - Health check customizado

## Tecnologias Utilizadas

- **Docker & Docker Compose:** Orquestração de containers
- **Nginx:** Load balancer e proxy reverso
- **Flask:** Framework backend Python
- **HTML/CSS/JavaScript:** Frontend responsivo
- **OpenSSL:** Geração de certificados SSL

---

**Desenvolvido para demonstrar domínio de configurações avançadas do Nginx como proxy reverso e load balancer.**