from database import Base
from sqlalchemy import Column
from sqlalchemy.sql.expression import text
from sqlalchemy.types import DateTime, Integer, BigInteger, Float


class Record(Base):
    __tablename__ = "records"
    record_id = Column("ID", BigInteger, primary_key=True, autoincrement=True)
    obj_id = Column("ID_OBJ", BigInteger, nullable=False)
    rec_date = Column("REC_DATE", DateTime, nullable=False, server_default=text("0000-00-00 00:00:00"))
    rid = Column("RID", Integer)
    rec_type = Column("REC_TYPE", Integer, default=1)
    lat = Column("LAT", Float)
    lon = Column("LON", Float)
    speed = Column("SPD", Float, default=0)
    power = Column("POWER", Integer, default=1)
    d1 = Column("D1", Integer)
    d2 = Column("D2", Integer)
    d3 = Column("D3", Integer)
    d4 = Column("D4", Integer)
    d5 = Column("D5", Integer)
    d6 = Column("D6", Integer)
    an1 = Column("AN1", Integer)
    an2 = Column("AN2", Integer)
    an3 = Column("AN3", Integer)
    an4 = Column("AN4", Integer)
    car_power = Column("CAR_POWER", Integer)
