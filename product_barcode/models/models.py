# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models, _
from odoo.exceptions import Warning,ValidationError
from odoo.osv import expression

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.onchange('seller_ids','id')
    @api.depends('seller_ids')
    def _generate_product_code(self):
        """
		Generate code of each product using it's component
        Product id from field [product id] [5 digits]
        Vendor id from field [vendor id] [4 digits]
		"""
        for template in self:
            if template.seller_ids:
                vendor_id = template.seller_ids[0].name.id
                template_id = self.search([],order='id desc', limit = 1)
                next_id = template_id.id + 1
                template.barcode = '"%s""%s"' % (str(next_id).zfill(5), str(vendor_id).zfill(4))
            else:
                template.barcode = ""
                
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    
    size_code = fields.Char(compute='_generate_product_code', size=2,
                                 help="Size Code from field [Variant Size Attribute] [2 digits]")
    color_code = fields.Char(compute='_generate_product_code', size=3,
                             help="Color Code from field [Variant Color Attribute] [3 digits]")
    
    @api.onchange('variant_seller_ids', 'product_tmpl_id',
                  'product_template_attribute_value_ids')
    @api.depends('variant_seller_ids','product_template_attribute_value_ids')
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
#             raise ValidationError('hhhhhh')
            if product.variant_seller_ids[0].name.id:
                vendor_id = product.variant_seller_ids[0].name.id
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
                        product.barcode = '"%s""%s"%s""%s"' % (str(template_id).zfill(5), 
                                                               str(vendor_id).zfill(4), product.size_code.zfill(2),
                                                               color_code.zfill(3))
                    else:
                        product.barcode = '"%s""%s"' % (template_id.zfill(5), vendor_id.zfill(4))
            else:
                product.barcode = ""
    
    
    
    @api.model_create_multi
    def create(self, vals_list):
        products = super(ProductProduct, self.with_context(create_product_product=True)).create(vals_list)
        # `_get_variant_id_for_combination` depends on existing variants
        products._generate_product_code()
        self.clear_caches()
        return products
