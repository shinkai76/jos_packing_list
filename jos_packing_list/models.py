# encoding=utf-8
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, create_engine, DateTime, Float, Unicode
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


class ObjectDict(dict):
    """Makes a dictionary behave like an object, with attribute-style access.
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

# 创建对象的基类:
Base = declarative_base()

def to_dict(self):
    result = ObjectDict()
    for c in self.__table__.columns:
        value = getattr(self, c.name, None)
        if isinstance(c.type, DateTime):
            if value:
                if type(value) != unicode:
                    result[c.name] = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    result[c.name] = value
            else:
                result[c.name] = value
        elif isinstance(c.type, Float):
            if value:
                result[c.name] = float(value)
            else:
                result[c.name] = value
        else:
            result[c.name] = value
    return result
 
Base.to_dict = to_dict


class SetOfBook(Base):
    __tablename__ = 'set_of_books'

    id = Column(Integer, primary_key=True)
    set_of_book = Column(Unicode(50))
    name = Column(Unicode(200))
    address = Column(Unicode(200))

class PackingList(Base):
    __tablename__ = 'packing_lists'

    id = Column(Integer, primary_key=True)
    code = Column(Unicode(50))
    box_count = Column(Integer)
    form_name = Column(Unicode(50))
    form_code = Column(Unicode(50))
    form_id = Column(Integer)
    partner_name = Column(Unicode(200))
    store_name = Column(Unicode(200))
    contactor = Column(Unicode(50))
    phone = Column(Unicode(50))
    mobile_phone = Column(Unicode(50))
    province = Column(Unicode(50))
    city = Column(Unicode(50))
    district = Column(Unicode(50))
    town = Column(Unicode(50))
    shipping_address = Column(Unicode(200))
    total_quantity = Column(Float)
    memo = Column(Unicode(200))
    form_created_at = Column(DateTime)
    status = Column(Integer)
    created_at = Column(DateTime)
    created_user = Column(Unicode(50))
    updated_at = Column(DateTime)
    updated_user = Column(Unicode(50))
    executed_at = Column(DateTime)
    executed_user = Column(Unicode(50))
    order_id = Column(Unicode(50))
    des = Column(Unicode(50))
    store = Column(Unicode(50))
    set_of_book = Column(Unicode(50))

packing_lists = PackingList.__table__


class PackingListLine(Base):
    __tablename__ = 'packing_list_lines'

    id = Column(Integer, primary_key=True)
    code = Column(String(50))
    packing_list_id = Column(Integer, ForeignKey("packing_lists.id"))
    total_quantity = Column(Float)
    set_of_book = Column(Unicode(50))

packing_list_lines = PackingListLine.__table__


class ProductLine(Base):
    __tablename__ = 'product_lines'

    id = Column(Integer, primary_key=True)
    packing_list_line_id = Column(Integer, ForeignKey("packing_list_lines.id"))
    product_id = Column(Integer)
    product_name = Column(Unicode(50))
    product_code = Column(Unicode(50))
    quantity = Column(Float)
    packing_quantity = Column(Float)
    set_of_book = Column(Unicode(50))

product_lines = ProductLine.__table__