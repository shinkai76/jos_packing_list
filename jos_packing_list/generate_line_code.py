# encoding=utf-8
import requests
import time
import json
import settings
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from models import *
from sqlalchemy import select, func, union_all, cast, Unicode, null, case

from random import randint

engine = create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (settings.USER, settings.PASSWORD,
                                                              settings.DATA_HOST, settings.DATABASE), echo=True, client_encoding='utf8')
Session = sessionmaker(bind=engine)
session = Session()
try:
	lines = session.query(PackingListLine).all()
	for item in lines:
		packing_list = session.query(PackingList).filter(PackingList.id == item.packing_list_id).first()
		if packing_list:
			item.code = packing_list.code + "-%05d" % item.id
	session.commit()
except Exception as e:
	session.rollback()
	raise e
finally:
	session.close()

