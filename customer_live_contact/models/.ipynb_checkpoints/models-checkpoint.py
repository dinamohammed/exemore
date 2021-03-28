# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError, Warning


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    contact_method_ids = fields.Many2many('contact.method','contact_method_res_partner_rel','partner_id','contact_method_id'
                                          ,string='Contacting Methods')
    
    @api.onchange('company_type')
    def onchange_company_type_pricelist(self):
        res = {}
        for contact in self:
            res['warning'] = {
                'title':_('Small Hint'),
                'message': _("It is preferable to change the Accounts of this Contact..")}
            contact.is_company = (contact.company_type == 'company')
            if contact.property_product_pricelist:
                if contact.company_type != contact.property_product_pricelist.company_type:
                    raise ValidationError('You must change the Pricelist to be with the same Type (Individual/Company)'
                                          + '\n'
                                          + 'and Accounts of current Contact..')
            return res

    

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')], required = 'True', default = 'person')
    
    

class ContactMethod(models.Model):
    _name = "contact.method"
    _description = "Contact Methods"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True) 

    
    
    
    
    
