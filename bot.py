import os
import feedparser
import requests

# Récupère l'URL depuis les variables d'environnement (sécurisé pour GitHub)
DISCORD_WEBHOOK_URL = os.environ.get(
    "DISCORD_WEBHOOK_URL", "TON_URL_WEBHOOK_ICI"
)
DEALABS_RSS_URL = "https://www.dealabs.com/rss/categorie/mode-accessoires"
FICHIER_HISTORIQUE = "deals_vus.txt"


def charger_deals_vus():
    if os.path.exists(FICHIER_HISTORIQUE):
        with open(FICHIER_HISTORIQUE, "r") as f:
            return set(line.strip() for line in f)
    return set()


def sauvegarder_deal_vu(deal_id):
    with open(FICHIER_HISTORIQUE, "a") as f:
        f.write(f"{deal_id}\n")


def envoyer_alerte_discord(titre, lien):
    payload = {
        "username": "Alerte Bon Plan Mode",
        "embeds": [{
            "title": f"🔥 {titre}",
            "url": lien,
            "color": 16738816,  # Couleur orange
            "description": (
                "Nouvelle offre détectée sur Dealabs ! Clique sur le titre pour"
                " voir le deal."
            ),
        }],
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"Erreur d'envoi Discord : {e}")


def verifier_dealabs():
    deals_vus = charger_deals_vus()
    feed = feedparser.parse(DEALABS_RSS_URL)

    mots_cles = [
        "nike",
        "adidas",
        "jordan",
        "lacoste",
        "ralph lauren",
        "carhartt",
        "the north face",
        "baskets",
    ]

    for entry in reversed(feed.entries):
        deal_id = entry.id
        if deal_id not in deals_vus:
            titre = entry.title
            lien = entry.link
            sauvegarder_deal_vu(deal_id)

            if any(mot in titre.lower() for mot in mots_cles):
                print(f"Alerte envoyée : {titre}")
                envoyer_alerte_discord(titre, lien)


if __name__ == "__main__":
    verifier_dealabs()