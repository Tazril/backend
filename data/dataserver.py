import databases
import sqlalchemy
from data.constants import *

class DataServer :
    
    """
    SQL Database Creation with single Table
    """
    def __init__(self):
        metadata = sqlalchemy.MetaData()
        self.memes = sqlalchemy.Table(
            TABLE_NAME,
            metadata,
            sqlalchemy.Column(ID, sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column(NAME, sqlalchemy.String(2000)),
            sqlalchemy.Column(CAPTION, sqlalchemy.String(2000)),
            sqlalchemy.Column(URL, sqlalchemy.String(2000))
        )
        engine = sqlalchemy.create_engine(
            DATABASE_URL, connect_args={"ssl": {"key":"secret"}}
        )
        metadata.create_all(engine)
        
        self.database = databases.Database(DATABASE_URL)

    """
    returns: Database Instance
    """
    def get_database(self):
        return self.database

    """
    returns: Table Instance
    """
    def get_table(self):
        return self.memes
