# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    contact_method_ids = fields.Many2many('contact.method','contact_method_res_partner_rel','partner_id','contact_method_id'
                                          ,string='Contacting Methods')
    
    @api.onchange('company_type')
    def onchange_company_type_pricelist(self):
        for contact in self:
            if contact.company_type != contact.property_product_pricelist:
                raise ValidationError('You must change the Pricelist to be with the same Type (Individual/Company)')
             return {
            'warning': {'title': _("Warning"),
                        'message': _("It is preferable to change the Accounts of this Contact..")},
             }
    

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company'), required = 'True'])
    
    

class contactmethod(models.Model):
    _name = "contact.method"
    _description = "Contact Methods"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True) 

    
    
    
    
    
