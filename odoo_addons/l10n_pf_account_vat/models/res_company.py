# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class res_company(osv.osv):
	_inherit = "res.company"
	_columns = {
		#'toto': fields.many2one('account.account', 'Toto'),
		'exports_ids': fields.many2many('account.account', 'account_account_exports', 'exports_id', 'account_id', 'Exports accounts'),
		'others_ids': fields.many2many('account.account', 'account_account_others', 'others_id', 'account_id', 'Others accounts'),
		'reduced_rate_ids': fields.many2many('account.account', 'account_account_reduced', 'reduced_rate_id', 'account_id', 'Reduced rate accounts'),
		'intermediate_rate_ids': fields.many2many('account.account', 'account_account_intermediate', 'intermediate_rate_id', 'account_id', 'Intermediate rate accounts'),
		'normal_rate_ids': fields.many2many('account.account', 'account_account_normal', 'normal_rate_id', 'account_id', 'Normal rate accounts'),
		'immo_ids': fields.many2many('account.account', 'account_account_immo', 'immo_id', 'account_id', 'Immo accounts'),
		'others_goods_services_ids': fields.many2many('account.account', 'account_account_goods_services', 'others_goods_services_id', 'account_id', 'Others goods and services accounts'),
		'customers_ids': fields.many2many('account.account', 'account_account_customers', 'customers_id', 'account_id', 'Customers accounts'),
		'turnover_ids': fields.many2many('account.account', 'account_account_turnover', 'turnover_id', 'account_id', 'Turnover accounts'),
		
		'bp': fields.char('BP'),
		'city_zip': fields.char('City Zip'),	
		'activity': fields.char('Company activity'),
		'regime_vat': fields.selection([('deposit','Deposit in simplified regime'),('annual','Annual in simplified regime'),('real','Real regime')], 'Regime Vat'),
		'type_vat': fields.selection([('cashing','Cashing vat'),('bills','Bills vat')],'Type vat'),
		'reduced_rate': fields.float('Reduced rate'),
		'intermediate_rate': fields.float('Intermediate rate'),
		'normal_rate': fields.float('Normal rate')
	}
	_defaults = {
		'reduced_rate': 5.0,
		'intermediate_rate': 13.0,
		'normal_rate': 16.0
	}
