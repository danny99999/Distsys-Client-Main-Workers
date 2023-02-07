from aiohttp import web
import random
import asyncio
import aiohttp

glavniPort= 8080

M= 1000
maxBrTrazenihOdgovora= 10000
brPrimljenihZahtjeva= 0
brVracenihOdgovora= 0
brPoslanihZadataka= 0
brIzvrsenihZadataka= 0

N= random.randint(5, 10)
print("Number of workers:", N)

workers= {"workerWithId"+str(id): [] for id in range(1, N+1)}
print("Workers:", workers)

routes= web.RouteTableDef()

@routes.get("/")
async def func(request):
    try:
        global N, workers, M
        global maxBrTrazenihOdgovora
        global brPrimljenihZahtjeva, brVracenihOdgovora
        global brPoslanihZadataka, brIzvrsenihZadataka
        
        brPrimljenihZahtjeva +=1
        print(f"Novi zahtjev primljen. Trenutno stanje primljenih zahtjeva: {brPrimljenihZahtjeva} / {maxBrTrazenihOdgovora}")
        podatci= await request.json()
        duzinaKoda= len(podatci.get("codes"))
        
        sviKodovi= '\n'.join(podatci.get("codes"))
        kodovi= sviKodovi.split("\n")
        podatci["codes"]= ["\n".join(kodovi[i:i+M]) for i in range(0, len(kodovi), M)]
        
        zadatci= []
        rezultati= []
        async with aiohttp.ClientSession(connector= aiohttp.TCPConnector(ssl= False)) as  session:
            trenutniWorker= 1
            for i in range(len(podatci.get("codes"))):
                zadatak= asyncio.create_task(session.get(f"http://127.0.0.1:{8080+trenutniWorker}/", json= {"id": podatci.get("client"), "podatci": podatci.get("codes")[i]}))
                brPoslanihZadataka +=1
                print(f"Novi zadatak poslan na worker {trenutniWorker}. Trenutno stanje poslanih zadataka: {brPoslanihZadataka}")
                zadatci.append(zadatak)
                workers["workerWithId"+str(trenutniWorker)].append(zadatak)
                if trenutniWorker == N:
                    trenutniWorker= 1
                else:
                    trenutniWorker +=1
                    
            rezultati= await asyncio.gather(*zadatci)
            brIzvrsenihZadataka += len(rezultati)
            print(f"Još {len(rezultati)} zadataka je izvršeno. Trenutno stanje dovršenih zadataka: {brIzvrsenihZadataka}")
            rezultati= [await rezultat.json() for rezultat in rezultati]
            rezultati= [rezultat.get("numberOfWords") for rezultat in rezultati]
            
        brVracenihOdgovora += 1
        print(f"Novi odgovor poslan. Trenutno stanje poslanih odgovora: {brVracenihOdgovora} / {maxBrTrazenihOdgovora}")   
        
        return web.json_response({"naziv": "master", "status": "OK", "klijent": podatci.get("client"), "prosječanBrRiječi": round(sum(rezultati) / duzinaKoda, 2)}, status = 200)
        
    except Exception as e:
        return web.json_response({"naziv": "master", "error": str(e)}, status = 500)        




app = web.Application()
app.router.add_routes(routes)
web.run_app(app, port = glavniPort, access_log = None)