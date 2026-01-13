#!/usr/bin/env node

// Script Node.js pour créer un utilisateur admin
const https = require('https');

const API_URL = 'procedure1.vercel.app';
const SETUP_SECRET = 'ejZ+z34wqydLsZwnXxfvIBR76CMFbrqHH1NATD6Ip5c=';
const EMAIL = process.argv[2] || 'admin@procedures.local';
const PASSWORD = process.argv[3] || 'AdminSecure123!';

const data = JSON.stringify({
  email: EMAIL,
  password: PASSWORD
});

const options = {
  hostname: API_URL,
  port: 443,
  path: '/api/setup/create-admin',
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${SETUP_SECRET}`,
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

console.log('Création de l\'utilisateur admin...');
console.log(`Email: ${EMAIL}`);
console.log(`API: https://${API_URL}/api/setup/create-admin`);
console.log('');

const req = https.request(options, (res) => {
  let body = '';

  res.on('data', (chunk) => {
    body += chunk;
  });

  res.on('end', () => {
    if (res.statusCode === 201 || res.statusCode === 200) {
      console.log('✅ Utilisateur admin créé avec succès!');
      console.log('');
      try {
        const response = JSON.parse(body);
        console.log('Réponse:', JSON.stringify(response, null, 2));
        console.log('');
        console.log('Vous pouvez maintenant vous connecter avec:');
        console.log(`  Email: ${EMAIL}`);
        console.log('  URL: https://procedure1.vercel.app/login');
      } catch (e) {
        console.log('Réponse:', body);
      }
      process.exit(0);
    } else {
      console.error(`❌ Erreur: Code HTTP ${res.statusCode}`);
      console.error('Réponse:', body);
      process.exit(1);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Erreur de connexion:', error.message);
  process.exit(1);
});

req.write(data);
req.end();
