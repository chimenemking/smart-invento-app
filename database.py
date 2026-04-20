from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import date

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    current_quantity = Column(Float, default=0)
    reorder_point = Column(Float, default=10)
    lead_time_days = Column(Integer, default=7)

class SalesHistory(Base):
    __tablename__ = 'sales_history'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    date = Column(Date, default=date.today)
    quantity_sold = Column(Float)

# Create engine and session
engine = create_engine('sqlite:///inventory.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()