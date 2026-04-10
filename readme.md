# 📺 FRAnime Bot

Un bot Discord qui surveille le calendrier de [FRAnime](https://franime.fr) et envoie automatiquement une notification lorsqu'un nouvel épisode est disponible le jour même.

---

## ✨ Fonctionnalités

- 🔍 Vérifie les animes du jour via l'API FRAnime
- 📨 Envoie une notification Discord via webhook avec un embed enrichi
- 🎉 Distingue les premières (épisode 1) des épisodes suivants
- 🇫🇷 / 🇯🇵 Indique la langue de diffusion (VF ou VO)
- 🗄️ Historique SQLite pour éviter les doublons de notifications
- 🧹 Nettoyage automatique des entrées de plus de 30 jours

---

## 📋 Prérequis

- Python 3.8+
- Les bibliothèques suivantes :

```bash
pip install requests
```

> `sqlite3` est inclus dans la bibliothèque standard Python.

---

## ⚙️ Configuration

Le bot utilise une variable d'environnement pour le webhook Discord :

```bash
export DISCORD_WEBHOOK="https://discord.com/api/webhooks/VOTRE_WEBHOOK_ICI"
```

Pour créer un webhook Discord :
1. Aller dans les paramètres d'un salon Discord
2. **Intégrations** → **Webhooks** → **Créer un webhook**
3. Copier l'URL et l'exporter comme variable d'environnement

---

## 🚀 Utilisation

```bash
python franime.py
```

Le script s'exécute une fois, vérifie les animes du jour, et envoie les notifications nécessaires. Il est conçu pour être **planifié via un cron job** :

```bash
# Exemple : exécution toutes les heures
0 * * * * /usr/bin/python3 /chemin/vers/franime.py
```

---

## 🗂️ Structure du projet

```
.
├── franime.py        # Script principal
└── historique.db     # Base SQLite (créée automatiquement au premier lancement)
```

---

## 🔔 Exemple de notification Discord

| Champ | Valeur |
|---|---|
| Titre | 🎉 PREMIÈRE : *Nom de l'anime* ou 📺 Nouvel épisode : *Nom* |
| Description | L'épisode X de la Saison Y est disponible ! |
| Langue | 🇫🇷 VF (bleu) ou 🇯🇵 VO (orange) |
| Sortie à | Heure et minutes de diffusion |
| Image | Affiche de l'anime |

La couleur de l'embed change selon la langue :
- 🔵 **Bleu** → Version Française (VF)
- 🟠 **Orange** → Version Originale (VO)

---

## 🧠 Fonctionnement interne

1. **Nettoyage** : suppression des entrées SQLite de plus de 30 jours
2. **Récupération** : appel à `https://api.franime.fr/api/calendrier_data`
3. **Filtrage** : seuls les animes dont le jour de diffusion correspond au jour actuel sont traités
4. **Déduplication** : une clé unique `titre_idAnime_saison_épisode` est vérifiée en base avant envoi
5. **Notification** : envoi de l'embed Discord si l'épisode n'a pas encore été notifié
6. **Sauvegarde** : la clé est insérée en base pour éviter tout doublon futur

---

## 📄 Licence

Ce projet est personnel et non officiel. Il n'est pas affilié à FRAnime.