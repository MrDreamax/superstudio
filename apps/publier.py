"""Publication depuis les applis : RETIRÉE (Super Studio 2.0). Tout se publie dans le chat avec Claude.

La personne dit « Programme ma semaine » (ou « Publie ce reel ») : le skill publieur le fait via Blotato,
après son OK. Les applis gardent seulement le bouton Télécharger. Ce module garde les mêmes fonctions pour que
les serveurs du Monteur et du Carrousel tournent sans rien publier.
"""
import json
import os

MESSAGE = "La publication se fait dans le chat : dis à Claude « Programme ma semaine » ou « Publie ce reel »."


def lire(p, d=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return d


def ecrire(p, o):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1)


def etat(dossier):
    return lire(os.path.join(dossier, "publication.json"), {}) or {}


def deja_publie(*cles):
    return ""


def demander(dossier, quoi, reseaux, quand, titre, cles_registre=(), forcer=False):
    return False, MESSAGE


def _maj(dossier, **k):
    e = etat(dossier)
    e.update(k)
    ecrire(os.path.join(dossier, "publication.json"), e)
    return e


def lancer(dossier, appli, contexte):
    _maj(dossier, statut="erreur", etape="", message=MESSAGE)
