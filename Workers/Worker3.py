import asyncio
from aiohttp import web
import random
import string
import re

workerPort= 8083

routes= web.RouteTableDef()

@routes.get("/")
async def func(request):
    try:
        randomReqWaitTime= random.random()*0.2+0.1
        await asyncio.sleep(randomReqWaitTime)
        
        podatci= await request.json()
        rijeci= re.sub("["+string.punctuation+"]", "", podatci.get("data")).split()
        rezultat= len(rijeci)
        
        randomResWaitTime= random.random()*0.2+0.1
        await asyncio.sleep(randomResWaitTime)
        
        
        return web.json_response({"naziv": "worker", "status": "OK", "numberOfWords": rezultat}, status = 200)
        
        
    except Exception as e:
        return web.json_response({"naziv": "worker", "error": str(e)}, status = 500)




app= web.Application()
app.router.add_routes(routes)
web.run_app(app, port= workerPort)