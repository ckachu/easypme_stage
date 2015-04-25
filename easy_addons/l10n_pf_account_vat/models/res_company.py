# -*- coding: utf-8 -*-

from openerp import models, fields


class res_company(models.Model):
    _inherit = "res.company"

    exports_ids = fields.Many2many('account.account', 'account_account_exports', 'exports_id', 'account_id', 'Exports accounts')
    others_ids = fields.Many2many('account.account', 'account_account_others', 'others_id', 'account_id', 'Others accounts')
    tax_reduced_rate_ids = fields.Many2many('account.tax', 'account_tax_reduced', 'reduced_rate_id', 'tax_code_id', 'Reduced rate Taxe')
    tax_intermediate_rate_ids = fields.Many2many('account.tax', 'account_tax_intermediate', 'intermediate_rate_id', 'tax_code_id', 'Intermediate rate Taxe')
    tax_normal_rate_ids = fields.Many2many('account.tax', 'account_tax_normal', 'normal_rate_id', 'tax_code_id', 'Normal rate Taxe')
    tax_immo_ids = fields.Many2many('account.tax', 'account_tax_immo', 'immo_id', 'tax_code_id', 'Immobilization Taxe')
    tax_others_goods_services_ids = fields.Many2many('account.tax', 'account_tax_goods_services', 'others_goods_services_id', 'tax_code_id', 'Others goods and services Taxe')
    customers_ids = fields.Many2many('account.account', 'account_account_customers', 'customers_id', 'account_id', 'Customers accounts')
    turnover_ids = fields.Many2many('account.account', 'account_account_turnover', 'turnover_id', 'account_id', 'Turnover accounts')
    sales_ids = fields.Many2many('account.account', 'account_account_sales', 'sales_id', 'account_id', 'Sales accounts')
    services_ids = fields.Many2many('account.account', 'account_account_services', 'services_id', 'account_id', 'Services accounts')
    credit_id = fields.Many2one('account.account', 'Credit accounts')
    vat_id = fields.Many2one('account.account', 'VAT accounts')
    journal_id = fields.Many2one('account.journal', 'Journal')
    period_declaration = fields.Selection([('month', 'Month'), ('trimester', 'Trimester')], 'Declaration period')
    bp = fields.Char('BP')
    city_zip = fields.Char('City Zip')
    activity = fields.Char('Company activity')
    regime_vat = fields.Selection([('simplified', 'Simplified regime'), ('real', 'Real regime')], 'Regime Vat')
    type_vat = fields.Selection([('cashing', 'Cashing vat'), ('bills', 'Bills vat')], 'Type vat')

    def on_change_regime_vat(self, cr, uid, ids, regime_vat, context=None):
        values = {}
        if regime_vat == 'simplified':
            values = {
                'type_vat': None,
                'period_declaration': None,
            }

        return {'value': values}
