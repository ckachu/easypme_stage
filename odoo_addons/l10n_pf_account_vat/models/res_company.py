# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class res_company(osv.osv):
	_inherit = "res.company"
	_columns = {
		'bp': fields.char('BP'),
		'city_zip': fields.char('City Zip'),	
		'activity': fields.char('Company activity'),
		'regime_vat': fields.selection([('deposit','Deposit in simplified regime'),('annual','Annual in simplified regime'),('real','Real regime')], 'Regime Vat'),
		'type_vat': fields.selection([('cashing','Cashing vat'),('bills','Bills vat')],'Type vat'),
		'exports_ids': fields.one2many('account.account', 'exports_id', 'Exports accounts'),
		'others_ids': fields.one2many('account.account', 'others_id', 'Others accounts'),
		'reduced_rate_ids': fields.one2many('account.account', 'reduced_rate_id', 'Reduced rate accounts'),
		'intermediate_rate_ids': fields.one2many('account.account', 'intermediate_rate_id', 'Intermediate rate accounts'),
		'normal_rate_ids': fields.one2many('account.account', 'normal_rate_id', 'Normal rate accounts'),
		'immo_ids': fields.one2many('account.account', 'immo_id', 'Immo accounts'),
		'others_goods_services_ids': fields.one2many('account.account', 'others_goods_services_id', 'Others goods and services accounts'),
		'customers_ids': fields.one2many('account.account', 'customers_id', 'Customers accounts'),
		'turnover_ids': fields.one2many('account.account', 'turnover_id', 'Turnover accounts'),
		'reduced_rate': fields.float('Reduced rate'),
		'intermediate_rate': fields.float('Intermediate rate'),
		'normal_rate': fields.float('Normal rate')
	}
	_defaults = {
		'reduced_rate': 5.0,
		'intermediate_rate': 13.0,
		'normal_rate': 16.0
	}
