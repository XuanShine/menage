from fastapi import FastAPI
from pony.orm import db_session
from database import *

app = FastAPI()

db.bind(provider='sqlite', filename=os.path.join(C, 'database.sqlite'), create_db=True)
db.generate_mapping(create_tables=True)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/menage/listeChambres/{date}")
async def listeChambre(date : str):
    "date: ddmmaaaa"
    with db_session:
        query = select(chambre for chambre in ChambreANettoyer if chambre.date == date).order_by(ChambreANettoyer.chambre)
        return {"date": date,
                "chambres": [chambre.json() for chambre in query]}

@app.post("/menage/set/{date}/{user}/{chambre}")
async def setChambreANettoyer(date: str, user: str, chambre: int):
    "date: ddmmaaaa"
    with db_session:
        user = User[user]
        chambre = Chambre[chambre]
        if (res := ChambreANettoyer.get(date=date, chambre=chambre, user=user)) is None:
            res = ChambreANettoyer(user=user, chambre=chambre, date=date)
            db.commit()
        json = res.json()
    return json

@app.delete("/menage/delete/{date}/{user}/{chambre}")
async def deleteChambreANettoyer(date: str, user: str, chambre: int):
    "date: ddmmaaaa"
    with db_session:
        user = User[user]
        chambre = Chambre[chambre]
        if (res := ChambreANettoyer.get(date=date, chambre=chambre, user=user)) is not None:
            data_return = res.json().copy()
            res.delete()
            db.commit()
            return data_return
        else:
            return {"message": "Element not in db"}


@app.get("/horaire/status/{user}")
async def horaires(user: str):
    with db_session:
        user = User[user]
        return {"user": user.json(),
                "horaires": [horaire.json() for horaire in user.horaires]}


@app.post("/horaire/arrive/{user}")
async def horaireArrive(user: str):
    with db_session:
        time = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        res = Horaire(time=time, etat=True, user=User[user])
        return res.json()

@app.post("/horaire/depart/{user}")
async def horaireDepart(user: str):
    with db_session:
        time = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        res = Horaire(time=time, etat=False, user=User[user])
        return res.json()
