# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

class res_config(osv.osv_memory):
	_inherit = 'account.config.settings'

	_columns = {
		# Factures
		'account_exports':fields.one2many('account.account','exports_id','Account Exports'),
		#'account_exports':fields.many2many('account.account','account_config_settings_exports','exports_id','account_ids', 'Account Exports'),
		'account_others': fields.one2many('account.account','others_id','Account Others operations'),
		'account_reduced_rate': fields.one2many('account.account','reduced_rate_id','Account Reduced rate'),
		'account_intermediate_rate': fields.one2many('account.account','intermediate_rate_id','Account Intermediate rate'),
		'account_normal_rate': fields.one2many('account.account','normal_rate_id','Accout Normal rate'),
		'account_immo': fields.one2many('account.account','immo_id','Account Immobilizations'),
		'account_others_goods_services': fields.one2many('account.account','others_goods_services_id','Account Others goods and services'),
		## Encaissements
		'account_customers': fields.one2many('account.account','customers_id','Account Customers'),
		'account_turnover': fields.one2many('account.account','turnover_id','Account Turnover' ),
	}
