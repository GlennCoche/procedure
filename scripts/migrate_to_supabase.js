/**
 * Script de migration des données SQLite locales vers Supabase
 * Migre les procédures et tips validés vers la production
 */

const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

// Données des procédures extraites de SQLite
const procedures = [
  {
    title: "Installation et montage mural de l'onduleur ABB TRIO",
    description: "Procédure complète pour installer physiquement l'onduleur TRIO sur une paroi, incluant le positionnement de l'étrier et l'accouplement des composants.",
    category: "Installation",
    tags: ["ABB", "TRIO", "Montage", "Étrier", "Installation physique"],
    steps: [
      { order: 1, title: "Positionnement de l'étrier", description: "Positionner l'étrier sur la paroi parfaitement mise à niveau et l'utiliser comme gabarit de perçage" },
      { order: 2, title: "Perçage", description: "Effectuer les 10 trous nécessaires avec une perceuse (mèche 10mm, profondeur 70mm)" },
      { order: 3, title: "Fixation de l'étrier", description: "Fixer l'étrier à la paroi avec 10 chevilles de 10mm" },
      { order: 4, title: "Installation du boîtier de jonction", description: "Accrocher le boîtier de jonction en insérant la tête des vis arrière dans les rainures de l'étrier" },
      { order: 5, title: "Préparation du connecteur", description: "Dévisser les vis du connecteur et enlever le bouchon permettant d'accéder au connecteur" },
      { order: 6, title: "Installation de l'onduleur", description: "Accrocher l'onduleur à l'étrier en insérant la tête des vis arrière dans les rainures" },
      { order: 7, title: "Accouplement", description: "Serrer la vis d'accouplement en agissant sur la partie inférieure du boîtier de jonction" },
      { order: 8, title: "Finalisation", description: "Visser les deux vis du connecteur à l'intérieur du boîtier et la vis de blocage sur le côté inférieur" }
    ]
  },
  {
    title: "Configuration du standard de réseau ABB TRIO",
    description: "Procédure de configuration du standard de réseau électrique selon le pays d'installation via les interrupteurs rotatifs.",
    category: "Configuration",
    tags: ["ABB", "TRIO", "Standard réseau", "Pays", "Configuration"],
    steps: [
      { order: 1, title: "Vérification onduleur éteint", description: "S'assurer que l'onduleur est éteint avant d'agir sur les interrupteurs rotatifs" },
      { order: 2, title: "Localiser les interrupteurs", description: "Identifier les interrupteurs rotatifs a05 sur la carte de communication" },
      { order: 3, title: "Configuration France", description: "Pour la France (400V): positionner l'interrupteur 1 sur 0 et l'interrupteur 2 sur D" },
      { order: 4, title: "Vérification", description: "Vérifier que la configuration est correcte selon le tableau des standards pays" },
      { order: 5, title: "Sauvegarde", description: "Les configurations se verrouillent après 24 heures de fonctionnement" }
    ]
  },
  {
    title: "Connexion du générateur PV (côté DC) ABB TRIO",
    description: "Procédure de raccordement des chaînes photovoltaïques à l'entrée DC de l'onduleur TRIO.",
    category: "Installation",
    tags: ["ABB", "TRIO", "DC", "PV", "Chaînes", "MPPT"],
    steps: [
      { order: 1, title: "Contrôle de polarité", description: "Vérifier avec un voltmètre que la tension de chaque chaîne respecte la polarité correcte et reste dans les limites (max 1000V)" },
      { order: 2, title: "Contrôle d'isolation", description: "Mesurer la tension entre chaque pôle et la terre - aucune tension ne doit être détectée" },
      { order: 3, title: "Configuration MPPT", description: "Choisir entre MPPT indépendants ou parallèles selon la configuration du générateur PV" },
      { order: 4, title: "Installation des cavaliers", description: "Installer les cavaliers si configuration MPPT parallèle, les retirer si indépendants" },
      { order: 5, title: "Connexion des chaînes", description: "Raccorder les chaînes via connecteurs rapides (S2F/S2X) ou bornier d'entrée DC (Base/S2)" },
      { order: 6, title: "Vérification des connexions", description: "Vérifier la tenue des connecteurs et installer les bouchons sur les entrées non utilisées" }
    ]
  },
  {
    title: "Mise en service de l'onduleur ABB TRIO",
    description: "Procédure de démarrage et mise en service de l'onduleur TRIO après installation complète.",
    category: "Mise en service",
    tags: ["ABB", "TRIO", "Démarrage", "Mise en service", "Connexion réseau"],
    steps: [
      { order: 1, title: "Armement du sectionneur", description: "Mettre le sectionneur AC+DC sur ON (armer d'abord AC, puis DC si séparés)" },
      { order: 2, title: "Contrôle tension d'entrée", description: "Vérifier que la tension d'entrée dépasse la Vstart (icône b14 s'allume)" },
      { order: 3, title: "Contrôle paramètres réseau", description: "L'onduleur vérifie la tension de réseau (icône b22 fixe si OK)" },
      { order: 4, title: "Phase DC-DC", description: "L'icône b17 clignote puis reste allumée (booster en fonctionnement)" },
      { order: 5, title: "Phase DC-AC", description: "L'icône b18 s'allume (onduleur en fonctionnement)" },
      { order: 6, title: "Connexion réseau", description: "Les icônes b21 s'allument en séquence jusqu'à connexion complète" },
      { order: 7, title: "Confirmation", description: "Un bip sonore et la LED verte allumée confirment le bon fonctionnement" }
    ]
  }
];

// Données des tips extraites de SQLite
const tips = [
  {
    title: "Distances minimales d'installation ABB TRIO",
    content: "Respecter les distances minimales autour de l'onduleur: 50cm sur les côtés et au-dessus, 80cm en-dessous. Ne pas exposer à la lumière directe du soleil pour éviter le derating de puissance.",
    category: "Installation",
    tags: ["ABB", "TRIO", "Distances", "Ventilation"]
  },
  {
    title: "Protection différentielle pour ABB TRIO",
    content: "Les onduleurs ABB Aurora sont équipés d'une protection différentielle intégrée (300mA/300ms). Il n'est PAS nécessaire d'installer un interrupteur différentiel de type B. Utiliser un type AC avec 300mA.",
    category: "Sécurité",
    tags: ["ABB", "TRIO", "Différentiel", "Protection"]
  },
  {
    title: "Résistance de terminaison RS485",
    content: "Activer la résistance de terminaison (120Ω) UNIQUEMENT sur le dernier onduleur de la chaîne RS485. Interrupteur a12 pour PMU, a13 pour PC. Ne pas dépasser 1000m de longueur de ligne.",
    category: "Communication",
    tags: ["ABB", "TRIO", "RS485", "Terminaison"]
  },
  {
    title: "Erreur Riso Low - Diagnostic ABB TRIO",
    content: "Si l'erreur E025 (Riso Low) apparaît: mesurer la résistance d'isolation avec un mégohmètre entre les pôles court-circuités et la terre. Si < 1MΩ, vérifier les panneaux, boîtiers de raccordement, parafoudres ou présence d'humidité.",
    category: "Dépannage",
    tags: ["ABB", "TRIO", "Riso", "Isolation", "Erreur"]
  }
];

async function migrateProcedures() {
  console.log('\n📋 Migration des procédures...');
  const createdProcedures = [];

  for (const proc of procedures) {
    try {
      const created = await prisma.procedure.create({
        data: {
          title: proc.title,
          description: proc.description,
          category: proc.category,
          tags: JSON.stringify(proc.tags),
          isActive: true,
          createdById: 1, // Admin user ID
          steps: {
            create: proc.steps.map(step => ({
              order: step.order,
              title: step.title,
              description: step.description,
              instructions: step.description,
              validationType: 'manual'
            }))
          }
        },
        include: {
          steps: true
        }
      });
      
      console.log(`  ✅ Procédure créée: "${created.title}" (ID: ${created.id}, ${created.steps.length} étapes)`);
      createdProcedures.push(created);
    } catch (error) {
      console.error(`  ❌ Erreur pour "${proc.title}":`, error.message);
    }
  }

  return createdProcedures;
}

async function migrateTips() {
  console.log('\n💡 Migration des tips...');
  const createdTips = [];

  for (const tip of tips) {
    try {
      const created = await prisma.tip.create({
        data: {
          title: tip.title,
          content: tip.content,
          category: tip.category,
          tags: JSON.stringify(tip.tags),
          createdById: 1 // Admin user ID
        }
      });
      
      console.log(`  ✅ Tip créé: "${created.title}" (ID: ${created.id})`);
      createdTips.push(created);
    } catch (error) {
      console.error(`  ❌ Erreur pour "${tip.title}":`, error.message);
    }
  }

  return createdTips;
}

async function main() {
  console.log('🚀 Démarrage de la migration vers Supabase...');
  console.log('━'.repeat(50));

  try {
    // Vérifier la connexion
    await prisma.$connect();
    console.log('✅ Connexion Supabase établie');

    // Migrer les procédures
    const procs = await migrateProcedures();
    
    // Migrer les tips
    const tipsList = await migrateTips();

    console.log('\n' + '━'.repeat(50));
    console.log('📊 Résumé de la migration:');
    console.log(`   - Procédures créées: ${procs.length}`);
    console.log(`   - Tips créés: ${tipsList.length}`);
    console.log('\n✅ Migration terminée avec succès!');
    console.log('👉 Vérifiez sur https://procedure1.vercel.app/');

  } catch (error) {
    console.error('❌ Erreur de migration:', error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

main();
