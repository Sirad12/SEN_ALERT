# app/seed.py : données de démonstration chargées si la base est vide
from sqlalchemy.orm import Session

from . import models

DONNEES = [
    ("SIG-000117", "Rue bouchée", "Signalement déjà fait ailleurs.", 520, 290, "Rejeté",
     [("Signalé", "25/10/2026", ""), ("Rejeté", "27/10/2026", "Motif : doublon")]),
    ("SIG-000118", "Caniveau bouché", "Caniveau rempli de sable devant le marché.", 320, 200, "Résolu",
     [("Signalé", "28/10/2026", ""), ("Vérifié", "29/10/2026", ""), ("En traitement", "31/10/2026", ""),
      ("Résolu", "03/11/2026", "Caniveau curé par l’équipe communale.")]),
    ("SIG-000119", "Rue bouchée", "Eau stagnante qui bloque la rue principale.", 290, 160, "En traitement",
     [("Signalé", "01/11/2026", ""), ("Vérifié", "02/11/2026", ""),
      ("En traitement", "04/11/2026", "Intervention prévue cette semaine.")]),
    ("SIG-000120", "Canal bouché", "Canal à ciel ouvert plein de déchets.", 470, 150, "Vérifié",
     [("Signalé", "03/11/2026", ""), ("Vérifié", "05/11/2026", "")]),
    ("SIG-000121", "Caniveau bouché", "Grille d’évacuation obstruée près de l’école.", 350, 95, "Signalé",
     [("Signalé", "06/11/2026", "")]),
    ("SIG-000122", "Caniveau bouché", "Caniveau effondré et rempli de gravats.", 210, 100, "Signalé",
     [("Signalé", "07/11/2026", "")]),
]


def charger(db: Session) -> None:
    if db.query(models.Signalement).first():
        return
    for id_, type_, desc, x, y, statut, etapes in DONNEES:
        s = models.Signalement(id=id_, type=type_, description=desc, x=x, y=y, statut=statut)
        s.historique = [models.Etape(statut=st, date=d, note=n) for st, d, n in etapes]
        db.add(s)
    db.commit()
