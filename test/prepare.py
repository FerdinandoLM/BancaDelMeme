import os 
import sys
sys.path.append('src')
from sqlalchemy import create_engine

import config
from models import Base

def main():
    try:
        os.remove(config.DBFILE)
    except FileNotFoundError:
        pass
    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    Base.metadata.create_all(engine)

main()
