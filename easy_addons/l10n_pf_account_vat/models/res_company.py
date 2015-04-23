# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class res_company(osv.osv):
	_inherit = "res.company"
	_columns = {
		'exports_ids': fields.many2many('account.account', 'account_account_exports', 'exports_id', 'account_id', 'Exports accounts'),
		'others_ids': fields.many2many('account.account', 'account_account_others', 'others_id', 'account_id', 'Others accounts'),
		
		'tax_reduced_rate_ids': fields.many2many('account.tax', 'account_tax_reduced', 'reduced_rate_id', 'tax_code_id', 'Reduced rate Taxe'),
		'tax_intermediate_rate_ids': fields.many2many('account.tax', 'account_tax_intermediate', 'intermediate_rate_id', 'tax_code_id', 'Intermediate rate Taxe'),
		'tax_normal_rate_ids': fields.many2many('account.tax', 'account_tax_normal', 'normal_rate_id', 'tax_code_id', 'Normal rate Taxe'),
		'tax_immo_ids': fields.many2many('account.tax', 'account_tax_immo', 'immo_id', 'tax_code_id', 'Immobilization Taxe'),
		'tax_others_goods_services_ids': fields.many2many('account.tax', 'account_tax_goods_services', 'others_goods_services_id', 'tax_code_id', 'Others goods and services Taxe'),
		
		'customers_ids': fields.many2many('account.account', 'account_account_customers', 'customers_id', 'account_id', 'Customers accounts'),
		
		'turnover_ids': fields.many2many('account.account', 'account_account_turnover', 'turnover_id', 'account_id', 'Turnover accounts'),
		
		'sales_ids': fields.many2many('account.account', 'account_account_sales', 'sales_id', 'account_id', 'Sales accounts'),
		'services_ids': fields.many2many('account.account', 'account_account_services', 'services_id', 'account_id', 'Services accounts'),
		
		'credit_id': fields.many2one('account.account', 'Credit accounts'),
		'vat_id': fields.many2one('account.account', 'VAT accounts'),
		
		'journal_id': fields.many2one('account.journal', 'Journal'),
		
		'period_declaration': fields.selection([('month','Month'),('trimester','Trimester')], 'Declaration period'),
		
		'bp': fields.char('BP'),
		'city_zip': fields.char('City Zip'),	
		
		'activity': fields.char('Company activity'),
		
		'regime_vat': fields.selection([('simplified', 'Simplified regime'), ('real', 'Real regime')], 'Regime Vat'),
		'type_vat': fields.selection([('cashing', 'Cashing vat'), ('bills', 'Bills vat')], 'Type vat'),
		
		'signature': fields.binary('Signature'),
	}

	#TODO: Faire une fonction qui met à None type_vat et period_declaration si on est en régime simplifié
