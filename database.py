import os, sys
C = os.path.abspath(os.path.dirname(__file__))
from datetime import datetime

from pony.orm import *

db = Database()

class User(db.Entity):
    name = PrimaryKey(str)
    permission = Optional("Permission")
    listeChambresANettoyer = Set("ChambreANettoyer")
    historique = Set("Historique")
    horaires = Set("Horaire")

    def json(self):
        return self.name

class Permission(db.Entity):
    name = PrimaryKey(str)
    user = Set(User)

class Historique(db.Entity):
    user = Required(User)
    date = Required(str, default=datetime.now().strftime("%d/%m/%Y - %H:%M:%S"))
    message = Required(str)

class Chambre(db.Entity):
    numero = PrimaryKey(int)
    datesNettoyage = Set("ChambreANettoyer")

    def json(self):
        return self.numero


class ChambreANettoyer(db.Entity):
    date = Required(str)
    chambre = Required(Chambre)
    user = Required(User)

    def json(self):
        return {"date": self.date,
                "chambre": self.chambre.json(),
                "user": self.user.json()}


class Horaire(db.Entity):
    time = Required(str)
    etat = Required(bool)  # True si présent au travail, False quand quitte le travail
    user = Required(User)

    def json(self):
        return {"date": self.time,
                "etat": self.etat,
                "user": self.user.json()}


def populate():
    db.bind(provider='sqlite', filename=os.path.join(C, 'database.sqlite'), create_db=True)
    db.generate_mapping()
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    # idb.drop_all_tables(with_all_data=True)
    
    with db_session:
        # Rooms
        for etage in range(2, 6):
            for chambre in range(1, 9):
                Chambre(numero=(etage*100+chambre))
        # User
        for user in ["Paul", "Antoine", "Sebastien"]:
            User(name=user)
        db.commit()

        date = "11022024"
        ChambreANettoyer(user=User["Paul"], chambre=Chambre[204], date=date)
        
        db.commit()