# encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

if 'threading' in sys.modules:
    raise Exception('threading module loaded before patching!')

import gevent

if '__pypy__' in sys.builtin_module_names:
    from psycopg2cffi import compat
    compat.register()
from gevent import monkey

monkey.patch_all()

from psyco_gevent import make_psycopg_green
make_psycopg_green()

from bottle import Bottle, request, run, static_file, response, abort, template

import bottle
import jwt


app = Bottle()

import settings
from sqlalchemy.orm import sessionmaker
from models import *
from common import *
from datetime import datetime, timedelta
from tornado.template import Template

engine = create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (settings.USER, settings.PASSWORD,
                                                              settings.DATA_HOST, settings.DATABASE), echo=True, client_encoding='utf8')
Session = sessionmaker(bind=engine)

bottle.debug(settings.DEBUG)
app.catchall = False
bottle.TEMPLATE_PATH.append(settings.TEMPLATE_PATH)


def token_auth(func):

    def wrapper(*args, **kwargs):
        try:
            token = request.headers.get("Token")
            if not token:
                raise Exception(u"必须传递令牌")
            data = jwt.decode(token, settings.secret)
            kwargs["access_level"] = data.get("access_level")
            kwargs["token"] = data.get("token")
            kwargs["set_of_book"] = data.get("set_of_book")
            kwargs["url"] = data.get("url")
            kwargs["user_name"] = data.get("user_name")
            return func(*args, **kwargs)
        except Exception as e:
            return {"state": 0, "errmsg": str(e)}
        
    return wrapper


@app.error(500)
def error500(error):
    response.set_header('Content-Type', 'text/plain; charset=utf-8')

    return unicode(error.body)


@app.route('/static/<filename:path>')
def send_static(filename):
    print filename
    return static_file(filename, root=settings.STATIC_PATH)


@app.route('/')
def main_handler():
    return "hello, world!"


@app.route('/api/access_token')
def generate():
    try:
        token = request.headers.get("Token")
        params = get_params(request)
        url = params.get("url")
        set_of_book = params.get("set_of_book")
        user_name = params.get("user_name")
        if not url:
            raise Exception(u"必须传递url")
        if not set_of_book:
            raise Exception(u"必须传递账套号")
        if not user_name:
            raise Exception(u"必须传递用户名")
        if not token:
            return {"state": 0, "errmsg": u"必须传递token"}
        params = ObjectDict(security_key=settings.security_key)
        r = requests.get('%s/api/security_keys?action=has_security_key' % url, headers={"Token": token}, params=params)
        if not r.text or r.text == 'null':
            raise Exception("没有权限")
        result = r.json()
        result["token"] = token
        result["url"] = url
        result["set_of_book"] = set_of_book
        result["user_name"] = user_name
        data = jwt.encode(result, settings.secret)
        return {"state": 1, "token": data}
    except Exception as e:
        return {"state": 0, "errmsg": str(e)}


@app.route('/api/packing_lists')
@token_auth
def get_delivery_documents(**kwargs):
    session = Session()
    try:
        access_level = kwargs.get("access_level")
        if not (access_level & 1):
            raise Exception(u"不具备访问级查看")
        token = kwargs.get("token")
        url = kwargs.get("url")
        set_of_book = kwargs.get("set_of_book")
        params = get_params(request)
        short_no = params.get("short_no")
        if not short_no:
            raise Exception(u'必须传递单号')
        try:
            form_id = int(short_no)
        except Exception as e:
            if short_code[:2].lower() != "sk":
                raise Exception(u'必须是销售单')
            form_id = int(short_code[2:])
        packing_list = session.query(PackingList).filter(PackingList.form_name == 'sale_order', PackingList.form_id == form_id, PackingList.set_of_book == set_of_book).first()
        if packing_list:
            result = packing_list.to_dict()
            result["state"] = 1
        else:
            sale_order = get_sale_order(url, token, form_id)
            if not sale_order:
                raise Exception(u'销售单不存在或状态不为已执行')
            order_id = None
            des = None
            store = None
            if sale_order.data:
                order_id = sale_order.data.get("order_id")
                des = sale_order.data.get("des")
                store = sale_order.data.get("store")
            store_name = get_store_name(url, token, sale_order.store_id)
            result = ObjectDict(state = 1, id = None, code = None, form_name = 'sale_order', store_name = store_name, form_code = sale_order.code, form_id = sale_order.id, partner_name = sale_order.partner_name, contactor = sale_order.contactor, phone = sale_order.phone, mobile_phone = sale_order.mobile_phone, province = sale_order.province, city = sale_order.city, district = sale_order.district, town = sale_order.town, shipping_address = sale_order.shipping_address, total_quantity = sale_order.total_quantity, memo = sale_order.memo, form_created_at = sale_order.created_at, status = None, created_at = None, created_user = None, updated_at = None, updated_user = None, executed_at = None, executed_user = None, box_count = 0, order_id = order_id, des = des, store = store, sale_order_lines = sale_order.sale_order_lines)
        return result

    except Exception as e:
        return {"state": 0, "errmsg": str(e)}
    finally:
        session.close()
    

@app.route('/api/packing_lists', method='POST')
@token_auth
def create_packing_lists(**kwargs):
    session = Session()
    try:
        access_level = kwargs.get("access_level")
        if not (access_level & 4):
            raise Exception(u'不具备访问级新建')
        set_of_book = kwargs.get("set_of_book")
        user_name = kwargs.get("user_name")
        params = get_params(request)
        form_name = params.get("form_name")
        form_code = params.get("form_code")
        form_id = params.get("form_id")
        partner_name = params.get("partner_name")
        store_name = params.get("store_name")
        contactor = params.get("contactor")
        phone = params.get("phone")
        mobile_phone = params.get("mobile_phone")
        province = params.get("province")
        city = params.get("city")
        district = params.get("district")
        town = params.get("town")
        shipping_address = params.get("shipping_address")
        total_quantity = params.get("total_quantity")
        memo = params.get("memo")
        form_created_at = params.get("form_created_at")
        status = 0
        created_at = datetime.now()
        created_user = user_name
        order_id = params.get("order_id")
        des = params.get("des")
        store = params.get("store")
        packing_list_lines = params.get("packing_list_lines") or None
        sale_order_lines = params.get("sale_order_lines") or None
        if not packing_list_lines and not sale_order_lines:
            raise Exception(u'必须传递明细信息')
        packing_list = session.query(PackingList).filter(PackingList.form_id == form_id, PackingList.form_name == 'sale_order', PackingList.set_of_book == set_of_book).first()
        if packing_list:
            raise Exception(u'不能使用同一种销售单%s 重复创建装箱单' % form_code)
        new_packing_list = PackingList(form_name = form_name, form_code = form_code, form_id = form_id, partner_name = partner_name, store_name = store_name, contactor = contactor, phone = phone, mobile_phone = mobile_phone, province = province, city = city, district = district, town = town, shipping_address = shipping_address, total_quantity = total_quantity, memo = memo, form_created_at = form_created_at, status = status, created_at = created_at, created_user = created_user, executed_at = None, executed_user = None, order_id = order_id, des = des, store = store, set_of_book=set_of_book)
        session.add(new_packing_list)
        session.flush()
        id = new_packing_list.id
        code = to_code(id)
        new_packing_list.code = code
        if packing_list_lines:
            new_packing_list.box_count=len(packing_list_lines)
            for pll in packing_list_lines:
                new_packing_list_line = PackingListLine(packing_list_id=id, set_of_book=set_of_book)
                session.add(new_packing_list_line)
                session.flush()
                new_packing_list_line.code = new_packing_list.code+"-%05d" % new_packing_list_line.id
                total_quantity = 0
                for pl in pll.get("product_lines"):
                    new_product_line = ProductLine(packing_list_line_id=new_packing_list_line.id, product_id=pl.get("product_id"), product_name=pl.get("product_name"), product_code=pl.get("product_code"), quantity=pl.get("quantity"), packing_quantity=pl.get("packing_quantity"), set_of_book=set_of_book)
                    total_quantity += pl.get("packing_quantity")
                    session.add(new_product_line)
                new_packing_list_line.total_quantity = total_quantity
        else:
            new_packing_list.box_count = 1
            new_packing_list_line = PackingListLine(packing_list_id=id, set_of_book=set_of_book, total_quantity=0)
            session.add(new_packing_list_line)
            session.flush()
            new_packing_list_line.code = new_packing_list.code+"-%05d" % new_packing_list_line.id
            for pl in sale_order_lines:
                new_product_line = ProductLine(packing_list_line_id=new_packing_list_line.id, product_id=pl.get("product_id"), product_name=pl.get("product_name"), product_code=pl.get("product_code"), quantity=pl.get("quantity"), packing_quantity=0, set_of_book=set_of_book)
                session.add(new_product_line)
        session.commit()
        result = new_packing_list.to_dict()
        result["state"] = 1
        return result
    except Exception as e:
        session.rollback()
        return {"state": 0, "errmsg": str(e)}
    finally:
        session.close()


@app.route('/api/packing_lists/<id:int>', method='PUT')
@token_auth
def update_packing_lists(id, **kwargs):
    session = Session()
    try:
        access_level = kwargs.get("access_level")
        if not (access_level & 2):
            raise Exception(u'不具备访问级编辑')
        set_of_book = kwargs.get("set_of_book")
        user_name = kwargs.get("user_name")
        params = get_params(request)
        packing_list = session.query(PackingList).filter(PackingList.id == id, PackingList.set_of_book == set_of_book).first()
        if not packing_list:
            raise Exception(u'装箱单 %s 不存在' %id)
        if packing_list.status == 6:
            raise Exception(u'已执行单据不能进行修改')
        if "memo" in params:
            packing_list.memo = params.get("memo")
        if "contactor" in params:
            packing_list.contactor = params.get("contactor")
        if "phone" in params:
            packing_list.phone = params.get("phone")
        if "mobile_phone" in params:
            packing_list.mobile_phone = params.get("mobile_phone")
        if "province" in params:
            packing_list.province = params.get("province")
        if "city" in params:
            packing_list.city = params.get("city")
        if "district" in params:
            packing_list.district = params.get("district")
        if "town" in params:
            packing_list.town = params.get("town")
        if "shipping_address" in params:
            packing_list.shipping_address = params.get("shipping_address")
        packing_list.updated_at = datetime.now()
        packing_list.updated_user = user_name
        if "packing_list_lines" in params and params.get("packing_list_lines"):
            packing_list_lines = params.get("packing_list_lines")
            packing_list.box_count = len(packing_list_lines)
            ids = [line.get("id") for line in packing_list_lines]
            old_packing_list_lines = session.query(PackingListLine).filter(PackingListLine.packing_list_id == id, PackingListLine.set_of_book == set_of_book).all()
            line_maps = ObjectDict()
            for o in old_packing_list_lines:
                if o.id not in ids:
                    delete_packing_list_line(o.id, session, set_of_book)
                else:
                    line_maps[o.id] = o
            
            for line in packing_list_lines:
                if line.get("id"):
                    packing_list_line = line_maps.get(line.get('id'))
                    total_quantity = 0
                    for pl in line.get("product_lines"):
                        pl = ObjectDict(pl)
                        if not pl.get("id"):
                            new_product_line = ProductLine(packing_list_line_id=packing_list_line.id, product_id=pl.product_id, product_name=pl.product_name, product_code=pl.product_code, quantity=pl.quantity, packing_quantity=pl.packing_quantity, set_of_book=set_of_book)
                            total_quantity += pl.packing_quantity
                            session.add(new_product_line)
                        else:
                            product_line = session.query(ProductLine).filter(ProductLine.id == pl.id, ProductLine.set_of_book == set_of_book).first()
                            product_line.packing_quantity = pl.packing_quantity
                            total_quantity += pl.packing_quantity
                    packing_list_line.total_quantity = total_quantity
                else:
                    new_packing_list_line = PackingListLine(packing_list_id = id, set_of_book = set_of_book)
                    session.add(new_packing_list_line)
                    session.flush()
                    new_packing_list_line.code = packing_list.code+"-%05d" % new_packing_list_line.id
                    total_quantity = 0
                    for pl in line.get("product_lines"):
                        pl = ObjectDict(pl)
                        new_product_line = ProductLine(packing_list_line_id=new_packing_list_line.id, product_id=pl.product_id, product_name=pl.product_name, product_code=pl.product_code, quantity=pl.quantity, packing_quantity=pl.packing_quantity, set_of_book=set_of_book)
                        total_quantity += pl.packing_quantity
                        session.add(new_product_line)
                    new_packing_list_line.total_quantity = total_quantity
        session.commit()
        result = packing_list.to_dict()
        result["state"] = 1
        return result
    except Exception as e:
        session.rollback()
        return {"state": 0, "errmsg": str(e)}
    finally:
        session.close()


@app.route('/api/packing_lists/<id:int>')
@token_auth
def get_packing_lists(id, **kwargs):
    session = Session()
    try:
        access_level = kwargs.get("access_level")
        if not (access_level & 1):
            raise Exception(u'不具备访问级查看')
        set_of_book = kwargs.get("set_of_book")
        params = get_params(request)
        action = params.get("action")
        packing_list = session.query(PackingList).filter(PackingList.id == id, PackingList.set_of_book == set_of_book).first()
        if not packing_list:
            raise Exception(u'装箱单不存在')
        if not action:
            result = packing_list.to_dict()
            result["state"] = 1
        elif action == "execute":
            user_name = kwargs.get("user_name")
            if packing_list.status == 6:
                raise Exception(u'单据已执行,不能重复执行')
            if not check_empty_box(id, session, set_of_book):
                raise Exception(u'有箱子装箱数量为空,请检查')
            if not check_quantity(id, session, set_of_book):
                raise Exception(u'商品数量有误,请修改后再执行')
            packing_list.status = 6
            packing_list.executed_at = datetime.now()
            packing_list.executed_user = user_name
            session.commit()
            result = packing_list.to_dict()
            result["state"] = 1
        else:
            raise Exception(u'不能识别的action %s' % action)
        return result
    except Exception as e:
        session.rollback()
        return {"state": 0, "errmsg": str(e)}
    finally:
        session.close()


@app.route('/api/packing_lists/<id:int>', method='POST')
def print_form(id):
    session = Session()
    try:
        params = get_params(request)
        token = params.get("Token")
        if not token:
            raise Exception(u'必须传递令牌')
        data = jwt.decode(token, settings.secret)
        user_name = data.get("user_name")
        set_of_book = data.get("set_of_book")
        action = params.get("action")
        if action == "print":
            form_name = params.get("form_name")
            company = session.query(SetOfBook).filter(SetOfBook.set_of_book == set_of_book).first()
            if not company:
                raise Exception(u'%s 账套配置不存在' % set_of_book)
            packing_list = session.query(PackingList).filter(PackingList.id == id, PackingList.set_of_book == set_of_book).first()
            if not packing_list:
                raise Exception(u'装箱单不存在')
            if form_name == "packing_list":
                if packing_list.status != 6:
                    raise Exception(u'必须先执行才能打印装箱单')
                with open('./templates/packing_list.html', 'r') as f:
                    data = f.read()
                t = Template(data)
                result = to_pdf(t.generate(packing_list=get_result(id, session, set_of_book), font_url=settings.font_url, set_of_book=company))
                response.set_header("Content-Type", "application/pdf")
                return result
            elif form_name == "tag":
                results = get_result(id, session, set_of_book)
                if packing_list.status != 6:
                    box_count = params.get("box_count")
                    if box_count == 0 or box_count == "undefined" or not box_count:
                        raise Exception(u'必须传递箱数')
                    results.box_count = int(box_count)
                with open('./templates/tag.html', 'r') as f:
                    data = f.read()
                t = Template(data)
                result = to_pdf(t.generate(packing_list=results, set_of_book=company, font_url=settings.font_url))
                response.set_header("Content-Type", "application/pdf")
                return result
            else:
                raise Exception(u'不能识别的form_name %s' % form_name)
        else:
            raise Exception(u'不能识别的action %s' % action)
    except Exception as e:
        return {"state": 0, "errmsg": str(e)}
    finally:
        session.close()


@app.route('/api/packing_lists/<id:int>/packing_list_lines')
@token_auth
def get_packing_list_lines(id, **kwargs):
    session = Session()
    try:
        access_level = kwargs.get('access_level')
        if not (access_level & 1):
            raise Exception(u'不具备访问级查看')
        set_of_book = kwargs.get("set_of_book")
        packing_list = session.query(PackingList).filter(PackingList.id == id, PackingList.set_of_book == set_of_book).first()
        if not packing_list:
            raise Exception(u"装箱单不存在")
        packing_list_lines = session.query(PackingListLine).filter(PackingListLine.packing_list_id == id, PackingListLine.set_of_book == set_of_book).order_by(PackingListLine.id).all()
        results = []
        for p in packing_list_lines:
            packing_list_line = p.to_dict()
            packing_list_line.product_lines = []
            product_lines = session.query(ProductLine).filter(ProductLine.packing_list_line_id == p.id, ProductLine.set_of_book == set_of_book).order_by(ProductLine.id).all()
            for pr in product_lines:
                product_line = pr.to_dict()
                packing_list_line.product_lines.append(product_line)
            results.append(packing_list_line)
        return {"state": 1, "total_quantity": packing_list.total_quantity, "status": packing_list.status, "packing_list_lines": results}
    except Exception, e:
        return {"state": 0, "errmsg": str(e)}
    finally:
        session.close()


@app.route('/api/packing_lists/<id:int>/packing_list_lines', method='POST')
@token_auth
def create_line(id, **kwargs):
    session = Session()
    try:
        access_level = kwargs.get("access_level")
        if not (access_level & 4):
            raise Exception(u'不具备访问级新建')
        set_of_book = kwargs.get("set_of_book")
        packing_list = session.query(PackingList).filter(PackingList.id == id, PackingList.set_of_book == set_of_book).first()
        if not packing_list:
            raise Exception(u"装箱单不存在")
        if packing_list.status == 6:
            raise Exception(u"单据已执行,不能修改")
        params = get_params(request)
        product_lines = params.get("product_lines")
        new_packing_list_line = PackingListLine(packing_list_id=id, set_of_book=set_of_book)
        session.add(new_packing_list_line)
        session.flush()
        packing_list.box_count += 1
        new_packing_list_line.code = packing_list.code+"-%05d" % new_packing_list_line.id
        product_lines = []
        total_quantity = 0
        for pl in product_lines:
            pl = ObjectDict(pl)
            new_product_line = ProductLine(packing_list_line_id=new_packing_list_line.id, product_id=pl.product_id, product_name=pl.product_name, product_code=pl.product_code, quantity=pl.quantity, packing_quantity=pl.packing_quantity, set_of_book = set_of_book)
            session.add(new_product_line)
            session.flush()
            total_quantity += pl.packing_quantity
            p1 = new_product_line.to_dict()
            product_lines.append(p1)
        new_packing_list_line.total_quantity = total_quantity
        session.commit()
        results = new_packing_list_line.to_dict()
        results.state = 1
        results.product_lines = product_lines
        return results
    except Exception, e:
        session.rollback()
        return {"state": 0, "errmsg": str(e)}
    finally:
        session.close()


@app.route('/api/packing_lists/<id:int>/packing_list_lines/<packing_list_line_id:int>', method='PUT')
@token_auth
def update_line(id, packing_list_line_id, **kwargs):
    session = Session()
    try:
        access_level = kwargs.get('access_level')
        if not (access_level & 2):
            raise Exception(u'不具备访问级编辑')
        packing_list = session.query(PackingList).filter(PackingList.id == id, PackingList.set_of_book == set_of_book).first()
        if not packing_list:
            raise Exception(u"装箱单不存在")
        if packing_list.status != 6:
            packing_list_line = session.query(PackingListLine).filter(PackingListLine.id == packing_list_line_id, PackingListLine.packing_list_id == id, PackingListLine.set_of_book == set_of_book).first()
            if not packing_list_line:
                raise Exception(u"该箱记录不存在")
            params = get_params(request)
            product_lines = params.get("product_lines")
            product_lines = []
            total_quantity = 0
            for pl in product_lines:
                pl = ObjectDict(pl)
                if not pl.get("id"):
                    new_product_line = ProductLine(packing_list_line_id=packing_list_line.id, product_id=pl.product_id, product_name=pl.product_name, product_code=pl.product_code, quantity=pl.quantity, packing_quantity=pl.packing_quantity, set_of_book = set_of_book)
                    session.add(new_product_line)
                    session.flush()
                    total_quantity += pl.packing_quantity
                    p1 = new_product_line.to_dict()
                else:
                    product_line = session.query(ProductLine).filter(ProductLine.id == int(pl.id), ProductLine.set_of_book == set_of_book).first()
                    product_line.packing_quantity = pl.packing_quantity
                    total_quantity += pl.packing_quantity
                    p1 = product_line.to_dict()
                product_lines.append(p1)
            packing_list_line.total_quantity = total_quantity
            session.commit()
            results = packing_list_line.to_dict()
            results.state = 1
            result.product_lines = product_lines
        else:
            results = {"state": 1}
        return results
    except Exception, e:
        session.rollback()
        return {"state": 0, "errmsg": str(e)}
    finally:
        session.close()


@app.route('/api/packing_lists/<id:int>/packing_list_lines/<packing_list_line_id:int>', method='POST')
def print_single(id, packing_list_line_id):
    session = Session()
    try:
        params = get_params(request)
        token = params.get("Token")
        if not token:
            raise Exception(u'必须传递令牌')
        data = jwt.decode(token, settings.secret)
        user_name = data.get("user_name")
        set_of_book = data.get("set_of_book")
        action = params.get("action")
        if action == "print":
            packing_list = session.query(PackingList).filter(PackingList.id == id, PackingList.set_of_book == set_of_book).first()
            if not packing_list:
                raise Exception(u'装箱单不存在')
            packing_list_line = session.query(PackingListLine).filter(PackingListLine.id == packing_list_line_id, PackingListLine.packing_list_id == id, PackingListLine.set_of_book == set_of_book).first()
            if not packing_list_line:
                raise Exception(u"该箱记录不存在")
            company = session.query(SetOfBook).filter(SetOfBook.set_of_book == set_of_book).first()
            if not company:
                raise Exception(u'%s 账套配置不存在' % set_of_book)
            with open('./templates/packing_list_line.html', 'r') as f:
                data = f.read()
            t = Template(data)
            result = to_pdf(t.generate(packing_list=get_one_page(session, id, packing_list_line_id, set_of_book), set_of_book=company, font_url=settings.font_url))
            response.set_header("Content-Type", "application/pdf")
            return result
    except Exception as e:
        return {"state": 0, "errmsg": str(e)}
    finally:
        session.close()


@app.route('/api/packing_reports')
@app.route('/api/packing_reports', method='POST')
def main_handler():
    session = Session()
    try:
        params = get_params(request)
        token = request.headers.get("Token") or params.get("Token")
        if not token:
            raise Exception(u'必须传递token')
        data = jwt.decode(token, settings.secret)
        access_level = data.get("access_level")
        if not (access_level & 1):
            raise Exception(u'不具备访问级查看')
        set_of_book = data.get("set_of_book")
        action = params.get("action")
        format = params.get("format")
        if action == "packing_list":
            result = packing_reports(session, params, set_of_book)
            if format and format == "excel":
                response.set_header("Content-Type", "application/ms-excel")
                body = result.get('body')
                import urllib
                response.set_header('Content-disposition', "attachment; filename=%s" % urllib.quote(result.get('file_name').encode('utf-8')))

                return body
        elif action == "packing_line":
            result = packing_report_lines(session, params, set_of_book)
            if format and format == "excel":
                response.set_header("Content-Type", "application/ms-excel")
                body = result.get('body')
                import urllib
                response.set_header('Content-disposition', "attachment; filename=%s" % urllib.quote(result.get('file_name').encode('utf-8')))

                return body
        else:
            raise Exception(u'不能识别的action %s' % action)
        return result
    except Exception as e:
        return {"state": 0, "errmsg": str(e)}
    finally:
        session.close()

def main():
    run(app, server="gevent", host=settings.HOST, port=settings.PORT, quiet=True)


if __name__ == '__main__':
    main()
