# -*- coding: utf-8 -*-
from typing import Optional, Tuple, List, Dict
from app_service.core_service import CoreService
from app_model.product_model import ProductColor, ProductCategory, Product, ProductImage, ProductSpecific, ProductColorImage


class ProductService(CoreService):

    def find_product_by_id(self, product_id: int) -> Optional[Product]:
        db_session = self.db_session
        product = db_session.query(Product).filter_by(id=product_id, removed=0).first()
        return product

    def find_product_by_criteria(self, criteria: Dict, page: int, row_per_page: int) -> Tuple:
        db_session = self.db_session
        self.build_criteria_range(criteria=criteria, page=page, row_per_page=row_per_page)
        if criteria.get('title', None):
            criteria['title'] = '%' + criteria['title'] + '%'

        sql = "  SELECT COUNT(product.id) "
        sql += " FROM " + Product.TABLE + " AS product "
        sql += " WHERE product.removed = 0 "
        if criteria.get('status', None):
            sql += " AND product.status = :status "
        if criteria.get('title', None):
            sql += " AND product.title LIKE :title "
        if criteria.get('category_id', None):
            sql += " AND product.category_id = :category_id "
        total_count = db_session.execute(sql, criteria).fetchone()[0]

        sql = "  SELECT product.* "
        sql += " FROM " + Product.TABLE + " AS product "
        sql += " WHERE product.removed = 0 "
        if criteria.get('status', None):
            sql += " AND product.status = :status "
        if criteria.get('title', None):
            sql += " AND product.title LIKE :title "
        if criteria.get('category_id', None):
            sql += " AND product.category_id = :category_id "
        sql += " LIMIT :index, :count "
        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return total_count, item_list


    def api_find_product_by_criteria(self, criteria: Dict):
        if criteria.get('keyword', None):
            criteria['title'] = '%' + criteria['keyword'] + '%'

        db_session = self.db_session
        sql = "  SELECT id, category_id, title, price "
        sql += " FROM " + Product.TABLE + " AS product "
        sql += " WHERE product.removed = 0 "
        if criteria.get('status', None):
            sql += " AND product.status = :status "
        if criteria.get('category_id', None):
            sql += " AND product.category_id = :category_id "
        if criteria.get('title', None):
            sql += " AND product.title LIKE :title "

        results = db_session.execute(sql, criteria)
        item_list = [dict(zip(row.keys(), row)) for row in results]
        return item_list

    def find_all_product_image_by_product_id(self, product_id) -> List[ProductImage]:
        """ 取得商品圖片 """
        db_session = self.db_session
        product_image_list = db_session.query(ProductImage).filter_by(product_id=product_id, removed=0).order_by(ProductImage.seq.asc()).all()
        return product_image_list

    def find_all_product_category(self) -> List[ProductCategory]:
        """ 取得所有商品分類 """
        db_session = self.db_session
        product_category_list = db_session.query(ProductCategory).filter_by(removed=0).all()
        return product_category_list

    def find_all_product_color(self) -> List[ProductColor]:
        """ 取得所有商品顏色 """
        db_session = self.db_session
        product_color_list = db_session.query(ProductColor).filter_by(removed=0).all()
        return product_color_list

    def find_or_create_product_color_by_title(self, title: str, user_id: int) -> ProductColor:
        """ 取得商品顏色，若不存在則新增 """
        db_session = self.db_session
        product_color = db_session.query(ProductColor).filter_by(title=title).first()
        if product_color:
            return product_color

        product_color = ProductColor(title=title, create_user_id=user_id)
        return product_color

    def find_all_product_specific_by_product_id(self, product_id) -> List[ProductSpecific]:
        """ 取得商品規格 """
        db_session = self.db_session
        product_specific_list = db_session.query(ProductSpecific).filter_by(product_id=product_id, removed=0).order_by(ProductSpecific.id.asc()).all()
        return product_specific_list

    def find_product_specific_by_product_id_and_title(self, product_id, title) -> Optional[ProductSpecific]:
        db_session = self.db_session
        product_specific = db_session.query(ProductSpecific).filter_by(product_id=product_id, title=title, removed=0).first()
        return product_specific

    def find_all_product_color_image_by_product_id(self, product_id) -> List[ProductColorImage]:
        """ 取得商品顏色圖片 """
        db_session = self.db_session
        product_color_image_list = db_session.query(ProductColorImage).filter_by(product_id=product_id, removed=0).all()
        return product_color_image_list

    def find_product_color_image_by_product_id_and_color(self, product_id, color) -> ProductColorImage:
        """ 取得商品顏色圖片 """
        db_session = self.db_session
        product_color_image = db_session.query(ProductColorImage).filter_by(product_id=product_id, color=color, removed=0).first()
        return product_color_image
