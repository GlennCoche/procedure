"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle2, XCircle, Loader2, Play, Square } from "lucide-react"

interface ServerStatus {
  backend: {
    running: boolean
    url: string
  }
  frontend: {
    running: boolean
    url: string
  }
}

export default function StartupPage() {
  const [status, setStatus] = useState<ServerStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [logs, setLogs] = useState<string[]>([])

  const checkStatus = async () => {
    try {
      // En production, utiliser les API routes Next.js
      const isProduction = typeof window !== 'undefined' && !window.location.hostname.includes('localhost')
      const apiUrl = isProduction 
        ? '/api/startup/status' 
        : 'http://localhost:8000/api/startup/status'
      
      const response = await fetch(apiUrl)
      if (!response.ok) {
        // Si l'API route n'existe pas, vérifier les services Next.js directement
        if (isProduction) {
          const [proceduresRes, authRes] = await Promise.allSettled([
            fetch('/api/procedures'),
            fetch('/api/auth/me')
          ])
          
          setStatus({
            backend: {
              running: proceduresRes.status === 'fulfilled' && proceduresRes.value.ok,
              url: window.location.origin
            },
            frontend: {
              running: authRes.status === 'fulfilled' && authRes.value.ok,
              url: window.location.origin
            }
          })
          return
        }
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setStatus(data)
    } catch (error) {
      console.error("Erreur lors de la vérification:", error)
      // En production, essayer de vérifier directement les API routes
      if (typeof window !== 'undefined' && !window.location.hostname.includes('localhost')) {
        try {
          const [proceduresRes, authRes] = await Promise.allSettled([
            fetch('/api/procedures'),
            fetch('/api/auth/me')
          ])
          
          setStatus({
            backend: {
              running: proceduresRes.status === 'fulfilled' && proceduresRes.value.ok,
              url: window.location.origin
            },
            frontend: {
              running: authRes.status === 'fulfilled' && authRes.value.ok,
              url: window.location.origin
            }
          })
        } catch (e) {
          console.error("Erreur lors de la vérification directe:", e)
        }
      }
    }
  }

  const startServers = async () => {
    setLoading(true)
    setLogs([...logs, "🚀 Vérification des services..."])
    
    try {
      const isProduction = typeof window !== 'undefined' && !window.location.hostname.includes('localhost')
      
      if (isProduction) {
        // En production, les services Next.js sont déjà démarrés
        setLogs([...logs, "✅ Services Next.js actifs"])
        await checkStatus()
        setLoading(false)
        return
      }
      
      // En développement, essayer de démarrer le backend FastAPI
      const response = await fetch("http://localhost:8000/api/startup/start", {
        method: "POST",
      })
      const data = await response.json()
      
      setLogs([...logs, `📝 ${data.message}`])
      
      // Vérifier périodiquement l'état
      const interval = setInterval(async () => {
        await checkStatus()
        if (status?.backend.running && status?.frontend.running) {
          clearInterval(interval)
          setLoading(false)
          setLogs([...logs, "✅ Tous les serveurs sont démarrés!"])
        }
      }, 2000)
      
      setTimeout(() => clearInterval(interval), 60000) // Timeout après 1 minute
    } catch (error) {
      setLogs([...logs, `❌ Erreur: ${error}`])
      setLoading(false)
    }
  }

  const stopServers = async () => {
    setLoading(true)
    setLogs([...logs, "🛑 Arrêt des serveurs..."])
    
    try {
      const isProduction = typeof window !== 'undefined' && !window.location.hostname.includes('localhost')
      
      if (isProduction) {
        setLogs([...logs, "ℹ️ En production, les services Next.js ne peuvent pas être arrêtés depuis cette page"])
        setLoading(false)
        return
      }
      
      await fetch("http://localhost:8000/api/startup/stop", {
        method: "POST",
      })
      setLogs([...logs, "✅ Serveurs arrêtés"])
      await checkStatus()
    } catch (error) {
      setLogs([...logs, `❌ Erreur: ${error}`])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkStatus()
    const interval = setInterval(checkStatus, 3000)
    return () => clearInterval(interval)
  }, [])

  const allRunning = status?.backend.running && status?.frontend.running

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
            Système de Procédures
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Panneau de contrôle - Démarrage automatique
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>État des Serveurs</CardTitle>
            <CardDescription>
              Vérification automatique de l'état des services
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-semibold">Backend API</p>
                  <p className="text-sm text-muted-foreground">
                    {status?.backend.url}
                  </p>
                </div>
                {status?.backend.running ? (
                  <CheckCircle2 className="h-6 w-6 text-green-500" />
                ) : (
                  <XCircle className="h-6 w-6 text-red-500" />
                )}
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-semibold">Frontend Web</p>
                  <p className="text-sm text-muted-foreground">
                    {status?.frontend.url}
                  </p>
                </div>
                {status?.frontend.running ? (
                  <CheckCircle2 className="h-6 w-6 text-green-500" />
                ) : (
                  <XCircle className="h-6 w-6 text-red-500" />
                )}
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={startServers}
                disabled={loading || allRunning}
                className="flex-1"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Démarrage...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Démarrer l'Application
                  </>
                )}
              </Button>
              {allRunning && (
                <Button
                  onClick={stopServers}
                  variant="destructive"
                  size="lg"
                >
                  <Square className="h-4 w-4 mr-2" />
                  Arrêter
                </Button>
              )}
            </div>

            {allRunning && (
              <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <div className="flex items-center gap-2 text-green-700 dark:text-green-400">
                  <CheckCircle2 className="h-5 w-5" />
                  <p className="font-semibold">Application prête !</p>
                </div>
                <div className="mt-2 space-y-1">
                  <a
                    href={status?.frontend.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-sm text-green-600 dark:text-green-400 hover:underline"
                  >
                    → Ouvrir l'application web
                  </a>
                  <a
                    href={`${status?.backend.url}/docs`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-sm text-green-600 dark:text-green-400 hover:underline"
                  >
                    → Voir la documentation API
                  </a>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {logs.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Journal d'activité</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1 max-h-60 overflow-y-auto font-mono text-sm">
                {logs.map((log, idx) => (
                  <div key={idx} className="text-gray-700 dark:text-gray-300">
                    {log}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
