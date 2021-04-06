# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError, Warning
import datetime


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
        
   ############## will be called in scheduled action to be executed daily ###########    
    def scheduled_action_function(self):
        days_to_followup = self.env['res.config.settings']
        date_to = datetime.datetime.today()
        date_from = date_to - datetime.timedelta(days = days_to_followup.max_days_to_follow_up)
        sale_transactions = self.env['sale.order'].search(['&'
                                                           ,('expected_date','>=',date_from)
                                                           ,('expected_date','<=',date_to)]).partner_id
        
        partners_to_note = self.env['res.partner'].search([('id','not in',sale_transactions.ids)])
        
        return partners_to_note
        
    #################### To view the partners to followup with ##############
    
    def action_view_customers_to_followup(self):
        partner_ids = self.scheduled_action_function()
        return {
            'name': _('Customer Followup'),
            'view_mode': 'tree',
            'res_model': 'res.partner',
            'view_id': self.env.ref('base.view_partner_tree').id,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', partner_ids.ids)],
        }
        
    ##############################################################

    @api.model
    def action_send_sms(self):
        for partner in self:
            if 'sms' in partner.contact_method_ids.code:
                return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'name': _("Send SMS Text Message"),
                    'res_model': 'sms.composer',
                    'target': 'new',
                    'views': [(False, "form")],
                    'context': {
#                         'default_body': self._get_sms_summary(options),
                        'default_res_model': 'res.partner',
                        'default_res_id': partner.id,
                        'default_composition_mode': 'comment',
                    },
                }
            
    @api.model
    def send_email(self):
        for partner in self:
            if 'email' in partner.contact_method_ids.code:
                email = partner.email
                if email and email.strip():
            # When printing we need te replace the \n of the summary by <br /> tags
                    body_html = self.with_context(print_mode=True, mail=True, lang=partner.lang or self.env.user.lang)
                    partner.with_context(mail_post_autofollow=True).message_post(
                        partner_ids=[invoice_partner.id],
                        body=body_html,
                        subject=_('%(company)s FollowUp - %(customer)s', company=self.env.company.name, customer=partner.name),
                        subtype_id=self.env.ref('mail.mt_note').id,
                        model_description=_('Followup reminder'),
                        email_layout_xmlid='mail.mail_notification_light',
                    )
                    return True
        
    @api.model
    def send_whatsapp(self):
        for partner in self:
            if 'whatsapp' in partner.contact_method_ids.code:
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Whatsapp Message'),
                    'res_model': 'whatsapp.message.wizard',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {'default_user_id': self.id},
                }
            else:
                return True

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')], required = 'True', default = 'person')
    
    

class ContactMethod(models.Model):
    _name = "contact.method"
    _description = "Contact Methods"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True) 

    
    
    
    
    
