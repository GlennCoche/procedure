#!/bin/bash

# Script de tests des routes API
# Usage: ./scripts/test-api.sh [email] [password]

set -e

# Configuration
API_URL="https://procedure1.vercel.app"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Tests des Routes API ===${NC}\n"

# Vérifier les arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo -e "${YELLOW}Usage: ./scripts/test-api.sh <email> <password>${NC}"
    echo "Les tests d'authentification nécessitent des identifiants valides."
    exit 1
fi

EMAIL="$1"
PASSWORD="$2"

# Variables pour stocker le token
TOKEN=""

# Fonction pour tester une route
test_route() {
    local method=$1
    local endpoint=$2
    local description=$3
    local headers=$4
    local data=$5
    
    echo -e "${YELLOW}Test: $description${NC}"
    echo -e "  ${BLUE}$method $endpoint${NC}"
    
    if [ -n "$data" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            $headers \
            -d "$data")
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            $headers)
    fi
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
        echo -e "  ${GREEN}✅ Succès (HTTP $HTTP_CODE)${NC}"
        return 0
    elif [ "$HTTP_CODE" -eq 401 ]; then
        echo -e "  ${YELLOW}⚠️  Non authentifié (HTTP $HTTP_CODE)${NC}"
        return 1
    elif [ "$HTTP_CODE" -eq 404 ]; then
        echo -e "  ${YELLOW}⚠️  Non trouvé (HTTP $HTTP_CODE)${NC}"
        return 1
    else
        echo -e "  ${RED}❌ Erreur (HTTP $HTTP_CODE)${NC}"
        echo "  Réponse: $(echo "$BODY" | head -c 100)"
        return 1
    fi
}

# Test 1: Login
echo -e "\n${BLUE}=== Test 1: Authentification ===${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" \
    -c /tmp/cookies.txt)

HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" \
    -c /tmp/cookies.txt)

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
    echo -e "${GREEN}✅ Login réussi${NC}"
    echo "  Réponse: $(echo "$LOGIN_RESPONSE" | head -c 200)"
else
    echo -e "${RED}❌ Login échoué (HTTP $HTTP_CODE)${NC}"
    echo "  Réponse: $LOGIN_RESPONSE"
    exit 1
fi

# Test 2: Me (utilisateur actuel)
echo -e "\n${BLUE}=== Test 2: Utilisateur Actuel ===${NC}"
test_route "GET" "/api/auth/me" "Récupérer l'utilisateur actuel" "-b /tmp/cookies.txt"

# Test 3: Liste des procédures
echo -e "\n${BLUE}=== Test 3: Procédures ===${NC}"
test_route "GET" "/api/procedures" "Liste des procédures" "-b /tmp/cookies.txt"

# Test 4: Liste des tips
echo -e "\n${BLUE}=== Test 4: Tips ===${NC}"
test_route "GET" "/api/tips" "Liste des tips" "-b /tmp/cookies.txt"

# Test 5: Liste des exécutions
echo -e "\n${BLUE}=== Test 5: Exécutions ===${NC}"
test_route "GET" "/api/executions" "Liste des exécutions" "-b /tmp/cookies.txt"

# Test 6: Routes setup (devraient retourner 404)
echo -e "\n${BLUE}=== Test 6: Routes Setup (devraient être supprimées) ===${NC}"
SETUP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/setup/create-admin" \
    -H "Authorization: Bearer ejZ+z34wqydLsZwnXxfvIBR76CMFbrqHH1NATD6Ip5c=" \
    -H "Content-Type: application/json")

SETUP_HTTP_CODE=$(echo "$SETUP_RESPONSE" | tail -n1)

if [ "$SETUP_HTTP_CODE" -eq 404 ]; then
    echo -e "${GREEN}✅ Routes setup correctement supprimées (404)${NC}"
else
    echo -e "${RED}❌ Routes setup encore accessibles (HTTP $SETUP_HTTP_CODE)${NC}"
    echo "  ⚠️  Les routes setup devraient être supprimées pour la sécurité"
fi

# Nettoyage
rm -f /tmp/cookies.txt

echo -e "\n${BLUE}=== Tests terminés ===${NC}"
echo -e "${GREEN}✅ Les routes principales sont fonctionnelles${NC}"
