# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

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

class l10n_pf_account_vat_declaration(osv.osv):
	_name = 'l10n.pf.account.vat.declaration'
	_description = 'Vat declaration'
	
	_inherit = 'account.chart','account.account'
	
	#def action_fill_declaration(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#self.pool.get('account.chart').account_chart_open_window(cr, uid, ids, context)
	
	#def _get_balance(self, cr, uid, id, field_names, args, context=None):
		#account_obj = self.pool.get('account.account')
		#res = {}
		#for report in self.browse(cr, uid, ids, context=context):
			#if report.id in res:
				#continue
			#res[report.id] = dict((fn, 0.0) for fn in field_names)
			#if report.type == 'accounts':
				#for a in report.account_ids:
					#for field in field_names:
						#res[report.id][field] += getattr(a, field)
			#elif report.type == 'account_type':
				#report_types = [x.id for x in report.account_type_ids]
				#account_ids = account_obj.search(cr, uid, [('user_type','in',report_types), ('type','!=','view')], context=context)
				#for a in account_obj.browse(cr, uid, account_ids, context=context):
					#for field in field_names:
						#res[report.id][field] += getattr(a, field)
			#elif report.type == 'account_report' and report.account_report_id:
				#res2 = self._get_balance(cr, uid, [report.account_report_id.id], field_names, False, context=context)
				#for key, value in res2.items():
					#for field in field_names:
						#res[report.id][field] += value[field]
			#elif report.type == 'sum':
				#res2 = self._get_balance(cr, uid, [rec.id for rec in report.children_ids], field_names, False, context=context)
				#for key, value in res2.items():
					#for field in field_names:
						#res[report.id][field] += value[field]
	
						
	_columns = {

		#'toto': fields.function(tutu, 'Toto'),
		
		'name': fields.char('Declaration name'),
		'date_declaration': fields.date('Declaration date'),
		
		'account_id': fields.many2one('account.account', 'Account'),
		
		'no_tahiti': fields.char('No Tahiti'),
		'company_id': fields.many2one('res.company','Company',required=True),
		'company_activity': fields.char('Activity'),
		'company_phone': fields.char('Telephone'),
		'company_street': fields.char('Street'),
		'company_city': fields.char('City'),
		'company_country': fields.char('Country'),
		'company_email': fields.char('Email'),
		'company_zip': fields.char('ZIP'),
		'company_bp': fields.char('BP'),
		'city_zip': fields.char('City ZIP'),
		'company_regime': fields.selection([('deposit','Deposit in simplified regime'),('annual','Annual in simplified regime'),('real','Real regime')], 'Regime'),
		'company_vat_type': fields.selection([('cashing','Cashing vat'),('bills','Bills vat')],'Type VAT'),
		
		'user_id': fields.many2one('res.users','Responsible',required=True),
		
		'account_sales': fields.float('Sales'),
		'account_services': fields.float('Services'),
		'account_exports': fields.float('Exports'),
		'account_other': fields.float('Other'),
		
		'base_reduced_rate': fields.float('Base reduced rate'),
		'base_intermediate_rate': fields.float('Base intermediate rate'),
		'base_normal_rate': fields.float('Base normal rate'),
		'base_regularization_to_donate': fields.float('Base regularization to donate'),
		
		'vat_due_reduced_rate': fields.float('Vat due reduced rate'),
		'vat_due_intermediate_rate': fields.float('Vat due intermediate rate'),
		'vat_due_normal_rate': fields.float('Vat due normal rate'),
		'vat_due_regularization_to_donate': fields.float('Vat due regularization to donate'),
		'total_vat_payable': fields.float('Total vat payable'),
		
		'vat_immobilization': fields.float('Vat immobilization'),
		'vat_other_goods_services': fields.float('Vat other goods and services'),
		'vat_regularization': fields.float('Regularization'),
		'defferal_credit': fields.float('Defferal credit'),
		'total_vat_deductible': fields.float('Total vat deductible'),
		
		'vat_credit': fields.float('Vat credit'),
		'reimbursement': fields.float('Reimbursement'),
		'credit_to_be_transferred': fields.float('Credit to be transferred'),
		'net_vat_due': fields.float('Net vat due'),
		
		'excluding_vat_sales': fields.float('Excluding vat sales'),
		'excluding_vat_services': fields.float('Excluding vat services'),
		'tax_due_sales': fields.float('Tax due sales'),
		'tax_due_services': fields.float('Tax due services'),
		'total_tax_payable': fields.float('Total tax payable'),
		
		'difference_deductible_payable': fields.float('Difference'),
		'deposit': fields.float('Deposit'),
		'total_difference_deposit': fields.float('Total'),
		'surplus': fields.float('Surplus'),
		'difference_payable_deductible': fields.float('Difference'),
		'obtained_reimbursement': fields.float('Reimbursement obtained'),
		'total_difference_reimbursement': fields.float('Total'),
		
		'net_to_pay': fields.float('Net to pay'),
		
		'date': fields.date('Signature Date', required=True),
		'place': fields.char('Signature Place', required=True),
		'means_of_payment': fields.selection([('check','Check'),('cash','Cash'),('transfert','Transfert')], 'Means of payment', required=True),
		
		
		'state': fields.selection([('draft','Draft'),('simulate','Simulate'),('done','Done')], 'Status', required=True, copy=False)
	}
	_defaults = {
		'date_declaration': lambda obj, cr, uid, context: time.strftime('%Y-%m-%d'),
		'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'l10n.pf.account.vat.declaration', context=context),
		'means_of_payment': 'check',
		'target_move': 'all',
		'state': 'draft'
	}
	
	
	
	## Cette méthode met l'état de la déclaration à "Simuler"
	def set_to_simulate(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'simulate'}, context=context)
	
	## Cette méthode met l'état de la déclaration à "Brouillon"
	def set_to_draft(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'draft'}, context=context)
	
	## Cette méthode valide la déclaration et met son état à "Valider" 
	def validate(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		return self.write(cr, uid, ids, {'state':'done'}, context)
	
	## Cette méthode récupère les informations de l'entreprise	
	def on_change_company_id(self, cr, uid, ids, company_id, context=None):
		values = {}
		if company_id:
			company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
			
			values = {
				'company_activity': company.activity,
				'company_phone': company.phone,
				'company_street': company.street,
				'company_city': company.city,
				'company_country': company.country_id.name,
				'company_email': company.email,
				'company_zip': company.zip,
				'company_bp': company.bp,
				'city_zip': company.city_zip,
				'company_regime': company.regime_vat,
				'company_vat_type': company.type_vat,
			}
		return {'value':values}
	
	#def action_fill_declaration(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#self.pool.get('account.chart').account_chart_open_window(cr, uid, ids, context)
		
		
	
	
	
	#def on_change_company_id(self, cr, uid, ids, company_id, context=None):
		#if company_id:
			#company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
			#return {'value':{
				#'company_regime':company.regime_vat,
				#'company_vat_type':company.type_vat}}
		#return {'value':{}}
	
	#def action_fill_declaration(self, cr, uid, ids, context=None):
	#	""" Cette méthode remplit les champs du formulaire.
	#	Pour cela, elle doit d'abord appeler une fonction qui calcule les balances
	#	dont on a besoin puis les met dans les champs correspondants.
	#	Par la suite, elle effectue les calculs des champs restants.
	#	"""
		
		
	
	
	
