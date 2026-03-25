#!/bin/bash

# Script alternativo para subir containers sem docker-compose
# Uso: ./scripts/start-manual.sh

set -e

echo "🌐 Criando network..."
docker network create ecommerce_network 2>/dev/null || echo "Network já existe"

echo "🔨 Building images..."
docker build -t ecommerce-backend:latest ./backend
docker build -t ecommerce-frontend:latest ./frontend
docker build -t ecommerce-admin:latest ./admin

echo "🚀 Iniciando backends..."
docker run -d --name ecommerce-backend1 \
  --network ecommerce_network \
  -e INSTANCE_ID=backend-instance-1 \
  -e INSTANCE_PORT=5000 \
  -e FLASK_ENV=production \
  ecommerce-backend:latest

docker run -d --name ecommerce-backend2 \
  --network ecommerce_network \
  -e INSTANCE_ID=backend-instance-2 \
  -e INSTANCE_PORT=5000 \
  -e FLASK_ENV=production \
  ecommerce-backend:latest

docker run -d --name ecommerce-backend3 \
  --network ecommerce_network \
  -e INSTANCE_ID=backend-instance-3 \
  -e INSTANCE_PORT=5000 \
  -e FLASK_ENV=production \
  ecommerce-backend:latest

echo "🎨 Iniciando frontend..."
docker run -d --name ecommerce-frontend \
  --network ecommerce_network \
  ecommerce-frontend:latest

echo "⚙️ Iniciando admin..."
docker run -d --name ecommerce-admin \
  --network ecommerce_network \
  ecommerce-admin:latest

echo "🔒 Iniciando Nginx..."
docker run -d --name ecommerce-nginx \
  --network ecommerce_network \
  -p 80:80 -p 443:443 \
  -v "$(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro" \
  -v "$(pwd)/nginx/conf.d:/etc/nginx/conf.d:ro" \
  -v "$(pwd)/nginx/ssl:/etc/nginx/ssl:ro" \
  nginx:alpine

echo ""
echo "✅ Containers iniciados!"
echo ""
echo "📊 Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌍 Acesse:"
echo "  - Frontend: http://localhost"
echo "  - API: http://localhost/api/info"
echo "  - Status: http://localhost/nginx-status"
echo ""
echo "🛑 Para parar: ./scripts/stop-manual.sh"
