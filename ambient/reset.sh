#!/bin/bash
echo "Resetando o ambiente Docker..."
docker compose -f docker-compose.yml down -v
docker compose -f docker-compose.yml build --no-cache
echo "Ambiente resetado e reerguido com sucesso!"