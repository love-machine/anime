import requests
import os
import sqlite3
from datetime import datetime, timedelta

class FRanime:
    def __init__(self):
        self.WEBHOOK = os.getenv("DISCORD_WEBHOOK")
        self.url = "https://api.franime.fr/api/calendrier_data"
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        
        # --- INITIALISATION SQLITE ---
        # Crée le fichier .db s'il n'existe pas
        self.conn = sqlite3.connect("historique.db")
        self.cursor = self.conn.cursor()
        
        # On crée la table avec deux colonnes : la clé unique et la date
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS historique (
                cle TEXT PRIMARY KEY,
                date_ajout TEXT
            )
        ''')
        self.conn.commit()

    def envoyer_discord(self, anime, actuel):
        langue = anime.get('lang', 'vo').lower()
        couleur = 3447003 if langue == "vf" else 15144241
        emojit_titre = "🎉 PREMIÈRE :" if actuel == 1 else "📺 Nouvel épisode :"
        emojit_langue = "🇫🇷" if langue == "vf" else "🇯🇵"

        payload = {
            "username": "FRAnime Bot",
            "avatar_url": "https://franime.fr/logo.png",
            "embeds": [{
                "title": f"{emojit_titre} {anime.get('title_anime')}",
                "description": f"L'épisode **{actuel}** de la **Saison {anime.get('saison')}** est disponible !",
                "url": anime.get('url_access_anime_page'),
                "color": couleur,
                "fields": [
                    {"name": f"{emojit_langue} Langue", "value": f"**{langue.upper()}**", "inline": True},
                    {"name": "⏰ Sortie à", "value": f"**{anime.get('heures')}h{anime.get('minutes'):02d}**", "inline": True}
                ],
                "image": {"url": anime.get('affiche')},
                "footer": {
                    "text": f"FRAnime Bot • Exécuté à {datetime.now().strftime('%H:%M')}",
                    "icon_url": "https://franime.fr/logo.png"
                }
            }]
        }
        requests.post(self.WEBHOOK, json=payload)

    def nettoyage_historique(self):
        # On calcule la date d'il y a 30 jours
        date_limite = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Commande SQL magique : Supprime tout ce qui est plus vieux que date_limite
        self.cursor.execute("DELETE FROM historique WHERE date_ajout < ?", (date_limite,))
        self.conn.commit()
        if self.cursor.rowcount > 0:
            print(f"🧹 Nettoyage : {self.cursor.rowcount} anciennes entrées supprimées.")

    def main(self):
        self.nettoyage_historique()
        
        jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        jour_actuel = jours[datetime.now().weekday()]
        date_du_jour = datetime.now().strftime("%Y-%m-%d")

        donnees = {} # Initialisation vide par sécurité
        try:
            reponse = requests.get(self.url, headers=self.headers, timeout=10)
            reponse.raise_for_status()
            donnees = reponse.json()
        except Exception as e:
            print(f"🚨 Erreur réseau : {e}")
            return

        if donnees.get('success'):
            for anime in donnees['data']:
                prochain = anime.get('prochain_ep')
                actuel = prochain - 1
                id_anime = str(anime.get('id_anime'))
                title_anime = anime.get('title_anime')
                saison = str(anime.get('saison'))
                jour = anime.get('jour')
                
                cle_unique = f"{title_anime}_{id_anime}_S{saison}_E{actuel}"
                
                # --- VÉRIFICATION SQLITE ---
                self.cursor.execute("SELECT 1 FROM historique WHERE cle = ?", (cle_unique,))
                existe = self.cursor.fetchone()

                if jour == jour_actuel and not existe:
                    print(f"✅ Nouveau ! {title_anime} - Épisode {actuel}")
                    self.envoyer_discord(anime, actuel)
                    
                    # --- INSERTION SQLITE ---
                    self.cursor.execute("INSERT INTO historique (cle, date_ajout) VALUES (?, ?)", 
                                       (cle_unique, date_du_jour))
                    self.conn.commit()

if __name__ == "__main__":
    bot = FRanime()
    bot.main()