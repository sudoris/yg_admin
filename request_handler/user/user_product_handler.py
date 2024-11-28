# -*- coding: utf-8 -*-
from app_config.config import (
    domain
)
import os
import json
from copy import copy
from jinja2 import Environment, FileSystemLoader
from flask import Blueprint, request, redirect, make_response, session, json, current_app, jsonify, g
from request_handler.user.user_request_helper import check_user_login, render_template
from app_service.product_service import ProductService
from app_model.product_model import Product, ProductImage, ProductColor, ProductSpecific, ProductColorImage, ProductStatus
from app_model.event_model import EventPrimary
from app_utility.file_utility import save_base64_str, save_file


row_per_page = 10
user_product_handler = Blueprint('user_product_handler', __name__)


@user_product_handler.route('/dashboard/user/product/list', methods=['GET', 'POST'])
@user_product_handler.route('/dashboard/user/product/list/<int:page>', methods=['GET', 'POST'])
@check_user_login
def product_list_handler(user_id, page=1):
    """ 商品列表 """
    db_session = g.db_session
    product_service = ProductService(db_session=db_session)

    criteria = {
        'title': request.values.get('title', ''),
        'category_id': request.values.get('category_id', ''),
    }
    total_count, item_list = product_service.find_product_by_criteria(criteria=copy(criteria), page=page, row_per_page=row_per_page)

    total_page, remainder = divmod(total_count, row_per_page)
    if remainder > 0:
        total_page += 1

    category_id_and_title_dict = {}
    category_list = product_service.find_all_product_category()
    for category in category_list:
        category_id_and_title_dict[category.id] = category.title

    template_path = 'user/pages/product/product_list.html'
    return render_template(template_path, item_list=item_list, criteria=criteria, category_list=category_list, category_id_and_title_dict=category_id_and_title_dict,
                           ProductStatus=ProductStatus, total_page=total_page, page=page, row_per_page=row_per_page)


@user_product_handler.route('/dashboard/user/product/create', methods=['GET', 'POST'])
@check_user_login
def product_create(user_id):
    db_session = g.db_session
    product_service = ProductService(db_session=db_session)

    if request.method == 'GET':
        color_payload = []
        color_list = product_service.find_all_product_color()
        for color in color_list:
            color_payload.append(color.title)

        category_list = product_service.find_all_product_category()
        template_path = 'user/pages/product/product_create.html'
        product = {'title': '', 'price': 0, 'status': 'NORMAL', 'category_id': 1, 'specificList': [], 'colorImageList': [], 'productImageList': []}
        return render_template(template_path, category_list=category_list, color_list=color_list,
                               color_list_json=json.dumps(color_payload, ensure_ascii=False),
                               product=json.dumps(product, ensure_ascii=False), product_content='')

    """ POST """
    content = json.loads(request.values.get('content', '{}'))
    title = content.get('title', '').strip()
    price = content.get('price', 0)
    status = content.get('status', 'NORMAL')
    category_id = content.get('category_id', 1)
    specific_list = content.get('specificList', [])
    color_image_list = content.get('colorImageList', [])
    product_image_list = content.get('productImageList', [])
    product_content = request.values.get('product_content', '').strip()

    product = Product(category_id=category_id, title=title, content=product_content, price=price, status=status, create_user_id=user_id)
    db_session.add(product)
    db_session.flush()

    for specific in specific_list:
        product_specific = ProductSpecific(product_id=product.id, title=specific['title'], color_list=json.dumps(specific['colorList'], ensure_ascii=False), create_user_id=user_id)
        db_session.add(product_specific)

    for color_image in color_image_list:
        if color_image['content'].startswith('data:'):
            image_url = save_base64_str(color_image['content'], 'product')
            color_image_item = ProductColorImage(product_id=product.id, color=color_image['color'], image_url=image_url, create_user_id=user_id)
            db_session.add(color_image_item)

    for product_image in product_image_list:
        product_image_item = db_session.query(ProductImage).filter_by(image_url=product_image['image_url'], removed=0).first()
        product_image_item.seq = product_image['seq'] if product_image['seq'] else 0
        if not product_image_item.product_id:
            product_image_item.product_id = product.id

    db_session.commit()
    return redirect('/dashboard/user/product/update/{}?result=1&message=新增成功'.format(product.id))


@user_product_handler.route('/dashboard/user/product/update/<int:product_id>', methods=['GET', 'POST'])
@check_user_login
def product_update(user_id, product_id):
    db_session = g.db_session
    product_service = ProductService(db_session=db_session)

    product = product_service.find_product_by_id(product_id=product_id)
    if not product or product.removed:
        return redirect('/dashboard/user/product/list')

    if request.method == 'GET':
        color_payload = []
        color_list = product_service.find_all_product_color()
        for color in color_list:
            color_payload.append(color.title)

        category_list = product_service.find_all_product_category()

        product_specific_payload = []
        product_specific_list = product_service.find_all_product_specific_by_product_id(product_id=product_id)
        for product_specific in product_specific_list:
            product_specific_payload.append({'title': product_specific.title, 'colorList': json.loads(product_specific.color_list)})

        product_color_image_payload = []
        product_color_image_list = product_service.find_all_product_color_image_by_product_id(product_id=product_id)
        for product_color_image in product_color_image_list:
            product_color_image_payload.append({'color': product_color_image.color, 'content': domain + product_color_image.image_url})

        product_image_payload = []
        product_image_list = product_service.find_all_product_image_by_product_id(product_id=product_id)
        for product_image in product_image_list:
            product_image_payload.append({'image_url': product_image.image_url, 'seq': product_image.seq})

        payload = {'id': product.id, 'title': product.title, 'price': product.price, 'status': product.status.name,
                   'category_id': product.category_id, 'specificList': product_specific_payload, 'colorImageList': product_color_image_payload, 'productImageList': product_image_payload}
        template_path = 'user/pages/product/product_update.html'
        return render_template(template_path, category_list=category_list, color_list=color_list,
                               color_list_json=json.dumps(color_payload, ensure_ascii=False),
                               product_id=product_id,
                               product=json.dumps(payload, ensure_ascii=False), product_content=product.content)

    """ POST """
    content = json.loads(request.values.get('content', '{}'))
    title = content.get('title', '').strip()
    price = content.get('price', 0)
    status = content.get('status', 'NORMAL')
    category_id = content.get('category_id', 1)
    specific_list = content.get('specificList', [])
    color_image_list = content.get('colorImageList', [])
    product_image_list = content.get('productImageList', [])

    product_content = request.values.get('product_content', '').strip()
    product.update(category_id=category_id, title=title, content=product_content, price=price, status=status, update_user_id=user_id)

    specific_title_list = []
    for specific in specific_list:
        specific_title_list.append(specific['title'])
        product_specific = db_session.query(ProductSpecific).filter_by(product_id=product.id, title=specific['title'], removed=0).first()
        if not product_specific:
            product_specific = ProductSpecific(product_id=product.id, title=specific['title'], color_list=json.dumps(specific['colorList'], ensure_ascii=False), create_user_id=user_id)
            db_session.add(product_specific)
        else:
            product_specific.update(color_list=json.dumps(specific['colorList'], ensure_ascii=False), update_user_id=user_id)

    remove_specific_list = db_session.query(ProductSpecific).filter(ProductSpecific.product_id==product.id, ProductSpecific.title.notin_(specific_title_list), ProductSpecific.removed==0).all()
    for remove_specific in remove_specific_list:
        remove_specific.delete(update_user_id=user_id)

    color_list = []
    for color_image in color_image_list:
        color_list.append(color_image['color'])
        color_image_item = db_session.query(ProductColorImage).filter_by(product_id=product.id, color=color_image['color'], removed=0).first()
        if not color_image_item:
            if color_image['content'].startswith('data:'):
                image_url = save_base64_str(color_image['content'], 'product')
                color_image_item = ProductColorImage(product_id=product.id, color=color_image['color'], image_url=image_url, create_user_id=user_id)
                db_session.add(color_image_item)
        else:
            if color_image['content'].startswith('data:'):
                image_url = save_base64_str(color_image['content'], 'product')
                color_image_item.update(image_url=image_url, update_user_id=user_id)

    remove_color_image_list = db_session.query(ProductColorImage).filter(ProductColorImage.product_id==product.id, ProductColorImage.color.notin_(color_list), ProductColorImage.removed==0).all()
    for remove_color_image in remove_color_image_list:
        remove_color_image.delete(update_user_id=user_id)

    image_url_list = []
    for product_image in product_image_list:
        image_url_list.append(product_image['image_url'])
        product_image_item = db_session.query(ProductImage).filter_by(image_url=product_image['image_url'], removed=0).first()
        product_image_item.seq = product_image['seq'] if product_image['seq'] else 0
        if not product_image_item.product_id:
            product_image_item.product_id = product.id

    remove_product_image_list = db_session.query(ProductImage).filter(ProductImage.product_id==product.id, ProductImage.image_url.notin_(image_url_list), ProductImage.removed==0).all()
    for remove_product_image in remove_product_image_list:
        remove_product_image.delete(update_user_id=user_id)

    db_session.commit()
    return redirect('/dashboard/user/product/update/{}?result=1&message=更新成功'.format(product.id))


@user_product_handler.route('/dashboard/user/product/color', methods=['GET', 'POST'])
@check_user_login
def product_color_management(user_id):
    """ 商品顏色管理 """
    db_session = g.db_session
    product_service = ProductService(db_session=db_session)

    if request.method == 'GET':
        color_payload = []
        color_list = product_service.find_all_product_color()
        for color in color_list:
            color_payload.append({'title': color.title, 'code': color.code})
        template_path = 'user/pages/product/color.html'
        return render_template(template_path, color_list=json.dumps(color_payload, ensure_ascii=False))

    """ POST """
    title_list = request.form.getlist('title')
    code_list = request.form.getlist('code')
    current_app.logger.info('title_list: {}'.format(title_list))
    current_app.logger.info('code_list: {}'.format(code_list))

    for index, title in enumerate(title_list):
        code = code_list[index]
        product_color = product_service.find_or_create_product_color_by_title(title=title, user_id=user_id)
        if not product_color.id:
            db_session.add(product_color)

        product_color.code = code
        db_session.commit()

    return redirect('/dashboard/user/product/color')


@user_product_handler.route('/dashboard/user/product/ajax-upload-file', methods=['GET', 'POST'])
@check_user_login
def ajax_upload_file(user_id):
    db_session = g.db_session

    if 'file' in request.files and request.files['file']:
        upload_file = request.files['file']
        image_url = save_file(upload_file=upload_file, prefix='product')
        image = ProductImage(image_url=image_url, create_user_id=user_id)
        db_session.add(image)
        db_session.commit()
        return jsonify({'result': 1, 'image_url': image_url})
    else:
        return jsonify({'result': 0})


@user_product_handler.route('/dashboard/user/ckeditor-ajax-upload-image', methods=['GET', 'POST'])
@check_user_login
def ckeditor_ajax_upload_image(user_id):
    """ CKEditor Ajax 上傳 相簿圖片 """
    upload_file = request.files['upload']
    fc_name = request.values.get('CKEditorFuncNum')
    if upload_file:
        image_url = domain + save_file(upload_file=upload_file, prefix='ckeditor')
        payload = '<script type="text/javascript">'
        payload += 'window.parent.CKEDITOR.tools.callFunction("' + fc_name + '","' + image_url + '","");'
        payload += '</script>'
        return payload


@user_product_handler.route('/dashboard/user/product2/ajax-upload-image', methods=['GET', 'POST'])
@check_user_login
def product_ajax_upload_image(user_id):
    payload = {'success': 1}
    if 'image' in request.files and request.files['image']:
        upload_file = request.files['image']
        payload['file'] = {'url': save_file(upload_file=upload_file, prefix='product')}

    return jsonify(payload)


@user_product_handler.route('/dummy/parse-content-from-json-to-html', methods=['GET', 'POST'])
def parse_content_from_json_to_html():
    db_session = g.db_session

    env = Environment(loader=FileSystemLoader(searchpath=os.path.join(os.getcwd(), 'template', 'api', 'editor_js')))
    template = env.get_template('content.html')

    product_list = db_session.query(Product).filter(Product.removed == 0).all()
    for product in product_list:
        try:
            product.content = template.render({'domain': domain, 'content_list': json.loads(product.content)})
            db_session.commit()
        except Exception as e:
            pass

    event_primary_list = db_session.query(EventPrimary).filter(EventPrimary.removed == 0).all()
    for event_primary in event_primary_list:
        try:
            event_primary.content = template.render({'domain': domain, 'content_list': json.loads(event_primary.content)})
            event_primary.content_fee = template.render({'domain': domain, 'content_list': json.loads(event_primary.content_fee)})
            db_session.commit()
        except Exception as e:
            pass

    return 'OK'
