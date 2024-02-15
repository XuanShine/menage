from fastapi import FastAPI
from pony.orm import db_session
from database import *
from fastapi.testclient import TestClient
from main import *

client = TestClient(app)
db.bind('sqlite', ':sharedmemory:')


def test_listeChambres():
    response = client.get("/menage/listeChambres/11022024")
    assert response == {}
    response2 = client.get("/menage/listeChambres/10022024")
    assert response2 == {}

def test_setChambreANettoyer():
    response = client.get("/menage/set/11022024/Paul/205")
    assert response == {}
    # Erreur user
    response2 = client.get("/menage/set/11022024/Toto/205")
    assert response2 == {}
    # Erreur chambre
    response3 = client.get("/menage/set/11022024/Paul/905")
    assert response3 == {}

def test_deleteChambreANettoyer():
    # Erreur chambre
    response = client.get("/menage/delete/11022024/Paul/301")
    assert response == {}
    # Erreur user
    response2 = client.get("/menage/delete/11022024/Toto/204")
    assert response2 == {}
    # Normal
    response3 = client.get("/menage/delete/11022024/Paul/204")
    assert response3 == {}