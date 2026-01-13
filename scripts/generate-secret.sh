#!/bin/bash

# Script pour générer un secret sécurisé
# Usage: ./scripts/generate-secret.sh

echo "Génération d'un secret sécurisé pour NEXTAUTH_SECRET..."
echo ""

# Essayer openssl d'abord
if command -v openssl &> /dev/null; then
    SECRET=$(openssl rand -base64 32)
    echo "Secret généré avec openssl:"
    echo "$SECRET"
    echo ""
    echo "Copiez ce secret et mettez-le à jour dans Vercel Dashboard:"
    echo "https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables"
    echo ""
    echo "Variable: NEXTAUTH_SECRET"
    echo "Valeur: $SECRET"
elif command -v python3 &> /dev/null; then
    SECRET=$(python3 -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())")
    echo "Secret généré avec Python:"
    echo "$SECRET"
    echo ""
    echo "Copiez ce secret et mettez-le à jour dans Vercel Dashboard:"
    echo "https://vercel.com/glenns-projects-7d11114a/procedure1/settings/environment-variables"
    echo ""
    echo "Variable: NEXTAUTH_SECRET"
    echo "Valeur: $SECRET"
else
    echo "Erreur: openssl ou python3 non trouvé"
    echo "Générez manuellement avec: openssl rand -base64 32"
    exit 1
fi
