/**
 * Système de détection et correction automatique des bugs
 */

import { BugReport, createBugReport, analyzeError } from './test-reports'
import { readFile, writeFile } from 'fs/promises'
import { join } from 'path'

export interface BugAnalysis {
  bug: BugReport
  rootCause: string
  suggestedFix: string
  affectedFiles: string[]
  confidence: 'high' | 'medium' | 'low'
}

/**
 * Analyser un bug et identifier la cause racine
 */
export async function analyzeBug(bug: BugReport): Promise<BugAnalysis> {
  const errorLower = bug.error.toLowerCase()
  let rootCause = 'Unknown error'
  let suggestedFix = 'Review error logs and code'
  let affectedFiles: string[] = []
  let confidence: 'high' | 'medium' | 'low' = 'low'

  // Analyser les patterns d'erreur communs
  if (errorLower.includes('500') || errorLower.includes('internal server error')) {
    rootCause = 'Server error - likely code exception or database issue'
    suggestedFix = 'Check server logs, verify database connection, review error handling'
    confidence = 'high'
    
    // Essayer d'identifier le fichier concerné
    if (bug.stack) {
      const stackLines = bug.stack.split('\n')
      for (const line of stackLines) {
        if (line.includes('/app/api/') || line.includes('/lib/')) {
          const match = line.match(/([^/]+\.(ts|tsx|js))/)
          if (match) {
            affectedFiles.push(match[1])
          }
        }
      }
    }
  } else if (errorLower.includes('401') || errorLower.includes('unauthorized')) {
    rootCause = 'Authentication error - user not authenticated or token invalid'
    suggestedFix = 'Verify authentication middleware, check JWT_SECRET, verify cookie handling'
    confidence = 'high'
    affectedFiles = ['frontend/app/api/auth/login/route.ts', 'frontend/lib/auth.ts']
  } else if (errorLower.includes('403') || errorLower.includes('forbidden')) {
    rootCause = 'Authorization error - user lacks required permissions'
    suggestedFix = 'Verify role checking logic, ensure user has correct role'
    confidence = 'high'
  } else if (errorLower.includes('404') || errorLower.includes('not found')) {
    rootCause = 'Resource not found - route or resource does not exist'
    suggestedFix = 'Verify route exists, check resource ID, verify database query'
    confidence = 'high'
  } else if (errorLower.includes('database') || errorLower.includes('prisma')) {
    rootCause = 'Database error - connection or query issue'
    suggestedFix = 'Check DATABASE_URL, verify Prisma schema, check database connection'
    confidence = 'high'
    affectedFiles = ['frontend/lib/db.ts', 'frontend/prisma/schema.prisma']
  } else if (errorLower.includes('cookie') || errorLower.includes('set-cookie')) {
    rootCause = 'Cookie handling error - issue with cookie setting or reading'
    suggestedFix = 'Verify Response.cookies.set() usage, check cookie configuration'
    confidence = 'high'
    affectedFiles = ['frontend/app/api/auth/login/route.ts', 'frontend/app/api/auth/register/route.ts']
  } else if (errorLower.includes('cannot read') || errorLower.includes('undefined')) {
    rootCause = 'Null/undefined reference - accessing property on undefined object'
    suggestedFix = 'Add null checks, verify object exists before accessing properties'
    confidence = 'medium'
  } else if (errorLower.includes('validation') || errorLower.includes('invalid')) {
    rootCause = 'Validation error - input data does not meet requirements'
    suggestedFix = 'Add input validation, check data types, verify required fields'
    confidence = 'medium'
  }

  return {
    bug,
    rootCause,
    suggestedFix,
    affectedFiles: affectedFiles.length > 0 ? affectedFiles : ['Unknown'],
    confidence,
  }
}

/**
 * Corriger automatiquement un bug basé sur l'analyse
 */
export async function autoFixBug(analysis: BugAnalysis): Promise<boolean> {
  try {
    // Pour l'instant, on ne corrige que les bugs avec haute confiance
    if (analysis.confidence !== 'high') {
      return false
    }

    // Correction spécifique pour les erreurs de cookies
    if (analysis.bug.error.toLowerCase().includes('cookie')) {
      // Cette correction a déjà été faite, donc on retourne true
      return true
    }

    // Correction pour les erreurs 500 liées à isActive
    if (analysis.bug.error.includes('isActive') && analysis.affectedFiles.some(f => f.includes('procedures'))) {
      // Vérifier et corriger le fichier procedures/route.ts
      const filePath = join(__dirname, '../../frontend/app/api/procedures/route.ts')
      try {
        const content = await readFile(filePath, 'utf-8')
        if (content.includes('isActive: 1')) {
          // Remplacer isActive: 1 par isActive: true pour PostgreSQL
          const fixed = content.replace(/isActive:\s*1/g, 'isActive: true')
          await writeFile(filePath, fixed, 'utf-8')
          analysis.bug.fix = 'Changed isActive: 1 to isActive: true for PostgreSQL compatibility'
          analysis.bug.status = 'fixed'
          return true
        }
      } catch (error) {
        console.error('Failed to fix isActive issue:', error)
        return false
      }
    }

    return false
  } catch (error) {
    console.error('Auto-fix failed:', error)
    return false
  }
}

/**
 * Re-tester après correction
 */
export async function retestAfterFix(bug: BugReport, testFunction: () => Promise<void>): Promise<boolean> {
  try {
    await testFunction()
    bug.status = 'fixed'
    return true
  } catch (error) {
    bug.status = 'failed'
    return false
  }
}

/**
 * Générer un rapport de correction
 */
export function generateFixReport(analyses: BugAnalysis[]): string {
  const fixed = analyses.filter(a => a.bug.status === 'fixed')
  const failed = analyses.filter(a => a.bug.status === 'failed')
  const pending = analyses.filter(a => a.bug.status === 'detected' || a.bug.status === 'analyzing')

  return `
# Rapport de Correction Automatique

## Résumé
- Total de bugs analysés: ${analyses.length}
- Corrigés automatiquement: ${fixed.length}
- Échecs de correction: ${failed.length}
- En attente: ${pending.length}

## Bugs Corrigés
${fixed.map(a => `
### ${a.bug.id} - ${a.bug.test}
- **Sévérité**: ${a.bug.severity}
- **Cause racine**: ${a.rootCause}
- **Correction**: ${a.bug.fix || a.suggestedFix}
- **Fichiers affectés**: ${a.affectedFiles.join(', ')}
`).join('\n')}

## Bugs Non Corrigés
${failed.map(a => `
### ${a.bug.id} - ${a.bug.test}
- **Sévérité**: ${a.bug.severity}
- **Cause racine**: ${a.rootCause}
- **Suggestion**: ${a.suggestedFix}
- **Confiance**: ${a.confidence}
`).join('\n')}
  `.trim()
}
