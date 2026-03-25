#!/bin/bash

# Script para parar e remover containers
echo "🛑 Parando containers..."
docker stop ecommerce-nginx ecommerce-backend1 ecommerce-backend2 ecommerce-backend3 ecommerce-frontend ecommerce-admin 2>/dev/null || true

echo "🗑️ Removendo containers..."
docker rm ecommerce-nginx ecommerce-backend1 ecommerce-backend2 ecommerce-backend3 ecommerce-frontend ecommerce-admin 2>/dev/null || true

echo "🌐 Removendo network..."
docker network rm ecommerce_network 2>/dev/null || true

echo "✅ Limpeza concluída!"
