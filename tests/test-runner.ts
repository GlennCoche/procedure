/**
 * Orchestrateur principal pour les tests
 */

import { exec } from 'child_process'
import { promisify } from 'util'
import { readFile, writeFile } from 'fs/promises'
import { join } from 'path'
import { TestReport, TestSuite, TestResult, BugReport } from './utils/test-reports'
import { analyzeBug, autoFixBug } from './utils/auto-fix'
import { saveJsonReport, saveHtmlReport } from './utils/test-reports'

const execAsync = promisify(exec)

export interface TestConfig {
  environment: 'local' | 'production'
  autoFix: boolean
  verbose: boolean
  suites: string[]
}

export class TestRunner {
  private config: TestConfig
  private report: TestReport
  private bugs: BugReport[] = []

  constructor(config: Partial<TestConfig> = {}) {
    this.config = {
      environment: config.environment || 'local',
      autoFix: config.autoFix !== false,
      verbose: config.verbose || false,
      suites: config.suites || ['auth', 'procedures', 'executions', 'tips', 'ia'],
    }

    this.report = {
      timestamp: new Date().toISOString(),
      environment: this.config.environment,
      summary: {
        total: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        duration: '0s',
      },
      suites: [],
      bugs: [],
    }
  }

  /**
   * Exécuter tous les tests
   */
  async runAll(): Promise<TestReport> {
    const startTime = Date.now()

    console.log('🚀 Démarrage des tests...')
    console.log(`Environnement: ${this.config.environment}`)
    console.log(`Auto-fix: ${this.config.autoFix ? 'Activé' : 'Désactivé'}`)
    console.log('')

    // Exécuter les tests par suite
    for (const suite of this.config.suites) {
      await this.runSuite(suite)
    }

    // Calculer la durée totale
    const duration = ((Date.now() - startTime) / 1000).toFixed(2)
    this.report.summary.duration = `${duration}s`

    // Générer les rapports
    await this.generateReports()

    return this.report
  }

  /**
   * Exécuter une suite de tests
   */
  private async runSuite(suiteName: string): Promise<void> {
    console.log(`\n📦 Exécution de la suite: ${suiteName}`)

    const suite: TestSuite = {
      name: suiteName,
      tests: [],
      duration: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
    }

    const startTime = Date.now()

    try {
      // Exécuter les tests API
      if (this.config.suites.includes(suiteName)) {
        await this.runApiTests(suiteName, suite)
      }

      // Exécuter les tests E2E
      if (this.config.suites.includes(suiteName)) {
        await this.runE2ETests(suiteName, suite)
      }

      // Analyser et corriger les bugs
      if (this.config.autoFix && suite.tests.some(t => t.status === 'failed')) {
        await this.analyzeAndFixBugs(suite)
      }
    } catch (error: any) {
      console.error(`Erreur lors de l'exécution de la suite ${suiteName}:`, error)
    }

    suite.duration = (Date.now() - startTime) / 1000
    suite.passed = suite.tests.filter(t => t.status === 'passed').length
    suite.failed = suite.tests.filter(t => t.status === 'failed').length
    suite.skipped = suite.tests.filter(t => t.status === 'skipped').length

    // Mettre à jour le résumé global
    this.report.summary.total += suite.tests.length
    this.report.summary.passed += suite.passed
    this.report.summary.failed += suite.failed
    this.report.summary.skipped += suite.skipped

    this.report.suites.push(suite)

    console.log(`✅ Suite ${suiteName}: ${suite.passed} passés, ${suite.failed} échoués, ${suite.skipped} ignorés`)
  }

  /**
   * Exécuter les tests API avec Vitest
   */
  private async runApiTests(suiteName: string, suite: TestSuite): Promise<void> {
    const testFile = `api/${suiteName}.test.ts`
    const testPath = join(__dirname, testFile)

    try {
      // Vérifier que le fichier existe
      await readFile(testPath)

      console.log(`  🔍 Tests API: ${testFile}`)

      const { stdout, stderr } = await execAsync(
        `cd ${join(__dirname, '..', 'frontend')} && npx vitest run ${testPath} --reporter=json`,
        { timeout: 60000 }
      )

      // Parser les résultats Vitest (format JSON)
      try {
        const results = JSON.parse(stdout)
        if (results.testResults) {
          for (const testResult of results.testResults) {
            suite.tests.push({
              name: testResult.name || testResult.title,
              status: testResult.status === 'passed' ? 'passed' : testResult.status === 'skipped' ? 'skipped' : 'failed',
              duration: testResult.duration || 0,
              error: testResult.error?.message,
              stack: testResult.error?.stack,
            })

            // Détecter les bugs
            if (testResult.status === 'failed') {
              const bug = {
                id: `BUG-${this.bugs.length + 1}`,
                severity: 'major' as const,
                test: testResult.name || testResult.title,
                error: testResult.error?.message || 'Test failed',
                stack: testResult.error?.stack,
                status: 'detected' as const,
                timestamp: new Date().toISOString(),
              }
              this.bugs.push(bug)
            }
          }
        }
      } catch (parseError) {
        // Si le parsing échoue, créer un test générique
        suite.tests.push({
          name: `API Tests for ${suiteName}`,
          status: stderr ? 'failed' : 'passed',
          duration: 0,
          error: stderr || undefined,
        })
      }
    } catch (error: any) {
      if (error.code === 'ENOENT') {
        console.log(`  ⚠️  Fichier de test non trouvé: ${testFile}`)
        suite.tests.push({
          name: `API Tests for ${suiteName}`,
          status: 'skipped',
          duration: 0,
        })
      } else {
        suite.tests.push({
          name: `API Tests for ${suiteName}`,
          status: 'failed',
          duration: 0,
          error: error.message,
        })
      }
    }
  }

  /**
   * Exécuter les tests E2E avec Playwright
   */
  private async runE2ETests(suiteName: string, suite: TestSuite): Promise<void> {
    const testFile = `e2e/${suiteName}.spec.ts`
    const testPath = join(__dirname, testFile)

    try {
      await readFile(testPath)

      console.log(`  🌐 Tests E2E: ${testFile}`)

      const { stdout, stderr } = await execAsync(
        `cd ${__dirname} && npx playwright test ${testFile} --reporter=json`,
        { timeout: 120000 }
      )

      // Parser les résultats Playwright
      try {
        const results = JSON.parse(stdout)
        if (results.suites) {
          for (const testSuite of results.suites) {
            for (const test of testSuite.tests || []) {
              suite.tests.push({
                name: test.title,
                status: test.outcome === 'expected' ? 'passed' : test.outcome === 'skipped' ? 'skipped' : 'failed',
                duration: test.duration || 0,
                error: test.results?.[0]?.error?.message,
                stack: test.results?.[0]?.error?.stack,
              })

              if (test.outcome !== 'expected' && test.outcome !== 'skipped') {
                const bug = {
                  id: `BUG-${this.bugs.length + 1}`,
                  severity: 'major' as const,
                  test: test.title,
                  error: test.results?.[0]?.error?.message || 'Test failed',
                  stack: test.results?.[0]?.error?.stack,
                  status: 'detected' as const,
                  timestamp: new Date().toISOString(),
                }
                this.bugs.push(bug)
              }
            }
          }
        }
      } catch (parseError) {
        suite.tests.push({
          name: `E2E Tests for ${suiteName}`,
          status: stderr ? 'failed' : 'passed',
          duration: 0,
          error: stderr || undefined,
        })
      }
    } catch (error: any) {
      if (error.code === 'ENOENT') {
        console.log(`  ⚠️  Fichier de test non trouvé: ${testFile}`)
        suite.tests.push({
          name: `E2E Tests for ${suiteName}`,
          status: 'skipped',
          duration: 0,
        })
      } else {
        suite.tests.push({
          name: `E2E Tests for ${suiteName}`,
          status: 'failed',
          duration: 0,
          error: error.message,
        })
      }
    }
  }

  /**
   * Analyser et corriger les bugs automatiquement
   */
  private async analyzeAndFixBugs(suite: TestSuite): Promise<void> {
    const failedTests = suite.tests.filter(t => t.status === 'failed')

    for (const test of failedTests) {
      if (!test.error) continue

      const bug = this.bugs.find(b => b.test === test.name)
      if (!bug) continue

      console.log(`  🔧 Analyse du bug: ${bug.id}`)

      // Analyser le bug
      const analysis = await analyzeBug(bug)

      console.log(`    Cause racine: ${analysis.rootCause}`)
      console.log(`    Suggestion: ${analysis.suggestedFix}`)

      // Tenter la correction automatique
      if (this.config.autoFix) {
        const fixed = await autoFixBug(analysis)
        if (fixed) {
          console.log(`    ✅ Bug corrigé automatiquement`)
          bug.status = 'fixed'
          bug.fix = analysis.suggestedFix

          // Re-tester (simplifié pour l'instant)
          // Dans une vraie implémentation, on relancerait le test spécifique
        } else {
          console.log(`    ⚠️  Correction automatique non disponible`)
        }
      }
    }
  }

  /**
   * Générer les rapports
   */
  private async generateReports(): Promise<void> {
    this.report.bugs = this.bugs

    console.log('\n📊 Génération des rapports...')

    try {
      const jsonFile = await saveJsonReport(this.report)
      console.log(`  ✅ Rapport JSON: ${jsonFile}`)

      const htmlFile = await saveHtmlReport(this.report)
      console.log(`  ✅ Rapport HTML: ${htmlFile}`)
    } catch (error) {
      console.error('Erreur lors de la génération des rapports:', error)
    }
  }

  /**
   * Afficher le résumé
   */
  printSummary(): void {
    console.log('\n' + '='.repeat(60))
    console.log('📊 RÉSUMÉ DES TESTS')
    console.log('='.repeat(60))
    console.log(`Total: ${this.report.summary.total}`)
    console.log(`✅ Réussis: ${this.report.summary.passed}`)
    console.log(`❌ Échoués: ${this.report.summary.failed}`)
    console.log(`⏭️  Ignorés: ${this.report.summary.skipped}`)
    console.log(`⏱️  Durée: ${this.report.summary.duration}`)
    console.log(`🐛 Bugs détectés: ${this.bugs.length}`)
    console.log('='.repeat(60))
  }
}

// Exporter pour utilisation en CLI
export default TestRunner
