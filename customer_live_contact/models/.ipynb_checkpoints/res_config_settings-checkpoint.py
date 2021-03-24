# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    max_days_to_follow_up = fields.Integer(string="Max Days to Follow up", default=False)

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('customer_live_contact.max_days_to_follow_up',
                                                         self.max_days_to_follow_up)
        res = super(ResConfigSettings, self).set_values()
        return res

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo().get_param(
            'customer_live_contact.max_days_to_follow_up',
            self.max_days_to_follow_up)
        res.update(
            max_days_to_follow_up=param
        )
        return res

    
    
    
    
    
    
    
    
    
