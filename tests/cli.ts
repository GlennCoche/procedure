#!/usr/bin/env node

/**
 * CLI interactif pour lancer les tests
 */

import TestRunner from './test-runner'
import { readFile } from 'fs/promises'
import { join } from 'path'

const args = process.argv.slice(2)

interface CLIOptions {
  environment?: 'local' | 'production'
  autoFix?: boolean
  verbose?: boolean
  suite?: string
  help?: boolean
}

function parseArgs(): CLIOptions {
  const options: CLIOptions = {}

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]
    
    if (arg === '--env' || arg === '-e') {
      options.environment = args[++i] as 'local' | 'production'
    } else if (arg === '--no-fix') {
      options.autoFix = false
    } else if (arg === '--fix') {
      options.autoFix = true
    } else if (arg === '--verbose' || arg === '-v') {
      options.verbose = true
    } else if (arg === '--suite' || arg === '-s') {
      options.suite = args[++i]
    } else if (arg === '--help' || arg === '-h') {
      options.help = true
    }
  }

  return options
}

function printHelp() {
  console.log(`
Usage: npm run test [options]

Options:
  --env, -e <local|production>  Environnement de test (défaut: local)
  --fix                          Activer la correction automatique (défaut: activé)
  --no-fix                       Désactiver la correction automatique
  --verbose, -v                  Mode verbeux
  --suite, -s <name>             Exécuter une suite spécifique (auth, procedures, executions, tips, ia)
  --help, -h                     Afficher cette aide

Exemples:
  npm run test                    # Lancer tous les tests en local
  npm run test -- --env production # Lancer tous les tests en production
  npm run test -- --suite auth    # Lancer uniquement les tests d'authentification
  npm run test -- --no-fix        # Lancer sans correction automatique
  `)
}

async function main() {
  const options = parseArgs()

  if (options.help) {
    printHelp()
    process.exit(0)
  }

  // Déterminer les suites à exécuter
  const suites = options.suite 
    ? [options.suite]
    : ['auth', 'procedures', 'executions', 'tips', 'ia']

  // Créer le runner
  const runner = new TestRunner({
    environment: options.environment || 'local',
    autoFix: options.autoFix !== false,
    verbose: options.verbose || false,
    suites,
  })

  try {
    // Exécuter les tests
    const report = await runner.runAll()

    // Afficher le résumé
    runner.printSummary()

    // Code de sortie basé sur les résultats
    if (report.summary.failed > 0) {
      console.log('\n❌ Certains tests ont échoué')
      process.exit(1)
    } else {
      console.log('\n✅ Tous les tests sont passés!')
      process.exit(0)
    }
  } catch (error: any) {
    console.error('\n❌ Erreur lors de l\'exécution des tests:', error)
    process.exit(1)
  }
}

// Exécuter si appelé directement
if (require.main === module) {
  main()
}

export default main
