#!/usr/bin/env python3
"""
Serveur de démarrage minimal - Accessible sur http://localhost:8080
Permet de démarrer l'application via une interface web
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import json
import os
import sys
import time
import threading
import socket
import traceback
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# État global des processus
processes = {}
status = {
    "backend": {"running": False, "url": "http://localhost:8000"},
    "frontend": {"running": False, "url": "http://localhost:3000"}
}

# Système de logs
log_file = Path(__file__).parent / "logs" / f"startup_{datetime.now().strftime('%Y%m%d')}.log"
log_file.parent.mkdir(exist_ok=True)

def log_debug(level, message, data=None):
    """Logger détaillé"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    log_entry = f"[{timestamp}] [{level.upper()}] {message}"
    if data:
        log_entry += f" | Data: {json.dumps(data, default=str)}"
    log_entry += "\n"
    
    # Écrire dans le fichier
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except:
        pass
    
    # Afficher dans la console
    if level in ['error', 'critical']:
        print(log_entry.strip(), file=sys.stderr)
    else:
        print(log_entry.strip())

def check_backend():
    """Vérifier si le backend est accessible"""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:8000/health", method="GET")
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status == 200
    except:
        return False

def check_frontend():
    """Vérifier si le frontend est accessible"""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:3000", method="GET")
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status == 200
    except:
        return False

def start_backend():
    """Démarrer le backend"""
    try:
        log_debug('info', 'Fonction start_backend() appelée')
        backend_dir = Path(__file__).parent / "backend"
        log_debug('debug', 'Backend directory', {'path': str(backend_dir)})
        
        venv_python = backend_dir / "venv" / "bin" / "python"
        log_debug('debug', 'Venv python path', {'path': str(venv_python), 'exists': venv_python.exists()})
        
        if not venv_python.exists():
            error_msg = "Environnement virtuel non trouvé. Exécutez: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
            log_debug('error', error_msg)
            return None, error_msg
        
        # Vérifier que .env existe
        env_file = backend_dir / ".env"
        if not env_file.exists():
            log_debug('info', 'Création du fichier .env')
            env_file.write_text("""OPENAI_API_KEY=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
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=change-me-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001
""")
        
        # Vérifier que la base de données est initialisée
        db_file = backend_dir / "app.db"
        if not db_file.exists():
            log_debug('info', 'Initialisation de la base de données')
            try:
                init_script = backend_dir / "scripts" / "init_db.py"
                if init_script.exists():
                    result = subprocess.run([str(venv_python), str(init_script)], 
                                         cwd=str(backend_dir), 
                                         capture_output=True, 
                                         timeout=10)
                    log_debug('info', 'Init DB terminé', {
                        'returncode': result.returncode,
                        'stdout': result.stdout.decode()[:200],
                        'stderr': result.stderr.decode()[:200]
                    })
            except Exception as e:
                log_debug('warn', 'Erreur init DB (non bloquant)', {'error': str(e)})
        
        log_debug('info', 'Lancement uvicorn')
        process = subprocess.Popen(
            [str(venv_python), "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, PYTHONUNBUFFERED="1")
        )
        log_debug('info', 'Processus backend créé', {'pid': process.pid})
        return process, None
    except Exception as e:
        log_debug('error', 'Exception dans start_backend', {
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        return None, str(e)

def start_frontend():
    """Démarrer le frontend"""
    try:
        log_debug('info', 'Fonction start_frontend() appelée')
        frontend_dir = Path(__file__).parent / "frontend"
        log_debug('debug', 'Frontend directory', {'path': str(frontend_dir)})
        
        # Vérifier que .env.local existe
        env_file = frontend_dir / ".env.local"
        if not env_file.exists():
            log_debug('info', 'Création du fichier .env.local')
            env_file.write_text("""NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=change-me-in-production-12345
""")
        
        node_modules = frontend_dir / "node_modules"
        log_debug('debug', 'Vérification node_modules', {'exists': node_modules.exists()})
        if not node_modules.exists():
            error_msg = "Dépendances npm non installées. Exécutez: cd frontend && npm install"
            log_debug('error', error_msg)
            return None, error_msg
        
        package_json = frontend_dir / "package.json"
        log_debug('debug', 'Vérification package.json', {'exists': package_json.exists()})
        if not package_json.exists():
            error_msg = "package.json non trouvé dans le dossier frontend"
            log_debug('error', error_msg)
            return None, error_msg
        
        log_debug('info', 'Lancement npm run dev')
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, NODE_ENV="development")
        )
        log_debug('info', 'Processus frontend créé', {'pid': process.pid})
        return process, None
    except Exception as e:
        log_debug('error', 'Exception dans start_frontend', {
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        return None, str(e)

class StartupHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            log_debug('debug', f'GET request: {self.path}')
            if self.path == "/" or self.path == "/index.html":
                log_debug('info', 'Serving HTML page')
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                html = self.get_html()
                self.wfile.write(html.encode('utf-8'))
            elif self.path == "/api/status":
                log_debug('info', 'GET /api/status')
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                status["backend"]["running"] = check_backend()
                status["frontend"]["running"] = check_frontend()
                log_debug('info', 'Status checked', status)
                self.wfile.write(json.dumps(status).encode())
            elif self.path == "/api/logs":
                # Retourner les logs de debug
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        logs = f.readlines()[-100:]  # Dernières 100 lignes
                    self.wfile.write(json.dumps({"logs": logs}).encode())
                except:
                    self.wfile.write(json.dumps({"logs": []}).encode())
            elif self.path.startswith("/api/"):
                log_debug('warn', f'Route API non gérée: {self.path}')
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            else:
                log_debug('warn', f'404: {self.path}')
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            log_debug('error', f'Erreur dans do_GET: {self.path}', {
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            self.send_response(500)
            self.end_headers()
    
    def do_POST(self):
        try:
            log_debug('debug', f'POST request: {self.path}')
            if self.path == "/api/start":
                log_debug('info', 'POST /api/start - Démarrage des serveurs')
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                
                result = {"status": "ok", "message": "Démarrage en cours..."}
                
                # Démarrer backend
                backend_running = check_backend()
                log_debug('info', f'Backend running: {backend_running}')
                if not backend_running and "backend" not in processes:
                    log_debug('info', 'Démarrage du backend...')
                    try:
                        proc, error = start_backend()
                        if proc:
                            processes["backend"] = proc
                            result["backend"] = "started"
                            log_debug('info', 'Backend démarré avec succès', {'pid': proc.pid})
                        else:
                            result["backend"] = f"error: {error}"
                            log_debug('error', 'Erreur démarrage backend', {'error': error})
                    except Exception as e:
                        error_msg = str(e)
                        result["backend"] = f"error: {error_msg}"
                        log_debug('error', 'Exception lors démarrage backend', {
                            'error': error_msg,
                            'traceback': traceback.format_exc()
                        })
                elif backend_running:
                    result["backend"] = "already_running"
                    log_debug('info', 'Backend déjà en cours d\'exécution')
                
                # Démarrer frontend
                frontend_running = check_frontend()
                log_debug('info', f'Frontend running: {frontend_running}')
                if not frontend_running and "frontend" not in processes:
                    log_debug('info', 'Démarrage du frontend...')
                    try:
                        proc, error = start_frontend()
                        if proc:
                            processes["frontend"] = proc
                            result["frontend"] = "started"
                            log_debug('info', 'Frontend démarré avec succès', {'pid': proc.pid})
                        else:
                            result["frontend"] = f"error: {error}"
                            log_debug('error', 'Erreur démarrage frontend', {'error': error})
                    except Exception as e:
                        error_msg = str(e)
                        result["frontend"] = f"error: {error_msg}"
                        log_debug('error', 'Exception lors démarrage frontend', {
                            'error': error_msg,
                            'traceback': traceback.format_exc()
                        })
                elif frontend_running:
                    result["frontend"] = "already_running"
                    log_debug('info', 'Frontend déjà en cours d\'exécution')
                
                log_debug('info', 'Résultat démarrage', result)
                self.wfile.write(json.dumps(result).encode())
            elif self.path == "/api/stop":
                log_debug('info', 'POST /api/stop - Arrêt des serveurs')
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                
                for name, proc in processes.items():
                    log_debug('info', f'Arrêt du processus: {name}', {'pid': proc.pid})
                    try:
                        proc.terminate()
                    except Exception as e:
                        log_debug('error', f'Erreur arrêt {name}', {'error': str(e)})
                processes.clear()
                
                self.wfile.write(json.dumps({"status": "stopped"}).encode())
            else:
                log_debug('warn', f'404 POST: {self.path}')
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            log_debug('error', f'Erreur dans do_POST: {self.path}', {
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            try:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            except:
                pass
    
    def log_message(self, format, *args):
        pass  # Désactiver les logs par défaut
    
    def get_html(self):
        return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Démarrage - Système de Procédures</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .status-card {
            background: #f5f5f5;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-card.running { background: #d4edda; }
        .status-card.stopped { background: #f8d7da; }
        .status-indicator {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #dc3545;
        }
        .status-indicator.running { background: #28a745; }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            transition: all 0.3s;
        }
        .btn:hover { background: #5568d3; transform: translateY(-2px); }
        .btn:disabled { background: #ccc; cursor: not-allowed; }
        .btn-stop {
            background: #dc3545;
            margin-top: 10px;
        }
        .btn-stop:hover { background: #c82333; }
        .logs {
            background: #1e1e1e;
            color: #0f0;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            max-height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .log-entry {
            margin: 5px 0;
        }
        .ready-message {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .ready-message a {
            color: #155724;
            text-decoration: underline;
            display: block;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Système de Procédures</h1>
        <p class="subtitle">Panneau de contrôle - Démarrage automatique</p>
        
        <div id="backend-status" class="status-card stopped">
            <div>
                <strong>Backend API</strong>
                <div style="font-size: 12px; color: #666;">http://localhost:8000</div>
            </div>
            <div class="status-indicator" id="backend-indicator"></div>
        </div>
        
        <div id="frontend-status" class="status-card stopped">
            <div>
                <strong>Frontend Web</strong>
                <div style="font-size: 12px; color: #666;">http://localhost:3000</div>
            </div>
            <div class="status-indicator" id="frontend-indicator"></div>
        </div>
        
        <button class="btn" id="start-btn" onclick="startServers()">
            ▶️ Démarrer l'Application
        </button>
        <button class="btn btn-stop" id="stop-btn" onclick="stopServers()" style="display: none;">
            ⏹️ Arrêter
        </button>
        
        <div id="logs" class="logs" style="display: none;"></div>
        <div id="ready-message" class="ready-message" style="display: none;"></div>
    </div>
    
    <script>
        let checkInterval;
        
        // Système de logs détaillé
        const debugLogs = [];
        const maxDebugLogs = 500;
        
        function addDebugLog(level, message, data) {
            const timestamp = new Date().toISOString();
            const logEntry = {
                timestamp: timestamp,
                level: level,
                message: message,
                data: data || null,
                stack: level === 'error' ? new Error().stack : null
            };
            debugLogs.push(logEntry);
            if (debugLogs.length > maxDebugLogs) {
                debugLogs.shift();
            }
            const consoleMethod = level === 'error' ? 'error' : (level === 'warn' ? 'warn' : 'log');
            console[consoleMethod](
                '[' + timestamp + '] [' + level.toUpperCase() + '] ' + message,
                data || ''
            );
        }
        
        function addLog(message) {
            addDebugLog('info', message);
            const logs = document.getElementById('logs');
            logs.style.display = 'block';
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.textContent = new Date().toLocaleTimeString() + ' - ' + message;
            logs.appendChild(entry);
            logs.scrollTop = logs.scrollHeight;
        }
        
        // Logger toutes les erreurs
        window.addEventListener('error', function(event) {
            addDebugLog('error', 'Erreur JavaScript: ' + event.message, {
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error ? event.error.toString() : null
            });
        });
        
        window.addEventListener('unhandledrejection', function(event) {
            addDebugLog('error', 'Promesse rejetée: ' + event.reason, {
                reason: event.reason ? event.reason.toString() : null
            });
        });
        
        function updateStatus() {
            fetch('/api/status')
                .then(function(r) {
                    if (!r.ok) {
                        throw new Error('Erreur HTTP: ' + r.status);
                    }
                    return r.json();
                })
                .then(function(data) {
                    if (data && data.backend && data.frontend) {
                        updateStatusCard('backend', data.backend.running);
                        updateStatusCard('frontend', data.frontend.running);
                        
                        if (data.backend.running && data.frontend.running) {
                            document.getElementById('start-btn').disabled = true;
                            document.getElementById('stop-btn').style.display = 'block';
                            showReadyMessage();
                        }
                    }
                })
                .catch(function(e) {
                    console.error('Erreur lors de la vérification:', e);
                });
        }
        
        function updateStatusCard(name, running) {
            const card = document.getElementById(name + '-status');
            const indicator = document.getElementById(name + '-indicator');
            if (running) {
                card.className = 'status-card running';
                indicator.className = 'status-indicator running';
            } else {
                card.className = 'status-card stopped';
                indicator.className = 'status-indicator';
            }
        }
        
        function startServers() {
            try {
                addDebugLog('info', 'startServers() appelée', {});
                addLog('🚀 Démarrage des serveurs...');
                const startBtn = document.getElementById('start-btn');
                if (!startBtn) {
                    addDebugLog('error', 'Bouton start-btn non trouvé', {});
                    return;
                }
                startBtn.disabled = true;
                
                addDebugLog('info', 'Envoi requête POST /api/start', {});
                fetch('/api/start', { method: 'POST' })
                    .then(function(r) {
                        addDebugLog('info', 'Réponse reçue', { status: r.status, ok: r.ok });
                        if (!r.ok) {
                            throw new Error('Erreur HTTP: ' + r.status);
                        }
                        return r.json();
                    })
                    .then(function(data) {
                        addDebugLog('info', 'Données reçues', data);
                        addLog('📝 ' + (data.message || 'Démarrage initié'));
                        if (data.backend) addLog('Backend: ' + data.backend);
                        if (data.frontend) addLog('Frontend: ' + data.frontend);
                        
                        // Vérifier périodiquement
                        if (checkInterval) {
                            clearInterval(checkInterval);
                            addDebugLog('info', 'Interval précédent nettoyé', {});
                        }
                        addDebugLog('info', 'Démarrage vérification périodique', {});
                        checkInterval = setInterval(function() {
                            updateStatus();
                            const backendIndicator = document.getElementById('backend-indicator');
                            const frontendIndicator = document.getElementById('frontend-indicator');
                            if (backendIndicator && frontendIndicator &&
                                backendIndicator.classList.contains('running') &&
                                frontendIndicator.classList.contains('running')) {
                                clearInterval(checkInterval);
                                addLog('✅ Tous les serveurs sont démarrés!');
                                addDebugLog('info', 'Tous les serveurs démarrés', {});
                            }
                        }, 2000);
                    })
                    .catch(function(e) {
                        addDebugLog('error', 'Erreur dans startServers', {
                            message: e.message,
                            stack: e.stack,
                            error: e.toString()
                        });
                        addLog('❌ Erreur: ' + e.message);
                        console.error('Erreur détaillée:', e);
                        if (startBtn) {
                            startBtn.disabled = false;
                        }
                    });
            } catch (e) {
                addDebugLog('error', 'Exception dans startServers', {
                    message: e.message,
                    stack: e.stack,
                    error: e.toString()
                });
                console.error('Exception critique:', e);
            }
        }
        
        function stopServers() {
            addLog('🛑 Arrêt des serveurs...');
            fetch('/api/stop', { method: 'POST' })
                .then(function(r) {
                    if (!r.ok) {
                        throw new Error('Erreur HTTP: ' + r.status);
                    }
                    return r.json();
                })
                .then(function() {
                    addLog('✅ Serveurs arrêtés');
                    document.getElementById('start-btn').disabled = false;
                    document.getElementById('stop-btn').style.display = 'none';
                    document.getElementById('ready-message').style.display = 'none';
                    if (checkInterval) clearInterval(checkInterval);
                    setTimeout(updateStatus, 1000);
                })
                .catch(function(e) {
                    addLog('❌ Erreur lors de l'arrêt: ' + e.message);
                    console.error('Erreur:', e);
                });
        }
        
        function showReadyMessage() {
            const msg = document.getElementById('ready-message');
            const link1 = document.createElement('a');
            link1.href = 'http://localhost:3000';
            link1.target = '_blank';
            link1.textContent = '→ Ouvrir l' + String.fromCharCode(39) + 'application web';
            const link2 = document.createElement('a');
            link2.href = 'http://localhost:8000/docs';
            link2.target = '_blank';
            link2.textContent = '→ Voir la documentation API';
            msg.innerHTML = '<strong>✅ Application prête !</strong><br>';
            msg.appendChild(document.createElement('br'));
            msg.appendChild(link1);
            msg.appendChild(document.createElement('br'));
            msg.appendChild(link2);
            msg.style.display = 'block';
        }
        
        // Fonction pour exporter les logs de debug
        function exportDebugLogs() {
            const logsJson = JSON.stringify(debugLogs, null, 2);
            const blob = new Blob([logsJson], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'debug-logs-' + new Date().toISOString() + '.json';
            a.click();
            URL.revokeObjectURL(url);
        }
        
        // Ajouter un bouton pour exporter les logs (dans la console)
        console.log('%c🔍 Logs de debug disponibles', 'color: blue; font-weight: bold');
        console.log('Utilisez exportDebugLogs() dans la console pour exporter les logs');
        console.log('Utilisez getDebugLogs() dans la console pour voir les logs');
        window.exportDebugLogs = exportDebugLogs;
        window.getDebugLogs = function() { return debugLogs; };
        
        // Vérifier l'état toutes les 3 secondes
        addDebugLog('info', 'Initialisation de la page', {});
        updateStatus();
        setInterval(updateStatus, 3000);
    </script>
</body>
</html>"""

def find_free_port(start_port=8080):
    """Trouver un port libre"""
    for port in range(start_port, start_port + 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def check_if_already_running():
    """Vérifier si un serveur est déjà en cours d'exécution"""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:8080/api/status", method="GET")
        with urllib.request.urlopen(req, timeout=1) as response:
            return True
    except:
        return False

def main():
    log_debug('info', '=== Démarrage du serveur de démarrage ===')
    
    # Vérifier si un serveur est déjà en cours d'exécution
    if check_if_already_running():
        print("✅ Un serveur de démarrage est déjà en cours d'exécution !")
        print("📱 Ouvrez votre navigateur sur: http://localhost:8080")
        if sys.platform == "darwin":
            import subprocess
            subprocess.Popen(['open', 'http://localhost:8080'])
        return
    
    port = find_free_port(8080)
    
    if port is None:
        log_debug('error', 'Impossible de trouver un port libre')
        print("❌ Impossible de trouver un port libre")
        sys.exit(1)
    
    if port != 8080:
        log_debug('warn', f'Port 8080 occupé, utilisation du port {port}')
        print(f"⚠️  Le port 8080 est occupé, utilisation du port {port}")
    
    try:
        server = HTTPServer(("0.0.0.0", port), StartupHandler)
        log_debug('info', f'Serveur HTTP créé sur le port {port}')
        print(f"🚀 Serveur de démarrage accessible sur http://localhost:{port}")
        print(f"📱 Ouvrez votre navigateur et allez sur http://localhost:{port}")
        print(f"💡 Cliquez sur 'Démarrer l'Application' pour lancer tout automatiquement")
        print(f"\n💡 Appuyez sur Ctrl+C pour arrêter\n")
        print(f"📁 Logs détaillés: {log_file}")
        
        # Ouvrir automatiquement le navigateur sur macOS
        if sys.platform == "darwin":
            import subprocess
            subprocess.Popen(['open', f'http://localhost:{port}'])
        
        server.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            log_debug('error', f'Port {port} déjà utilisé')
            print(f"❌ Le port {port} est déjà utilisé.")
            print(f"💡 Un serveur est peut-être déjà en cours d'exécution.")
            print(f"💡 Essayez d'ouvrir http://localhost:{port} dans votre navigateur")
            print(f"💡 Ou arrêtez le processus avec: lsof -ti:{port} | xargs kill")
        else:
            log_debug('error', f'Erreur OSError: {e}')
            print(f"❌ Erreur: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        log_debug('info', 'Arrêt demandé par l\'utilisateur')
        print("\n🛑 Arrêt du serveur de démarrage...")
        for proc in processes.values():
            try:
                proc.terminate()
            except:
                pass
        server.shutdown()
    except Exception as e:
        log_debug('critical', 'Exception critique', {
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        print(f"❌ Erreur critique: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
