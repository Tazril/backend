from typing import List
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.models import Meme, MemeIn, MemeBody
import validators
from data.dataserver import DataServer
from constants import *



app = FastAPI(title=TITLE)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

data_server = DataServer()
database = data_server.get_database()
memes = data_server.get_table()

@app.on_event(STARTUP)
async def startup():
    await database.connect()

@app.on_event(SHUTDOWN)
async def shutdown():
    await database.disconnect()

@app.get(HOME)
async def home():
    return {"message" : "Home Page"}

"""
GET MEME COUNT
:returns: memes count
"""
@app.get(MEME_COUNT, status_code = status.HTTP_200_OK)
async def get_meme_count():
    query = memes.select().count() 
    result = await database.fetch_one(query)
    return result

"""
GET MEME LIST
:param skip: skips/offset number of row
:param take: take/limit number of rows
:param sort: column on which list should be sorted
:param dir: sort direction  
:returns: memes list
"""
@app.get(MEME_LIST, response_model=List[Meme], status_code = status.HTTP_200_OK)
async def get_meme_list(skip: int = 0, take: int = 100,sort :str = 'id',dir :str = 'desc'):
    query = '''select * from memes order by {} collate nocase {} limit {} offset {}
            '''.format(sort,dir,take,skip)
    print(skip,take,sort,dir)
    result = await database.fetch_all(query)
    return result


"""
POST MEME 
:param meme: meme object to be posted
:returns: posted meme id
"""
@app.post(MEME_LIST, status_code = status.HTTP_201_CREATED)
async def create_meme(meme : MemeIn):
    if not validators.url(meme.url):
        raise HTTPException(status_code=422, detail="Invalid URL")
    query = '''select id from memes 
            where name = '{}' and url = '{}' and caption = '{}'
        '''.format(meme.name,meme.url,meme.caption)
    result = await database.fetch_one(query)
    if result:
        raise HTTPException(status_code=409, detail="Meme already exists")
    query = memes.insert().values(name=meme.name, caption=meme.caption, url=meme.url)
    record_id = await database.execute(query)
    return {"id": record_id}


"""
GET MEME 
:param meme_id: id of the meme to be retrieved
:returns: meme
"""
@app.get(MEME, response_model=Meme, status_code = status.HTTP_200_OK)
async def get_meme(meme_id: int):
    query = memes.select().where(memes.c.id == meme_id)
    result = await database.fetch_one(query)
    if not result: 
        raise HTTPException(status_code=404, detail=MEME_NOT_FOUND)
    return result

"""
GET MEME 
:param meme_id: id of the meme to be updated
:param body: carries new caption or url of the meme 
:returns: meme
"""
@app.patch(MEME, status_code = status.HTTP_200_OK)
async def update_meme(meme_id: int, body : MemeBody):
    query = memes.update().where(memes.c.id == meme_id)
    if not body.url and not body.caption:
        raise HTTPException(status_code=400, detail=PATCH_MISSING_FIELD)
    if body.caption:
        query = query.values(caption=body.caption)
    if body.url:
        if not validators.url(body.url):
            raise HTTPException(status_code=422, detail=INVALID_URL)
        query = query.values(url=body.url)
    result = await database.execute(query)
    if not result: 
        raise HTTPException(status_code=404, detail=MEME_NOT_FOUND)
    query = memes.select().where(memes.c.id == meme_id)
    result = await database.fetch_one(query)
    return result

"""
DELETE MEME 
:param meme_id: id of the meme to be deleted
:returns: meme id
"""
@app.delete(MEME,  status_code = status.HTTP_200_OK)
async def delete_meme(meme_id: int):
    query = memes.delete().where(memes.c.id == meme_id)
    record_id = await database.execute(query)
    if(record_id==0): 
        raise HTTPException(status_code=404, detail=MEME_NOT_FOUND)
    return {"id": record_id}