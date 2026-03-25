#!/bin/bash

# Script para reinstalar docker-compose no WSL

echo "🔧 Removendo docker-compose corrompido..."
sudo rm -f /usr/bin/docker-compose /usr/local/bin/docker-compose

echo "📥 Baixando docker-compose v2.24.5..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose

echo "🔐 Aplicando permissões..."
sudo chmod +x /usr/local/bin/docker-compose

echo "✅ Verificando instalação..."
docker-compose --version

echo ""
echo "✓ Docker Compose reinstalado com sucesso!"
echo "Execute: docker-compose up -d --build"
