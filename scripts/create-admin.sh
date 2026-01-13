#!/bin/bash

# Script de création d'utilisateur admin
# Usage: ./scripts/create-admin.sh [email] [password]

set -e

# Configuration
API_URL="https://procedure1.vercel.app"
SETUP_SECRET="ejZ+z34wqydLsZwnXxfvIBR76CMFbrqHH1NATD6Ip5c="

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Création d'utilisateur admin ===${NC}\n"

# Vérifier les arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo -e "${RED}Erreur: Email et mot de passe requis${NC}"
    echo ""
    echo "Usage:"
    echo "  ./scripts/create-admin.sh <email> <password>"
    echo ""
    echo "Exemple:"
    echo "  ./scripts/create-admin.sh admin@example.com MonMotDePasse123!"
    exit 1
fi

EMAIL="$1"
PASSWORD="$2"

# Valider l'email
if [[ ! "$EMAIL" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    echo -e "${RED}Erreur: Format d'email invalide${NC}"
    exit 1
fi

# Valider le mot de passe (minimum 8 caractères)
if [ ${#PASSWORD} -lt 8 ]; then
    echo -e "${RED}Erreur: Le mot de passe doit contenir au moins 8 caractères${NC}"
    exit 1
fi

echo -e "Email: ${GREEN}$EMAIL${NC}"
echo -e "API URL: ${GREEN}$API_URL${NC}"
echo ""

# Créer l'utilisateur admin
echo "Création de l'utilisateur admin..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/setup/create-admin" \
  -H "Authorization: Bearer $SETUP_SECRET" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

# Séparer le body et le code HTTP
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

# Vérifier le code HTTP
if [ "$HTTP_CODE" -eq 201 ] || [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ Utilisateur admin créé avec succès!${NC}"
    echo ""
    echo "Réponse:"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    echo ""
    echo -e "${GREEN}Vous pouvez maintenant vous connecter avec:${NC}"
    echo -e "  Email: ${GREEN}$EMAIL${NC}"
    echo -e "  URL: ${GREEN}https://procedure1.vercel.app/login${NC}"
elif [ "$HTTP_CODE" -eq 401 ]; then
    echo -e "${RED}❌ Erreur: Non autorisé${NC}"
    echo "Vérifiez que SETUP_SECRET est correct dans le script."
    exit 1
elif [ "$HTTP_CODE" -eq 400 ]; then
    echo -e "${RED}❌ Erreur: Requête invalide${NC}"
    echo "Réponse:"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    exit 1
elif [ "$HTTP_CODE" -eq 404 ]; then
    echo -e "${RED}❌ Erreur: Route non trouvée (404)${NC}"
    echo "La route /api/setup/create-admin n'existe plus."
    echo "Elle a probablement été supprimée après la création de l'admin."
    exit 1
else
    echo -e "${RED}❌ Erreur: Code HTTP $HTTP_CODE${NC}"
    echo "Réponse:"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Création terminée ===${NC}"
