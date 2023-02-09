import asyncio
import aiohttp
import pandas as pd

print("Pokretanje klijent skripte\n")

listaIdKlijenata= list(range(1, 10001))
print("Učitavanje podataka\n")
dataframe= pd.read_json("data/dataset.json", lines=True)
print("Podatci učitani.\n")

redoviPoKlijentu= int(len(dataframe) / len(listaIdKlijenata))

klijenti= {id:[] for id in listaIdKlijenata}

for id, kodovi in klijenti.items():
    odReda= (id-1)*redoviPoKlijentu
    doReda= odReda+redoviPoKlijentu
    for index, red in dataframe.iloc[odReda+1:doReda+1].iterrows():
        kodovi.append(red.get("content"))
        
zadatci=[]
rezultati=[]

async def procesiranjeKoda():
    global zadatci
    global rezultati
    
    print("Slanje podataka\n")
    async with aiohttp.ClientSession(connector= aiohttp.TCPConnector(ssl= False)) as session:
        for id, kodovi in klijenti.items():
            zadatci.append(asyncio.create_task(session.get("http://127.0.0.1:8080/", json= {"client":id, "codes":kodovi})))
        print("Podatci poslani.\n")
        print("Čekanje svih odgovora...\n")
        rezultati= await asyncio.gather(*zadatci)
        rezultati= [await x.json() for x in rezultati]
        print("Dohvaćeni rezultati obrade podataka za sve klijente.\n")
        
asyncio.get_event_loop().run_until_complete(procesiranjeKoda())

procesiraniPodatci= {}
for rezultat in rezultati:
    print("Prosječna duljina koda za klijenta koji ima ID", rezultat.get("client"), "je", rezultat.get("averageWordcount"))
    