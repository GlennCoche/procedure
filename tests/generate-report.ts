#!/usr/bin/env node

/**
 * Script pour générer un rapport à partir des résultats existants
 */

import { readdir, readFile } from 'fs/promises'
import { join } from 'path'
import { saveHtmlReport, TestReport } from './utils/test-reports'

async function generateReportFromLatest(): Promise<void> {
  const reportsDir = join(__dirname, 'reports')
  
  try {
    // Lister tous les fichiers JSON de rapport
    const files = await readdir(reportsDir)
    const jsonReports = files
      .filter(f => f.startsWith('test-report-') && f.endsWith('.json'))
      .sort()
      .reverse() // Le plus récent en premier
    
    if (jsonReports.length === 0) {
      console.log('❌ Aucun rapport JSON trouvé dans tests/reports/')
      console.log('💡 Exécutez d\'abord les tests avec: npm run test')
      process.exit(1)
    }
    
    // Lire le rapport le plus récent
    const latestReport = jsonReports[0]
    console.log(`📄 Lecture du rapport: ${latestReport}`)
    
    const reportPath = join(reportsDir, latestReport)
    const reportContent = await readFile(reportPath, 'utf-8')
    const report: TestReport = JSON.parse(reportContent)
    
    // Générer le rapport HTML
    console.log('📊 Génération du rapport HTML...')
    const htmlFile = await saveHtmlReport(report)
    
    console.log(`✅ Rapport HTML généré: ${htmlFile}`)
    console.log(`\n📊 Résumé:`)
    console.log(`   Total: ${report.summary.total}`)
    console.log(`   ✅ Réussis: ${report.summary.passed}`)
    console.log(`   ❌ Échoués: ${report.summary.failed}`)
    console.log(`   ⏭️  Ignorés: ${report.summary.skipped}`)
    console.log(`   ⏱️  Durée: ${report.summary.duration}`)
    console.log(`   🐛 Bugs: ${report.bugs.length}`)
    
  } catch (error: any) {
    console.error('❌ Erreur lors de la génération du rapport:', error.message)
    process.exit(1)
  }
}

// Exécuter si appelé directement
if (require.main === module) {
  generateReportFromLatest()
}

export default generateReportFromLatest
