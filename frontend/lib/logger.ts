/**
 * Système de logging détaillé pour le frontend
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'critical'

interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
  data?: any
  stack?: string
  component?: string
  function?: string
}

class FrontendLogger {
  private logs: LogEntry[] = []
  private maxLogs = 1000
  private logToConsole = true
  private logToServer = false

  private formatMessage(level: LogLevel, message: string, data?: any, component?: string, func?: string): LogEntry {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      component,
      function: func,
    }

    if (data) {
      entry.data = data
    }

    if (level === 'error' || level === 'critical') {
      entry.stack = new Error().stack
    }

    return entry
  }

  private addLog(entry: LogEntry) {
    this.logs.push(entry)
    
    // Limiter le nombre de logs
    if (this.logs.length > this.maxLogs) {
      this.logs.shift()
    }

    // Logger dans la console
    if (this.logToConsole) {
      const consoleMethod = entry.level === 'debug' ? 'log' 
                          : entry.level === 'critical' ? 'error' 
                          : entry.level
      const prefix = `[${entry.timestamp}] [${entry.level.toUpperCase()}]`
      if (entry.component) {
        console[consoleMethod](`${prefix} [${entry.component}]`, entry.message, entry.data || '')
      } else {
        console[consoleMethod](`${prefix}`, entry.message, entry.data || '')
      }
    }

    // Envoyer au serveur si activé
    if (this.logToServer && (entry.level === 'error' || entry.level === 'critical')) {
      this.sendToServer(entry)
    }
  }

  private async sendToServer(entry: LogEntry) {
    try {
      await fetch('/api/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry),
      })
    } catch (error) {
      // Ne pas logger l'erreur de logging pour éviter les boucles
    }
  }

  debug(message: string, data?: any, component?: string, func?: string) {
    this.addLog(this.formatMessage('debug', message, data, component, func))
  }

  info(message: string, data?: any, component?: string, func?: string) {
    this.addLog(this.formatMessage('info', message, data, component, func))
  }

  warn(message: string, data?: any, component?: string, func?: string) {
    this.addLog(this.formatMessage('warn', message, data, component, func))
  }

  error(message: string, error?: Error | any, component?: string, func?: string) {
    this.addLog(this.formatMessage('error', message, error, component, func))
  }

  critical(message: string, error?: Error | any, component?: string, func?: string) {
    this.addLog(this.formatMessage('critical', message, error, component, func))
  }

  getLogs(level?: LogLevel, limit: number = 100): LogEntry[] {
    let filtered = this.logs
    if (level) {
      filtered = this.logs.filter(log => log.level === level)
    }
    return filtered.slice(-limit)
  }

  clearLogs() {
    this.logs = []
  }

  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2)
  }

  enableServerLogging() {
    this.logToServer = true
  }

  disableServerLogging() {
    this.logToServer = false
  }
}

export const logger = new FrontendLogger()

// Logger automatique des erreurs globales
if (typeof window !== 'undefined') {
  window.addEventListener('error', (event) => {
    logger.error('Erreur JavaScript globale', {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    }, 'Global', 'window.onerror')
  })

  window.addEventListener('unhandledrejection', (event) => {
    logger.error('Promesse rejetée non gérée', {
      reason: event.reason,
    }, 'Global', 'unhandledrejection')
  })
}
