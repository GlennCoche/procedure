#!/bin/bash

# Script pour démarrer le serveur Next.js de manière persistante
# Usage: ./scripts/start-server.sh [start|stop|restart|status]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend"
PID_FILE="$PROJECT_DIR/.next-server.pid"
LOG_FILE="$PROJECT_DIR/.next-server.log"

cd "$FRONTEND_DIR"

function start_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Serveur déjà en cours d'exécution (PID: $PID)"
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi

    echo "🚀 Démarrage du serveur Next.js..."
    nohup npm run dev > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > "$PID_FILE"
    
    # Attendre que le serveur soit prêt
    echo "⏳ Attente du démarrage du serveur..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1 || curl -s http://localhost:3001 > /dev/null 2>&1; then
            echo "✅ Serveur démarré avec succès (PID: $SERVER_PID)"
            echo "📝 Logs disponibles dans: $LOG_FILE"
            return 0
        fi
        sleep 1
    done
    
    echo "⚠️  Le serveur semble démarré mais n'est pas encore accessible"
    echo "📝 Vérifiez les logs: tail -f $LOG_FILE"
    return 0
}

function stop_server() {
    if [ ! -f "$PID_FILE" ]; then
        echo "ℹ️  Aucun serveur en cours d'exécution"
        return 0
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "🛑 Arrêt du serveur (PID: $PID)..."
        kill "$PID" 2>/dev/null || true
        sleep 2
        # Force kill si nécessaire
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -9 "$PID" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
        echo "✅ Serveur arrêté"
    else
        echo "ℹ️  Le serveur n'est pas en cours d'exécution"
        rm -f "$PID_FILE"
    fi
}

function restart_server() {
    echo "🔄 Redémarrage du serveur..."
    stop_server
    sleep 2
    start_server
}

function status_server() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Serveur non démarré"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Serveur en cours d'exécution (PID: $PID)"
        
        # Vérifier sur quel port
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo "   Port: 3000"
        elif curl -s http://localhost:3001 > /dev/null 2>&1; then
            echo "   Port: 3001"
        else
            echo "   ⚠️  Port non détecté"
        fi
        
        echo "   Logs: $LOG_FILE"
        return 0
    else
        echo "❌ Serveur non démarré (PID file existe mais processus mort)"
        rm -f "$PID_FILE"
        return 1
    fi
}

case "${1:-start}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        status_server
        ;;
    *)
        echo "Usage: $0 [start|stop|restart|status]"
        exit 1
        ;;
esac
