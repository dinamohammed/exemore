# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    max_days_to_follow_up = fields.Integer(string="Max Days to Follow up")
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['max_days_to_follow_up'] = self.env['ir.config_parameter'].\
                                       get_param('max_days_to_follow_up', default= 0)
        return res

    def set_values(self):
        self.max_days_to_follow_up and self.env['ir.config_parameter'].\
            set_param('max_days_to_follow_up', self.max_days_to_follow_up)
        super(ResConfigSettings, self).set_values()

    
    
    
    
    
    
    
    
    
