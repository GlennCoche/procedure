#!/usr/bin/env python3
"""
Script de seed avec des données de test basées sur le document Huawei EMMA
Crée des procédures et tips d'exemple pour tester toutes les fonctionnalités
"""

import sys
import requests
from pathlib import Path
from typing import List, Dict, Any

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


# Données d'exemple basées sur le document Huawei EMMA
HUAWEI_ALARMS = [
    {
        "alarm_id": "4000",
        "alarm_name": "Inverter Communication Error",
        "severity": "Major",
        "causes": [
            {
                "cause_id": "1",
                "description": "The cable connection between EMMA and the inverter is abnormal."
            }
        ],
        "suggestions": [
            "Access the device monitoring menu on the app and locate the inverter experiencing abnormal communication based on the device status indicator.",
            "Check whether the inverter is powered on. If it is powered off, the alarm will be automatically cleared after it is powered on. If it is powered on, check whether the cable connection between the inverter and the EMMA is normal."
        ]
    },
    {
        "alarm_id": "4001",
        "alarm_name": "App Communication Certificate Expired",
        "severity": "Minor",
        "causes": [
            {
                "cause_id": "1",
                "description": "The device time is incorrectly set or the certificate has expired."
            }
        ],
        "suggestions": [
            "Check whether the device time is incorrectly set. If yes, reset or synchronize the system time.",
            "Contact your vendor or technical support to apply for a new certificate file and load it."
        ]
    },
    {
        "alarm_id": "4003",
        "alarm_name": "Auxiliary Power Fault",
        "severity": "Critical",
        "causes": [
            {
                "cause_id": "1",
                "description": "The auxiliary power supply of EMMA is abnormal."
            }
        ],
        "suggestions": [
            "Contact your vendor or technical support to replace EMMA."
        ]
    },
    {
        "alarm_id": "4004",
        "alarm_name": "Abnormal DI Instruction",
        "severity": "Major",
        "causes": [
            {
                "cause_id": "1",
                "description": "The parameters of active power dispatch via DI port are incorrectly configured."
            },
            {
                "cause_id": "2",
                "description": "The DI cable connection is abnormal."
            },
            {
                "cause_id": "3",
                "description": "The inverter does not support the reporting of dispatch values on DI ports."
            },
            {
                "cause_id": "4",
                "description": "The parameters of reactive power dispatch via DI port are incorrectly configured."
            }
        ],
        "suggestions": [
            "Check whether the settings in the DI signal configuration table for active power dispatch are complete and meet the requirements of the local power operator. If not, correct the settings.",
            "Check the cable connection between the Ripple Control device and the inverter. Ensure that the Ripple Control device is connected to only one inverter.",
            "Check the inverter software version. If the inverter software does not support the reporting of dispatch values on DI ports, update the inverter software.",
            "Check whether the settings in the DI signal configuration table for reactive power dispatch are complete and meet the requirements of the local power operator. If not, correct the settings."
        ]
    },
    {
        "alarm_id": "4006",
        "alarm_name": "Charger Communication Error",
        "severity": "Major",
        "causes": [
            {
                "cause_id": "1",
                "description": "The cable connection between EMMA and the charger is abnormal or the home router is faulty."
            },
            {
                "cause_id": "2",
                "description": "The EMMA certificate is abnormal or the charger communication certificate is abnormal."
            }
        ],
        "suggestions": [
            "Access the device monitoring menu on the app and locate the charger experiencing abnormal communication based on the device status indicator.",
            "Check whether the charger is powered off. If it is powered off, the alarm will be automatically cleared after it is powered on. If the charger is powered on, check whether the cable or Wi-Fi connection to the home router is normal.",
            "Contact your vendor or technical support to apply for a new certificate file and load it."
        ]
    },
    {
        "alarm_id": "4013",
        "alarm_name": "BackupBox Overload",
        "severity": "Major",
        "causes": [
            {
                "cause_id": "1",
                "description": "The power of appliances is too high."
            }
        ],
        "suggestions": [
            "Check whether high-power appliances are started. If yes, shut them down."
        ]
    }
]

# Tips d'exemple
EXAMPLE_TIPS = [
    {
        "title": "Vérification préventive des connexions",
        "content": "Effectuez une vérification visuelle des connexions tous les 3 mois. Vérifiez que tous les câbles sont bien serrés et qu'il n'y a pas de signes de corrosion ou d'usure.",
        "category": "Maintenance préventive",
        "tags": ["maintenance", "connexions", "préventif"]
    },
    {
        "title": "Gestion des certificats",
        "content": "Les certificats de communication expirent généralement après 1 an. Configurez un rappel 30 jours avant l'expiration pour éviter les interruptions de service.",
        "category": "Configuration",
        "tags": ["certificats", "sécurité", "configuration"]
    },
    {
        "title": "Diagnostic rapide des alarmes",
        "content": "En cas d'alarme, commencez toujours par vérifier l'alimentation électrique et les connexions physiques avant d'effectuer des modifications de configuration.",
        "category": "Diagnostic",
        "tags": ["diagnostic", "alarmes", "dépannage"]
    },
    {
        "title": "Mise à jour du firmware",
        "content": "Vérifiez régulièrement les mises à jour du firmware de vos équipements. Les nouvelles versions corrigent souvent des bugs et améliorent la compatibilité.",
        "category": "Maintenance",
        "tags": ["firmware", "mise à jour", "maintenance"]
    }
]


def create_procedure_from_alarm(alarm: Dict, brand: str = "Huawei") -> Dict:
    """Créer une structure de procédure à partir d'une alarme"""
    steps = []
    order = 1
    
    # Étape 1: Identifier l'alarme
    steps.append({
        "title": f"Identifier l'alarme {alarm['alarm_id']}",
        "description": f"Vérifier que l'alarme {alarm['alarm_id']} ({alarm['alarm_name']}) est bien présente",
        "instructions": f"Accéder au menu de monitoring de l'application et localiser l'équipement présentant l'alarme {alarm['alarm_id']}.",
        "order": order,
        "validation_type": "manual"
    })
    order += 1
    
    # Étapes pour chaque cause
    for idx, cause in enumerate(alarm['causes'], 1):
        steps.append({
            "title": f"Vérifier la cause {idx}",
            "description": cause['description'],
            "instructions": _generate_instructions_for_cause(cause, alarm),
            "order": order,
            "validation_type": "manual"
        })
        order += 1
    
    # Étapes pour les suggestions
    for idx, suggestion in enumerate(alarm['suggestions'], 1):
        steps.append({
            "title": f"Action {idx}",
            "description": suggestion[:100] + "..." if len(suggestion) > 100 else suggestion,
            "instructions": suggestion,
            "order": order,
            "validation_type": "manual"
        })
        order += 1
    
    return {
        "title": f"Résolution alarme {alarm['alarm_id']}: {alarm['alarm_name']} ({brand})",
        "description": f"Procédure de résolution pour l'alarme {alarm['alarm_id']} ({alarm['alarm_name']}) sur équipement {brand}. Sévérité: {alarm['severity']}",
        "category": f"Alarmes {brand}",
        "tags": [brand, f"Alarme-{alarm['alarm_id']}", alarm['severity'].lower(), "maintenance"],
        "steps": steps
    }


def _generate_instructions_for_cause(cause: Dict, alarm: Dict) -> str:
    """Générer des instructions détaillées pour une cause"""
    description = cause.get('description', '')
    instructions = f"Vérifier: {description}\n\n"
    
    if "cable" in description.lower() or "connection" in description.lower():
        instructions += "1. Vérifier visuellement les connexions\n"
        instructions += "2. Tester la continuité des câbles si nécessaire\n"
        instructions += "3. Vérifier que les connecteurs sont bien serrés\n"
    elif "certificate" in description.lower():
        instructions += "1. Vérifier la date système de l'équipement\n"
        instructions += "2. Contacter le support technique pour un nouveau certificat\n"
    elif "power" in description.lower():
        instructions += "1. Vérifier l'alimentation électrique\n"
        instructions += "2. Contrôler les fusibles et disjoncteurs\n"
    elif "parameter" in description.lower() or "configuration" in description.lower():
        instructions += "1. Accéder au menu de configuration\n"
        instructions += "2. Vérifier les paramètres actuels\n"
        instructions += "3. Comparer avec les valeurs recommandées\n"
    
    return instructions


def seed_data(api_url: str = "http://localhost:8000", email: str = "admin@procedures.local", password: str = "admin123"):
    """Seed la base de données avec des données de test"""
    
    # Se connecter
    session = requests.Session()
    
    print(f"🔐 Connexion à l'API avec {email}...")
    response = session.post(
        f"{api_url}/api/auth/login",
        data={"username": email, "password": password}
    )
    
    if response.status_code != 200:
        print(f"❌ Échec de la connexion: {response.status_code} - {response.text}")
        return
    
    token = response.json().get("access_token")
    if not token:
        print("❌ Token non reçu")
        return
    
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("✅ Connexion réussie\n")
    
    # Créer les procédures
    procedures_created = 0
    print("📋 Création des procédures...")
    
    for alarm in HUAWEI_ALARMS:
        procedure_data = create_procedure_from_alarm(alarm)
        
        response = session.post(
            f"{api_url}/api/procedures",
            json=procedure_data
        )
        
        if response.status_code == 201:
            procedures_created += 1
            proc = response.json()
            print(f"  ✅ Procédure créée: {proc['title']} (ID: {proc['id']}, {len(procedure_data['steps'])} étapes)")
        else:
            print(f"  ❌ Erreur création procédure {alarm['alarm_id']}: {response.status_code} - {response.text[:100]}")
    
    print(f"\n✨ {procedures_created}/{len(HUAWEI_ALARMS)} procédures créées\n")
    
    # Créer les tips
    tips_created = 0
    print("💡 Création des tips...")
    
    for tip_data in EXAMPLE_TIPS:
        response = session.post(
            f"{api_url}/api/tips",
            json=tip_data
        )
        
        if response.status_code == 201:
            tips_created += 1
            tip = response.json()
            print(f"  ✅ Tip créé: {tip['title']} (ID: {tip['id']})")
        else:
            print(f"  ❌ Erreur création tip: {response.status_code} - {response.text[:100]}")
    
    print(f"\n✨ {tips_created}/{len(EXAMPLE_TIPS)} tips créés\n")
    
    # Créer des tips à partir des alarmes (références)
    print("📚 Création des tips de référence...")
    ref_tips_created = 0
    
    for alarm in HUAWEI_ALARMS:
        tip_content = f"**Alarme {alarm['alarm_id']}: {alarm['alarm_name']}**\n\n"
        tip_content += f"**Sévérité:** {alarm['severity']}\n\n"
        tip_content += f"**Causes possibles:**\n"
        for cause in alarm['causes']:
            tip_content += f"- {cause['description']}\n"
        tip_content += f"\n**Suggestions:**\n"
        for suggestion in alarm['suggestions']:
            tip_content += f"- {suggestion}\n"
        
        tip_data = {
            "title": f"Référence: Alarme {alarm['alarm_id']} - {alarm['alarm_name']}",
            "content": tip_content,
            "category": "Alarmes Huawei",
            "tags": ["Huawei", f"Alarme-{alarm['alarm_id']}", alarm['severity'].lower(), "référence"]
        }
        
        response = session.post(
            f"{api_url}/api/tips",
            json=tip_data
        )
        
        if response.status_code == 201:
            ref_tips_created += 1
            tip = response.json()
            print(f"  ✅ Tip de référence créé: {tip['title']} (ID: {tip['id']})")
        else:
            print(f"  ❌ Erreur création tip de référence: {response.status_code}")
    
    print(f"\n✨ {ref_tips_created}/{len(HUAWEI_ALARMS)} tips de référence créés\n")
    
    print("=" * 60)
    print("🎉 Seed terminé!")
    print(f"  - {procedures_created} procédures créées")
    print(f"  - {tips_created} tips créés")
    print(f"  - {ref_tips_created} tips de référence créés")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed la base de données avec des données de test")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000", help="URL de l'API")
    parser.add_argument("--email", type=str, default="admin@procedures.local", help="Email admin")
    parser.add_argument("--password", type=str, default="admin123", help="Mot de passe admin")
    
    args = parser.parse_args()
    
    seed_data(api_url=args.api_url, email=args.email, password=args.password)
