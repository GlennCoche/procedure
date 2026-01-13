#!/usr/bin/env node

// Script pour générer le hash bcrypt d'un mot de passe
// Usage: node scripts/generate-password-hash.js [password]

const password = process.argv[2] || 'AdminSecure123!';

// Essayer d'utiliser bcryptjs (plus léger que bcrypt)
try {
  const bcrypt = require('bcryptjs');
  
  bcrypt.hash(password, 10, (err, hash) => {
    if (err) {
      console.error('Erreur:', err);
      process.exit(1);
    }
    console.log('Mot de passe:', password);
    console.log('Hash bcrypt:', hash);
    console.log('');
    console.log('SQL pour créer l\'admin dans Supabase:');
    console.log(`INSERT INTO users (email, password_hash, role, created_at, updated_at)`);
    console.log(`VALUES (`);
    console.log(`  'admin@procedures.local',`);
    console.log(`  '${hash}',`);
    console.log(`  'admin',`);
    console.log(`  NOW(),`);
    console.log(`  NOW()`);
    console.log(`);`);
  });
} catch (e) {
  console.error('bcryptjs non installé. Installation...');
  console.log('Exécutez: npm install bcryptjs');
  console.log('Puis réessayez.');
  process.exit(1);
}
