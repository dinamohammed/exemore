# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError


class ExpenseType(models.Model):
    _name = 'expense.type'
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    account_id = fields.Many2one('account.account','Account')
    
    
class ExpenseExpense(models.Model):
    _name = 'expense.expense'
    
    name = fields.Char('Reference')
    expense_type = fields.Many2one('expense.type','Expense Type')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Validated'), ('sent', 'Sent')], 
                             readonly=True, default='draft', copy=False, string="Status")
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry', readonly=True, ondelete='cascade',
        check_company=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, tracking=True, 
                                 domain="[('type', 'in', ('bank', 'cash'))]")
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        compute='_compute_currency_id',
        help="The Expense's currency.")

    amount = fields.Monetary('Amount', currency_field='currency_id')
    date = fields.Date('Date',default= datetime.today())
    partner_id = fields.Many2one('res.partner', string="Contact")

    
    
    @api.depends('journal_id')
    def _compute_currency_id(self):
        for pay in self:
            pay.currency_id = pay.journal_id.currency_id or pay.journal_id.company_id.currency_id
            
    def _get_default_journal(self):
        ''' Retrieve the default journal for the account.payment.
        /!\ This method will not override the method in 'account.move' because the ORM
        doesn't allow overriding methods using _inherits. Then, this method will be called
        manually in 'create' and 'new'.
        :return: An account.journal record.
        '''
        return self.env['account.move']._search_default_journal(('bank', 'cash'))
    
    def _prepare_move_line(self):
        for rec in self:
            debit = credit = rec.currency_id.compute(rec.amount, rec.currency_id)
#             raise ValidationError('%s'%debit)
            sequence_code = 'hr.advance.sequence'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.date).next_by_code(sequence_code)
            move = {
             'name': '/',
             'journal_id': rec.journal_id.id,
             'date': datetime.today(),
 
             'line_ids': [(0, 0, {
                     'name': rec.name or '/',
                     'debit': debit,
                     'account_id': rec.expense_type.account_id.id,
                     'partner_id': self.partner_id.id or self.env.user.partner_id.id,
                 }), (0, 0, {
                     'name': rec.name or '/',
                     'credit': credit,
                     'account_id': rec.journal_id.default_account_id.id,
                     'partner_id': self.partner_id.id or self.env.user.partner_id.id,
                 })]
            }
            move_id = self.env['account.move'].create(move)
            return rec.write({ 'move_id': move_id.id})
        
    
    
    
    def button_confirm(self):
        ''' draft -> posted '''
        self._prepare_move_line()
        self.move_id._post(soft=False)
        self.write({'state':'posted'})
        

        
class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    
    expense_id = fields.Many2one('expense.expense', string="Expense Ref", copy=False)