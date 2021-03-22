# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models, _
from odoo.exceptions import Warning,ValidationError
from odoo.osv import expression

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    #### solve brackets error #############
    
    @api.onchange('seller_ids')
    @api.depends('seller_ids')
    def _generate_product_code(self):
        """
		Generate code of each product using it's component
        Product id from field [product id] [5 digits]
        Vendor id from field [vendor id] [4 digits]
		"""
        for template in self:
            if template.seller_ids[0].id:
                vendor_id = template.seller_ids[0].id
                template_id = template.id
                template.barcode = "%s%s" % (template_id.zfill(5)), vendor_id.zfill(4)))
            else:
                template.barcode = ""
    
    
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    
    size_code = fields.Char(compute='_generate_product_code', size=2,
                                 help="Size Code from field [Variant Size Attribute] [2 digits]")
    color_code = fields.Char(compute='_generate_product_code', size=3,
                             help="Color Code from field [Variant Color Attribute] [3 digits]")
    
    @api.onchange('seller_ids', 'product_tmpl_id',
                  'product_template_attribute_value_ids')
    @api.depends('seller_ids')
    def _generate_product_code(self):
        """
		Generate code of each product using it's component
        Product id from field [product id] [5 digits]
        Vendor id from field [vendor id] [4 digits]
        Size Code from field [Variant Size] [2 digits]
        Color Code from field [Variant Color Attribute] [3 digits]
		"""
        for product in self:
            color_attr = self.env.ref('product.product_attribute_2')
            size_attr = self.env.ref('product_barcode.product_attribute_size')
            if product.seller_ids[0].id:
                vendor_id = product.seller_ids[0].id
                template_id = product.product_tmpl_id.id
                
                for attr_val_line in product.product_template_attribute_value_ids:
                    if attr_val_line.attribute_id == color_attr \
                            and attr_val_line.product_attribute_value_id:
                        product.color_code = attr_val_line.product_attribute_value_id.name[:3]
                    if attr_val_line.attribute_id == size_attr \
                            and attr_val_line.product_attribute_value_id:
                        product.size_code = attr_val_line.product_attribute_value_id.name[:2]
            
                    if not product.color_code:
                        product.color_code = "000"
                    if not product.size_code:
                        product.size_code = "00"
                    color_code = ""
                    for word in product.color_code.split():
                        if word.isdigit():
                            color_code += word
                        
                    if product.size_code or color_code:
                        product.barcode = "%s%s%s%s" % (template_id.zfill(5)), vendor_id.zfill(4)), product.size_code, color_code)
                    else:
                        product.barcode = "%s%s" % (template_id.zfill(5)), vendor_id.zfill(4)))
            else:
                product.barcode = ""
