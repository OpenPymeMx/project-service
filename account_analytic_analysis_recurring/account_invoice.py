# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

import time
from openerp import models, api
from openerp.addons.account import signals


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def re_open_contract(self):
        # Re open a contract if the overdue invoice is paid
        account_invoice_line_obj = self.env['account.invoice.line']
        current_date = time.strftime('%Y-%m-%d')
        for invoice_line in self.invoice_line:
            contract = invoice_line.account_analytic_id
            if not contract:
                continue
            invoices = account_invoice_line_obj.search_count(
                [('account_analytic_id', '=', contract.id),
                 ('invoice_id.date_due', '<=', current_date),
                 ('invoice_id.state', '=', 'open')]
            )
            if not invoices and contract.state == 'overdue':
                contract.write(
                    {'state': 'open'}
                )

    @signals.invoice_set_paid.connect
    def cath_action_paid(self, cr, uid, ids, context):
        context = dict(context or {})
        invoice = self.browse(cr, uid, ids, context)
        return invoice.re_open_contract()
