# -*- coding: utf-8 -*-

from openerp import models, fields


class account_move_line(models.Model):
    _inherit = "account.move.line"

    _columns = {
        'declaration_id': fields.many2one('l10n.pf.account.vat.declaration', 'Declaration VAT', help='Il s agit de la déclaration de TVA', select=1, copy=False)
    }
