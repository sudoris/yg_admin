# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from app_service.core_service import CoreService
from app_model.member_model import Member
from app_model.order_model import OrderPrimary, OrderDetail, ShopCartItem
from app_model.product_model import Product


class OrderService(CoreService):

    def find_order_primary_by_id(self, primary_id: int) -> Optional[OrderPrimary]:
        db_session = self.db_session
        order_primary = db_session.query(OrderPrimary).filter(OrderPrimary.id == primary_id).first()
        return order_primary

    def count_order_primary_of_this_year(self):
        db_session = self.db_session
        year = datetime.now().year

        criteria = {'year': year}
        sql = "  SELECT COUNT(order_primary.id) "
        sql += " FROM " + OrderPrimary.TABLE + " AS order_primary "
        sql += " WHERE YEAR(order_primary.create_datetime) = :year "
        total_count = db_session.execute(sql, criteria).fetchone()[0]
        return total_count

    def find_order_primary_by_criteria(self, criteria: dict, page: int, row_per_page: int) -> Tuple:

        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)

        flag_search_member = False
        if criteria.get('no', None) or criteria.get('identify_no', None):
            flag_search_member = True

        if criteria.get('name', None):
            criteria['name'] = '%' + criteria['name'] + '%'
        if criteria.get('mobile', None):
            criteria['mobile'] = '%' + criteria['mobile'] + '%'
        if criteria.get('create_datetime_start', None):
            criteria['create_datetime_start'] = criteria['create_datetime_start'] + ' 00:00:00'
        if criteria.get('create_datetime_end', None):
            criteria['create_datetime_end'] = criteria['create_datetime_end'] + ' 23:59:59'
        if criteria.get('no', None):
            criteria['no'] = '%' + criteria['no'] + '%'
        if criteria.get('identify_no', None):
            criteria['identify_no'] = '%' + criteria['identify_no'] + '%'
        if criteria.get('card_no', None):
            criteria['card_no'] = '%' + criteria['card_no'] + '%'

        member_id_list = []
        if flag_search_member:
            sql = "  SELECT id "
            sql += " FROM " + Member.TABLE
            sql += " WHERE 1 = 1 "
            if criteria.get('no', None):
                sql += " AND no LIKE :no "
            if criteria.get('identify_no', None):
                sql += " AND identify_no LIKE :identify_no "
            results = db_session.execute(sql, criteria)
            item_list = [dict(zip(row.keys(), row)) for row in results]
            for item in item_list:
                member_id_list.append(item['id'])

        if flag_search_member and len(member_id_list) == 0:
            return 0, []

        sql = "  SELECT COUNT(`order`.id) "
        sql += " FROM " + OrderPrimary.TABLE + " `order` "
        sql += " WHERE 1 = 1 "
        if criteria.get('status', None):
            sql += " AND status = :status "
        if criteria.get('name', None):
            sql += " AND name LIKE :name "
        if criteria.get('card_no', None):
            sql += " AND card_no LIKE :card_no "
        if criteria.get('mobile', None):
            sql += " AND mobile LIKE :mobile "
        if criteria.get('create_datetime_start', None):
            sql += " AND create_datetime >= :create_datetime_start "
        if criteria.get('create_datetime_end', None):
            sql += " AND create_datetime <= :create_datetime_end "
        if flag_search_member:
            sql += " AND member_id IN ( "
            for index, member_id in enumerate(member_id_list) :
                sql += str(member_id)
                if index != len(member_id_list) - 1:
                    sql += ", "
            sql += " ) "

        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT `order`.*, `member`.id AS mem_member_id, `member`.no AS mem_member_no, `member`.name AS mem_member_name "
        sql += " FROM " + OrderPrimary.TABLE + " `order` "
        sql += " INNER JOIN " + Member.TABLE + " `member` ON `member`.id = `order`.member_id "
        sql += " WHERE 1 = 1 "
        if criteria.get('status', None):
            sql += " AND status = :status "
        if criteria.get('name', None):
            sql += " AND order.name LIKE :name "
        if criteria.get('card_no', None):
            sql += " AND card_no LIKE :card_no "
        if criteria.get('mobile', None):
            sql += " AND order.mobile LIKE :mobile "
        if criteria.get('create_datetime_start', None):
            sql += " AND create_datetime >= :create_datetime_start "
        if criteria.get('create_datetime_end', None):
            sql += " AND create_datetime <= :create_datetime_end "
        if flag_search_member:
            sql += " AND member_id IN ( "
            for index, member_id in enumerate(member_id_list) :
                sql += str(member_id)
                if index != len(member_id_list) - 1:
                    sql += ", "
            sql += " ) "
        sql += " ORDER BY `order`.id DESC "
        sql += " LIMIT :index, :count "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_order_detail_by_primary_id(self, primary_id: int) -> Tuple:
        db_session = self.db_session

        sql = "  SELECT COUNT(`order`.id) "
        sql += " FROM " + OrderDetail.TABLE + " `order` "
        sql += " WHERE 1 = 1 "
        sql += " AND primary_id = " + str(primary_id)
        total_count = db_session.execute(sql).fetchone()[0]

        sql = "  SELECT `order`.product_id, `products`.title, `order`.`price`, `order`.specific, `order`.color, `order`.quantity "
        sql += " FROM " + OrderDetail.TABLE + " `order` "
        sql += " INNER JOIN " + Product.TABLE + " `products` ON `products`.id = `order`.product_id"
        sql += " WHERE 1 = 1 "
        sql += " AND primary_id = " + str(primary_id)

        results = db_session.execute(sql)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list

    def find_order_by_criteria(self, criteria: dict, page: int,
                               row_per_page: int) -> List:
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria,
                                  page=page,
                                  row_per_page=row_per_page)
        if criteria.get('name', None):
            criteria['name'] = '%' + criteria['name'] + '%'
        if criteria.get('mobile', None):
            criteria['mobile'] = '%' + criteria['mobile'] + '%'
        if criteria.get('create_datetime_start', None):
            criteria['create_datetime_start'] = criteria[
                'create_datetime_start'] + ' 00:00:00'
        if criteria.get('create_datetime_end', None):
            criteria['create_datetime_end'] = criteria[
                'create_datetime_end'] + ' 23:59:59'

        sql = "  SELECT `order`.id, `order`.no, `order`.card_no, `order`.total_price, `order`.status, `order`.mobile, `order`.create_datetime, `detail`.primary_id, `detail`.product_id, `products`.id AS pt_product_id, `products`.title, `detail`.`price`, `detail`.specific, `detail`.color, `detail`.quantity "
        sql += " FROM " + OrderPrimary.TABLE + " `order` "
        sql += " LEFT OUTER JOIN " + OrderDetail.TABLE + " `detail` ON `detail`.primary_id = `order`.id"
        sql += " LEFT OUTER JOIN " + Product.TABLE + " `products` ON `products`.id = `detail`.product_id"
        sql += " WHERE 1 = 1 "
        if criteria.get('status', None):
            sql += " AND status = :status "
        if criteria.get('name', None):
            sql += " AND name LIKE :name "
        if criteria.get('mobile', None):
            sql += " AND mobile LIKE :mobile "
        if criteria.get('create_datetime_start', None):
            sql += " AND create_datetime >= :create_datetime_start "
        if criteria.get('create_datetime_end', None):
            sql += " AND create_datetime <= :create_datetime_end "
        sql += " ORDER BY `order`.id ASC "
        sql += " LIMIT :index, :count "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return item_list

    def find_shop_card_item_by_line_info_id_and_product_id_and_specific_and_color(self, line_info_id, product_id, specific, color):
        db_session = self.db_session
        shop_card_item = db_session.query(ShopCartItem).filter(ShopCartItem.line_info_id == line_info_id, ShopCartItem.product_id == product_id,
                                                               ShopCartItem.specific == specific, ShopCartItem.color == color).order_by(ShopCartItem.id.desc()).first()
        return shop_card_item

    def find_all_shop_card_item_by_line_info_id(self, line_info_id) -> List[ShopCartItem]:
        db_session = self.db_session
        shop_card_item_list = db_session.query(ShopCartItem).filter(ShopCartItem.line_info_id == line_info_id, ShopCartItem.quantity > 0).all()
        return shop_card_item_list
