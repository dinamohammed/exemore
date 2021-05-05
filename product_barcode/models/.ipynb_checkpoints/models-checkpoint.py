# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models, _
from odoo.exceptions import Warning,ValidationError
from odoo.osv import expression

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    attribute_line_ids = fields.One2many('product.template.attribute.line', 'product_tmpl_id',
                                         'Product Attributes', copy=False)
    
    product_ref = fields.Char('Reference',required=True, index=True,
                              copy=False, default='New', store = True, readonly = True)
    
    @api.model
    def create(self, vals):
        """
        Add new option to get sequence automatic of ref number
        :param vals:
        :return:
        """
        if vals.get('product_ref', 'New') == 'New':
#             raise ValidationError('%s'%self.env['ir.sequence'].next_by_code('contact.ref'))
            vals['product_ref'] = self.env['ir.sequence'].sudo().next_by_code('product.ref.seq') or '/'
        self._generate_product_code()
        result = super(ProductTemplate, self).create(vals)

        return result
    
    @api.onchange('seller_ids','product_ref')
    @api.depends('seller_ids','product_ref')
    def _generate_product_code(self):
        """
		Generate code of each product using it's component
        Product id from field [product id] [5 digits]
        Vendor id from field [vendor id] [4 digits]
		"""
        for template in self:
            if template.seller_ids:
                vendor_id = template.seller_ids[0].name.vendor_ref
#                 vendor_id = template.seller_ids[0].name.id
                template_id = self.search([],order='id desc', limit = 1)
#                 raise ValidationError('%s'%template_id.product_ref)
                next_id = int(template_id.product_ref) + 1
                template.barcode = '%s%s' % (str(template_id.product_ref).zfill(5), str(vendor_id).zfill(4))
#             else:
#                 template.barcode = ""
                
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    
    size_code = fields.Char(compute='_generate_product_code', size=2,
                                 help="Size Code from field [Variant Size Attribute] [2 digits]")
    color_code = fields.Char(compute='_generate_product_code', size=3,
                             help="Color Code from field [Variant Color Attribute] [3 digits]")
    color_name = fields.Char(compute='_generate_product_code')
    size_name = fields.Char(compute='_generate_product_code')
    
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
            color_attr = self.env.ref('product_barcode.product_attribute_2')
            size_attr = self.env.ref('product_barcode.product_attribute_size')
#             raise ValidationError('hhhhhh')
            if product.variant_seller_ids:
#vendor_id = product.variant_seller_ids[0].name.id
                vendor_id = product.variant_seller_ids[0].name.vendor_ref
                template_id = product.product_tmpl_id.product_ref
                
                for attr_val_line in product.product_template_attribute_value_ids:
                    if attr_val_line.attribute_id == color_attr \
                            and attr_val_line.product_attribute_value_id:
                        product.color_code = attr_val_line.product_attribute_value_id.name[:3]
                        product.color_name = attr_val_line.product_attribute_value_id.name[3:]
                    if attr_val_line.attribute_id == size_attr \
                            and attr_val_line.product_attribute_value_id:
                        product.size_code = attr_val_line.product_attribute_value_id.name[:2]
                        product.size_name = attr_val_line.product_attribute_value_id.name[2:]
            
                    if not product.color_code:
                        product.color_code = "000"
                    if not product.size_code:
                        product.size_code = "00"
                    color_code = ""
                    for word in product.color_code.split():
                        if word.isdigit():
                            color_code += word
                        
                    if product.size_code or color_code:
                        product.barcode = '%s%s%s%s' % (str(template_id).zfill(5), 
                                                               str(vendor_id).zfill(4), product.size_code.zfill(2),
                                                               color_code.zfill(3))
                    else:
                        product.barcode = '%s%s' % (template_id.zfill(5), vendor_id.zfill(4))
#             else:
#                 product.barcode = ""
    
    
    
    @api.model_create_multi
    def create(self, vals_list):
        products = super(ProductProduct, self.with_context(create_product_product=True)).create(vals_list)
        # `_get_variant_id_for_combination` depends on existing variants
        products._generate_product_code()
        self.clear_caches()
        return products

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    vendor_ref = fields.Char('Reference',required=True, index=True, copy=False,
                              default='New', store = True, readonly= True)
    
    
    @api.model
    def create(self, vals):
        if vals.get('vendor_ref', 'New') == 'New':
            if vals.get('supplier_rank'):
                vals['vendor_ref'] = self.env['ir.sequence'].sudo().next_by_code('vendor.ref.seq') or '/'
        result = super(ResPartner, self).create(vals)

        return result
