#!/bin/bash
# Script de deploy rápido

echo "Deploying Actor..."
cd ../
apify push

echo "Worker pronto para deploy no Render."
echo "Certifique-se de configurar as env vars: SUPABASE_URL, SUPABASE_KEY, GROQ_API_KEY"
