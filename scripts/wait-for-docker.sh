#!/bin/bash

# Script para aguardar Docker estar disponível
echo "🐋 Verificando Docker..."
echo ""
echo "👉 ABRA O DOCKER DESKTOP NO WINDOWS AGORA"
echo ""
echo "Aguardando Docker ficar disponível..."

max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker ps >/dev/null 2>&1; then
        echo ""
        echo "✅ Docker está funcionando!"
        echo ""
        docker version --format '{{.Server.Version}}'
        echo ""
        echo "Pronto para usar! Execute:"
        echo "  ./scripts/start-manual.sh"
        echo "  OU"
        echo "  docker-compose up -d --build"
        exit 0
    fi

    attempt=$((attempt + 1))
    echo -n "."
    sleep 1
done

echo ""
echo "❌ Timeout: Docker não iniciou em 60 segundos"
echo ""
echo "Verifique:"
echo "  1. Docker Desktop está aberto no Windows?"
echo "  2. Ícone da baleia está azul?"
echo "  3. Settings → Resources → WSL Integration está ativado?"
exit 1
