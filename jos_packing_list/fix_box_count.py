# encoding=utf-8

from models import *
from common import *

session = Session()
try:
	packing_lists = session.query(PackingList).filter(PackingList.status == 6).all()
	for item in packing_lists:
		packing_list_lines = session.query(PackingListLine).filter(PackingListLine.packing_list_id == item.id).all()
		box_count = 0
		for i in packing_list_lines:
			box_count += 1
		item.box_count = box_count
	session.commit()
except Exception as e:
	session.rollback()
	raise e
finally:
	session.close()