# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class res_config(osv.osv_memory):
	_inherit = 'account.config.settings'
	_columns = {
		# Factures
		'account_exports':fields.many2many('account.account','account_config_settings_exports','exports_id','account_ids', 'Account Exports'),
		'account_others': fields.many2many('account.account','account_config_setting_others','others_id','account_ids','Account Others operations'),
		'account_reduced_rate': fields.many2many('account.account','account_config_setting_reduced','reduced_id','account_ids','Account Reduced rate'),
		'account_intermediate_rate': fields.many2many('account.account','account_config_setting_intermediate','intermediate_id','account_ids','Account Intermediate rate'),
		'account_normal_rate': fields.many2many('account.account','account_config_setting_normal','normal_id','account_ids','Accout Normal rate'),
		'account_immo': fields.many2many('account.account','account_config_setting_immo','immo_id','account_ids','Account Immobilizations'),
		'account_others_goods_services': fields.many2many('account.account','account_config_setting_goods_services','goods_services_id','account_ids','Account Others goods and services'),
		# Encaissements
		'account_customers': fields.many2many('account.account','account_config_setting_customers','customers_id','account_ids','Account Customers'),
		'account_turnover': fields.many2many('account.account','account_config_setting_turnover','turnover_id','account_ids','Account Turnover' )
	}
	
	#_columns = {
		## Factures
		#'account_exports':fields.many2many('account.account','account_config_settings_exports','exports_id','account_id', 'Account Exports'),
		#'account_others': fields.char('Account Others operations'),
		#'account_reduced_rate': fields.char('Account Reduced rate'),
		#'account_intermediate_rate': fields.char('Account Intermediate rate'),
		#'account_normal_rate': fields.char('Accout Normal rate'),
		#'account_immo': fields.char('Account Immobilizations'),
		#'account_others_goods_services': fields.char('Account Others goods and services'),
		## Encaissements
		#'account_customers': fields.char('Account Customers'),
		#'account_turnover': fields.char('Account Turnover' )
	#}
