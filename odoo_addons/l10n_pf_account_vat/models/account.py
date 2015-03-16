# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

class account_account(osv.osv):
	_inherit = 'account.account'
	
	_columns = {
		'exports_id': fields.many2one('account.account', 'Exports'),
		'others_id': fields.many2one('account.account', 'Others' ),
		'reduced_rate_id': fields.many2one('account.account', 'Reduced rate'),
		'intermediate_rate_id': fields.many2one('account.account', 'Intermediate rate'),
		'normal_rate_id': fields.many2one('account.account', 'Normal rate'),
		'immo_id': fields.many2one('account.account', 'Immo id'),
		'others_goods_services_id': fields.many2one('account.account', 'Goods and services'),
		'customers_id': fields.many2one('account.account', 'Customers'),
		'turnover_id': fields.many2one('account.account', 'Turnover')
	}
