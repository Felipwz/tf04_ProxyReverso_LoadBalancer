#!/bin/bash

# Script para gerar certificados SSL self-signed para TF04 E-commerce
# Para uso em ambiente de desenvolvimento/demonstração

echo "🔒 Gerando certificados SSL self-signed..."

# Criar diretório SSL se não existir
mkdir -p nginx/ssl

# Gerar chave privada
openssl genrsa -out nginx/ssl/key.pem 2048

# Gerar certificado self-signed válido por 365 dias
openssl req -new -x509 -key nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -subj "/C=BR/ST=SP/L=São Paulo/O=TF04 E-commerce/CN=localhost"

# Definir permissões corretas
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem

echo "✅ Certificados SSL gerados com sucesso em nginx/ssl/"
echo "📋 Para aceitar certificado no navegador:"
echo "   1. Acesse https://localhost"
echo "   2. Clique em 'Avançado' ou 'Advanced'"
echo "   3. Clique em 'Continuar para localhost'"