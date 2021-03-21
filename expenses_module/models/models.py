# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ExpenseType(models.Model):
    _name = 'expense.type'
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    account_id = fields.Many2one('account.account','Account')
    
    
class ExpenseExpense(models.Model):
    _name = 'expense.expense'
    
    expense_type = fields.Many2one('expense.type','Expense Type')
    journal_id = fields.Many2one('account.journal','Journal')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Validated'), ('sent', 'Sent')], 
                             readonly=True, default='draft', copy=False, string="Status")
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry', required=True, readonly=True, ondelete='cascade',
        check_company=True)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        compute='_compute_currency_id',
        help="The Expense's currency.")
    
    
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
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        write_off_line_vals_list = []

        for vals in vals_list:

            # Hack to add a custom write-off line.
            write_off_line_vals_list.append(vals.pop('write_off_line_vals', None))

            # Force the move_type to avoid inconsistency with residual 'default_move_type' inside the context.
            vals['move_type'] = 'entry'

            # Force the computation of 'journal_id' since this field is set on account.move but must have the
            # bank/cash type.
            if 'journal_id' not in vals:
                vals['journal_id'] = self._get_default_journal().id

            # Since 'currency_id' is a computed editable field, it will be computed later.
            # Prevent the account.move to call the _get_default_currency method that could raise
            # the 'Please define an accounting miscellaneous journal in your company' error.
            if 'currency_id' not in vals:
                journal = self.env['account.journal'].browse(vals['journal_id'])
                vals['currency_id'] = journal.currency_id.id or journal.company_id.currency_id.id

        payments = super().create(vals_list)

        for i, pay in enumerate(payments):
            write_off_line_vals = write_off_line_vals_list[i]

            # Write payment_id on the journal entry plus the fields being stored in both models but having the same
            # name, e.g. partner_bank_id. The ORM is currently not able to perform such synchronization and make things
            # more difficult by creating related fields on the fly to handle the _inherits.
            # Then, when partner_bank_id is in vals, the key is consumed by account.payment but is never written on
            # account.move.
            to_write = {'expense_id': pay.id}
            for k, v in vals_list[i].items():
                if k in self._fields and self._fields[k].store and k in pay.move_id._fields and pay.move_id._fields[k].store:
                    to_write[k] = v

            if 'line_ids' not in vals_list[i]:
                to_write['line_ids'] = [(0, 0, line_vals) for line_vals in pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)]

            pay.move_id.write(to_write)

        return payments
    
    
    
    
    def button_confirm(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)
        

        
class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    
    expense_id = fields.Many2one('expense.expense', string="Expense Ref", copy=False)