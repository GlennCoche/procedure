/**
 * Système de génération de rapports de tests
 */

export interface TestResult {
  name: string
  status: 'passed' | 'failed' | 'skipped'
  duration: number
  error?: string
  stack?: string
}

export interface TestSuite {
  name: string
  tests: TestResult[]
  duration: number
  passed: number
  failed: number
  skipped: number
}

export interface BugReport {
  id: string
  severity: 'critical' | 'major' | 'minor'
  test: string
  error: string
  stack?: string
  fix?: string
  status: 'detected' | 'analyzing' | 'fixed' | 'failed'
  timestamp: string
}

export interface TestReport {
  timestamp: string
  environment: 'local' | 'production'
  summary: {
    total: number
    passed: number
    failed: number
    skipped: number
    duration: string
  }
  suites: TestSuite[]
  bugs: BugReport[]
}

/**
 * Générer un ID unique pour un bug
 */
let bugCounter = 1
export function generateBugId(): string {
  return `BUG-${String(bugCounter++).padStart(3, '0')}`
}

/**
 * Analyser une erreur et déterminer sa sévérité
 */
export function analyzeError(error: string, testName: string): BugReport['severity'] {
  const errorLower = error.toLowerCase()
  
  // Erreurs critiques
  if (
    errorLower.includes('500') ||
    errorLower.includes('database') ||
    errorLower.includes('connection') ||
    errorLower.includes('cannot read property') ||
    errorLower.includes('undefined')
  ) {
    return 'critical'
  }
  
  // Erreurs majeures
  if (
    errorLower.includes('401') ||
    errorLower.includes('403') ||
    errorLower.includes('404') ||
    errorLower.includes('validation') ||
    errorLower.includes('permission')
  ) {
    return 'major'
  }
  
  // Erreurs mineures
  return 'minor'
}

/**
 * Créer un rapport de bug
 */
export function createBugReport(
  test: string,
  error: string,
  stack?: string
): BugReport {
  return {
    id: generateBugId(),
    severity: analyzeError(error, test),
    test,
    error,
    stack,
    status: 'detected',
    timestamp: new Date().toISOString(),
  }
}

/**
 * Générer un rapport JSON
 */
export function generateJsonReport(report: TestReport): string {
  return JSON.stringify(report, null, 2)
}

/**
 * Sauvegarder un rapport JSON
 */
import { writeFile, mkdir } from 'fs/promises'
import { join } from 'path'

export async function saveJsonReport(report: TestReport, filename?: string): Promise<string> {
  const reportsDir = join(__dirname, '../reports')
  await mkdir(reportsDir, { recursive: true })
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const reportFile = filename || join(reportsDir, `test-report-${timestamp}.json`)
  
  await writeFile(reportFile, generateJsonReport(report), 'utf-8')
  return reportFile
}

/**
 * Générer un rapport HTML
 */
export function generateHtmlReport(report: TestReport): string {
  const passedPercentage = (report.summary.passed / report.summary.total * 100).toFixed(1)
  const failedPercentage = (report.summary.failed / report.summary.total * 100).toFixed(1)
  
  return `
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rapport de Tests - ${report.timestamp}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; background: #f5f5f5; }
    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { color: #333; margin-bottom: 20px; }
    .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
    .stat-card { padding: 20px; border-radius: 8px; text-align: center; }
    .stat-card.total { background: #e3f2fd; }
    .stat-card.passed { background: #e8f5e9; }
    .stat-card.failed { background: #ffebee; }
    .stat-card.skipped { background: #fff3e0; }
    .stat-value { font-size: 32px; font-weight: bold; margin-bottom: 5px; }
    .stat-label { color: #666; font-size: 14px; }
    .suite { margin-bottom: 30px; border: 1px solid #ddd; border-radius: 8px; padding: 20px; }
    .suite-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .suite-name { font-size: 20px; font-weight: bold; }
    .test { padding: 10px; margin: 5px 0; border-radius: 4px; }
    .test.passed { background: #e8f5e9; }
    .test.failed { background: #ffebee; }
    .test.skipped { background: #fff3e0; }
    .test-name { font-weight: 500; }
    .test-error { margin-top: 5px; color: #c62828; font-size: 12px; font-family: monospace; }
    .bugs { margin-top: 30px; }
    .bug { padding: 15px; margin: 10px 0; border-left: 4px solid; border-radius: 4px; }
    .bug.critical { border-color: #c62828; background: #ffebee; }
    .bug.major { border-color: #f57c00; background: #fff3e0; }
    .bug.minor { border-color: #1976d2; background: #e3f2fd; }
    .bug-id { font-weight: bold; margin-bottom: 5px; }
    .bug-status { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px; }
    .bug-status.detected { background: #ffebee; }
    .bug-status.fixed { background: #e8f5e9; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Rapport de Tests</h1>
    <p><strong>Environnement:</strong> ${report.environment}</p>
    <p><strong>Date:</strong> ${new Date(report.timestamp).toLocaleString('fr-FR')}</p>
    
    <div class="summary">
      <div class="stat-card total">
        <div class="stat-value">${report.summary.total}</div>
        <div class="stat-label">Total</div>
      </div>
      <div class="stat-card passed">
        <div class="stat-value">${report.summary.passed}</div>
        <div class="stat-label">Réussis (${passedPercentage}%)</div>
      </div>
      <div class="stat-card failed">
        <div class="stat-value">${report.summary.failed}</div>
        <div class="stat-label">Échoués (${failedPercentage}%)</div>
      </div>
      <div class="stat-card skipped">
        <div class="stat-value">${report.summary.skipped}</div>
        <div class="stat-label">Ignorés</div>
      </div>
    </div>
    
    ${report.suites.map(suite => `
      <div class="suite">
        <div class="suite-header">
          <div class="suite-name">${suite.name}</div>
          <div>${suite.passed} passés, ${suite.failed} échoués, ${suite.skipped} ignorés</div>
        </div>
        ${suite.tests.map(test => `
          <div class="test ${test.status}">
            <div class="test-name">${test.name}</div>
            ${test.error ? `<div class="test-error">${test.error}</div>` : ''}
          </div>
        `).join('')}
      </div>
    `).join('')}
    
    ${report.bugs.length > 0 ? `
      <div class="bugs">
        <h2>Bugs Détectés (${report.bugs.length})</h2>
        ${report.bugs.map(bug => `
          <div class="bug ${bug.severity}">
            <div class="bug-id">
              ${bug.id} - ${bug.test}
              <span class="bug-status ${bug.status}">${bug.status}</span>
            </div>
            <div><strong>Sévérité:</strong> ${bug.severity}</div>
            <div><strong>Erreur:</strong> ${bug.error}</div>
            ${bug.fix ? `<div><strong>Correction:</strong> ${bug.fix}</div>` : ''}
          </div>
        `).join('')}
      </div>
    ` : ''}
  </div>
</body>
</html>
  `.trim()
}

/**
 * Sauvegarder un rapport HTML
 */
export async function saveHtmlReport(report: TestReport, filename?: string): Promise<string> {
  const reportsDir = join(__dirname, '../reports')
  await mkdir(reportsDir, { recursive: true })
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const reportFile = filename || join(reportsDir, `test-report-${timestamp}.html`)
  
  await writeFile(reportFile, generateHtmlReport(report), 'utf-8')
  return reportFile
}
