from fastapi import FastAPI, Cookie
from fastapi.responses import JSONResponse, RedirectResponse
from pony.orm import db_session
from database import *

from typing import Annotated

app = FastAPI()

db.bind(provider='sqlite', filename=os.path.join(C, 'database.sqlite'), create_db=True)
db.generate_mapping(create_tables=True)


def nowToStr():
    return datetime.now().strftime("%d/%m/%Y - %H:%M:%S")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/iam/{username}")
async def hello(username: str):
    with db_session:
        if (user := User.get(name=username)) is not None:
            Historique(user=user, date=nowToStr(), message=f"Set Cookie {username}")
            content = {"message": "cookie set"}
            response = JSONResponse(content=content)
            response.set_cookie(key="user", value=username)
            return response

@app.get("/menage/listeChambres/{date}")
async def listeChambre(date : str):
    "date: ddmmaaaa"
    with db_session:
        query = select(chambre for chambre in ChambreANettoyer if chambre.date == date).order_by(ChambreANettoyer.chambre)
        return {"date": date,
                "chambres": [chambre.json() for chambre in query]}

@app.post("/menage/set/{date}/{user}/{chambre}")
async def setChambreANettoyer(date: str, username: str, chambre: int):
    "date: ddmmaaaa"
    with db_session:
        user = User[username]
        Historique(user=user, date=nowToStr(), message=f"{username}: {date}+{chambre}")
        chambre = Chambre[chambre]
        if (res := ChambreANettoyer.get(date=date, chambre=chambre, user=user)) is None:
            res = ChambreANettoyer(user=user, chambre=chambre, date=date)
            db.commit()
        json = res.json()
    return json

@app.delete("/menage/delete/{date}/{username}/{chambre}")
async def deleteChambreANettoyer(date: str, username: str, chambre: int):
    "date: ddmmaaaa"
    with db_session:
        user = User[username]
        Historique(user=user, date=nowToStr(), message=f"{username}: {date}-{chambre}")
        chambre = Chambre[chambre]
        if (res := ChambreANettoyer.get(date=date, chambre=chambre, user=user)) is not None:
            data_return = res.json().copy()
            res.delete()
            db.commit()
            return data_return
        else:
            return {"message": "Element not in db"}


@app.get("/horaire/status")
async def horaires(username: Annotated[str | None, Cookie()] = None):
    if username is None:
        return {"message": "please set cookie ’user’. Go to /iam/{user}"}
        
    with db_session:
        user = User[username]
        return {"user": user.json(),
                "horaires": [horaire.json() for horaire in user.horaires]}


@app.post("/horaire/arrive")
async def horaireArrive(username: Annotated[str | None, Cookie()] = None):
    if username is None:
        return {"message": "please set cookie ’user’. Go to /iam/{user}"}
    
    with db_session:
        Historique(user=User[username], date=nowToStr(), message=f"{username}: arrive")
        res = Horaire(time=nowToStr(), etat=True, user=User[username])
        return res.json()


@app.post("/horaire/depart")
async def horaireDepart(username: Annotated[str | None, Cookie()] = None):
    if username is None:
        return {"message": "please set cookie ’user’. Go to /iam/{user}"}
      
    with db_session:
        Historique(user=User[username], date=nowToStr(), message=f"{username}: arrive")
        res = Horaire(time=nowToStr(), etat=False, user=User[username])
        return res.json()
