# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

import openerp.addons.decimal_precision as dp

from openerp.osv import fields, osv
from openerp import models, api, _

class l10n_pf_account_vat_declaration(osv.osv):
	_name = 'l10n.pf.account.vat.declaration'
	_description = 'Vat declaration'

	def _get_fiscalyear(self, cr, uid, context=None):
		return self.pool.get('account.fiscalyear').find(cr, uid, context=context)

	def account_chart_open_window(self, cr, uid, ids, context=None):
		import pdb
		pdb.set_trace()
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		period_obj = self.pool.get('account.period')
		fy_obj = self.pool.get('account.fiscalyear')
		if context is None:
			context = {}
		data = self.read(cr, uid, ids, context=context)[0]
		result = mod_obj.get_object_reference(cr, uid, 'account', 'action_account_tree')
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		fiscalyear_id = data.get('fiscalyear', False) and data['fiscalyear'][0] or False
		result['periods'] = []
		if data['period_from'] and data['period_to']:
			period_from = data.get('period_from', False) and data['period_from'][0] or False
			period_to = data.get('period_to', False) and data['period_to'][0] or False
			result['periods'] = period_obj.build_ctx_periods(cr, uid, period_from, period_to)
		result['context'] = str({'fiscalyear': fiscalyear_id, 'periods': result['periods'], \
		'state': data['target_move']})
		if fiscalyear_id:
			result['name'] += ':' + fy_obj.read(cr, uid, [fiscalyear_id], context=context)[0]['code']
		return result

	def action_fill_declaration(self, cr, uid, ids, context=None):
		import pdb
		pdb.set_trace()
		if context is None:
			context = {}
		for field in ['exports_ids', 'others_ids', 'reduced_rate_ids', 'intermediate_rate_ids', 'normal_rate_ids', 'immo_ids', 'others_goods_services_ids', 'sales_ids', 'services_ids', 'credit_ids', 'deposit']:
			res = 0.0
			if self.browse(cr, uid, ids, context=context).company_regime == 'deposit':
				if field == 'sales_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.sales_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'excluding_vat_sales': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'excluding_vat_sales': -res})
				elif field == 'services_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.services_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'excluding_vat_services': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'excluding_vat_services': -res})
				elif field == 'immo_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.immo_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'vat_immobilization': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'vat_immobilization': -res})
				elif field == 'credit_ids':
					pdb.set_trace()
					search_ids = self.search(cr, uid, [('company_regime','=','deposit'),('state','=','done')])
					for obj in self.browse(cr, uid, search_ids, context=context):
						d1 = datetime.strptime(self.browse(cr, uid, ids, context=context).date_declaration, '%Y-%m-%d')
						d2 = datetime.strptime(obj.date_declaration, '%Y-%m-%d')
						if (str(d1.year) == str(d2.year + 1)):
							self.browse(cr, uid, ids, context=context).update({'defferal_credit': obj.vat_credit})
							print obj.vat_credit
			elif (self.browse(cr, uid, ids, context=context).company_regime == 'annual' or (self.browse(cr, uid, ids, context=context).company_regime == 'real' and self.browse(cr, uid, ids, context=context).company_vat_type == 'bills')):
				if field == 'exports_ids':
					for i in  self.browse(cr, uid, ids, context=context).company_id.exports_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'account_exports': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'account_exports': -res})
				elif field == 'others_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.others_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'account_other': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'account_other': -res})
				elif field == 'reduced_rate_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.reduced_rate_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'vat_due_reduced_rate': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'vat_due_reduced_rate': -res})
				elif field == 'intermediate_rate_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.intermediate_rate_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'vat_due_intermediate_rate': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'vat_due_intermediate_rate': -res})
				elif field == 'normal_rate_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.normal_rate_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'vat_due_normal_rate': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'vat_due_normal_rate': -res})
				elif field == 'immo_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.immo_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'vat_immobilization': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'vat_immobilization': -res})
				elif field == 'others_goods_services_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.others_goods_services_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'vat_other_goods_services': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'vat_other_goods_services': -res})
				elif field == 'deposit':
					pdb.set_trace()
					search_ids = self.search(cr, uid, [('company_regime','=','deposit')])
					print search_ids
				elif field == 'credit_ids':
					pdb.set_trace()
					search_ids = self.search(cr, uid, [('company_regime', 'in', ('annual','real'))])
					print search_ids
					for obj in self.browse(cr, uid, search_ids, context=context):
						if self.browse(cr, uid, ids, context=context).company_regime == 'annual':
							d1 = datetime.strptime(self.browse(cr, uid, ids, context=context).period_to.date_start, '%Y-%m-%d')
							d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
							if (str(d1.year) == str(d2.year + 1)) and (obj.state == 'done') and (self.browse(cr, uid, ids, context=context).company_regime == obj.company_regime):
								self.browse(cr, uid, ids, context=context).update({'defferal_credit': obj.credit_to_be_transferred})
								print obj.credit_to_be_transferred
						elif (self.browse(cr, uid, ids, context=context).company_regime == 'real') and (self.browse(cr, uid, ids, context=context).company_vat_type == 'bills'):
							d1 = datetime.strptime(self.browse(cr, uid, ids, context=context).period_to.date_start, '%Y-%m-%d')
							d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
							if str(d1.year) == str(d2.year + 1):
								if ((str(d1.month) == str(d2.month - 11)) or (str(d1.month) == str(d2.month - 9))) and (obj.state == 'done') and (self.browse(cr, uid, ids, context=context).company_regime == obj.company_regime) and (self.browse(cr, uid, ids, context=context).company_vat_type == obj.company_vat_type):
									self.browse(cr, uid, ids, context=context).update({'defferal_credit': obj.credit_to_be_transferred})
									print obj.credit_to_be_transferred
							else:
								if ((str(d1.month - 1) == str(d2.month)) or (str(d1.month) == str(d2.month + 3))) and (obj.state == 'done') and (self.browse(cr, uid, ids, context=context).company_regime == obj.company_regime) and (self.browse(cr, uid, ids, context=context).company_vat_type == obj.company_vat_type):
									self.browse(cr, uid, ids, context=context).update({'defferal_credit': obj.credit_to_be_transferred})
									print obj.credit_to_be_transferred
			elif (self.browse(cr, uid, ids, context=context).company_regime == 'real' and self.browse(cr, uid, ids, context=context).company_vat_type == 'cashing'):
				if field == 'exports_ids':
					for i in  self.browse(cr, uid, ids, context=context).company_id.exports_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'account_exports': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'account_exports': -res})
				elif field == 'others_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.others_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'account_other': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'account_other': -res})	
				elif field == 'intermediate_rate_ids':
					compte_client_n = 0.0
					chiffre_n = 0.0
					taux_inter_n = 0.0
					compte_client_n_1 = 0.0					
					# on recupere le montant du 411 pour l'annee N
					for i in self.browse(cr, uid, ids, context=context).company_id.customers_ids:
						compte_client_n = compte_client_n + i.balance
					# on recupere le montant du 706 pour l'annee N
					for i in self.browse(cr, uid, ids, context=context).company_id.turnover_ids:
						chiffre_n = chiffre_n + i.balance
					# on  recupere le montant du taux intermédiaire pour l'annee N
					for i in self.browse(cr, uid, ids, context=context).company_id.intermediate_rate_ids:
						taux_inter_n = taux_inter_n + i.balance
					# on recupere la balance 411 dans la periode d'ouverture de l'annee N 
					context_prev = {
						'fiscalyear': self.browse(cr, uid, ids, context=context).fiscalyear.id,
						'period_from': self.browse(cr, uid, ids, context=context).period_from.id,
						'period_to': self.browse(cr, uid, ids, context=context).period_from.id,
						'target_move': self.browse(cr, uid, ids, context=context).target_move
					}
					for i in self.browse(cr, uid, ids, context=context_prev).company_id.customers_ids:
						compte_client_n_1 = compte_client_n_1 + i.balance
					# Calcul du montant TTC
					ttc = compte_client_n_1 + chiffre_n + taux_inter_n - compte_client_n
					# Calcul du montant HT
					ht = ttc / 1.13
					# Calcul du montant de la prestation à déclarer
					prestation = ht
					self.browse(cr, uid, ids, context=context).update({'base_intermediate_rate': prestation})
					# Calcul du montant de la TVA due de la prestation
					res = ht * 0.13
					self.browse(cr, uid, ids, context=context).update({'vat_due_intermediate_rate': res})
				elif field == 'immo_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.immo_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'vat_immobilization': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'vat_immobilization': -res})
				elif field == 'others_goods_services_ids':
					for i in self.browse(cr, uid, ids, context=context).company_id.others_goods_services_ids:
						res = res + i.balance
						print res
					if res >= 0:
						self.browse(cr, uid, ids, context=context).update({'vat_other_goods_services': res})
					else:
						self.browse(cr, uid, ids, context=context).update({'vat_other_goods_services': -res})
				elif field == 'credit_ids':
					pdb.set_trace()
					search_ids = self.search(cr, uid, [('company_regime','=','real'),('company_vat_type','=','cashing')])
					print search_ids
					for obj in self.browse(cr, uid, search_ids, context=context):
						d1 = datetime.strptime(self.browse(cr, uid, ids, context=context).period_to.date_start, '%Y-%m-%d')
						d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
						if ((str(d1.month) == str(d2.month + 1)) or (str(d1.month) == str(d2.month + 3))) and (obj.state == 'done') and (self.browse(cr, uid, ids, context=context).company_regime == obj.company_regime) and (self.browse(cr, uid, ids, context=context).company_vat_type == obj.company_vat_type):
							self.browse(cr, uid, ids, context=context).update({'defferal_credit': obj.credit_to_be_transferred})
							print obj.credit_to_be_transferred
							
		return self.browse(cr, uid, ids, context=context)
	
	## Cette fonction calcule le montant des bases hors TVA
	@api.one
	@api.depends('vat_due_reduced_rate','vat_due_intermediate_rate','vat_due_normal_rate','company_id','company_vat_type')
	def _compute_amount_base(self):
		if self.company_vat_type == 'cashing':
			self.base_reduced_rate = 0.0
			self.base_intermediate_rate = self.vat_due_intermediate_rate / (self.company_id.intermediate_rate / 100.0)
			self.base_normal_rate = 0.0
		else:
			self.base_reduced_rate = self.vat_due_reduced_rate / (self.company_id.reduced_rate / 100.0)
			self.base_intermediate_rate = self.vat_due_intermediate_rate / (self.company_id.intermediate_rate / 100.0)
			self.base_normal_rate = self.vat_due_normal_rate / (self.company_id.normal_rate / 100.0)

	## Cette fonction calcule le total de la TVA exigible des régimes annuel simplifié et réel selon le type de TVA
	@api.one
	@api.depends('vat_due_reduced_rate','vat_due_intermediate_rate','vat_due_normal_rate','vat_due_regularization_to_donate','company_vat_type')
	def _compute_total_due(self):
		if self.company_vat_type == 'cashing':
			self.total_vat_payable = self.vat_due_intermediate_rate + self.vat_due_regularization_to_donate
		else:
			self.total_vat_payable = self.vat_due_reduced_rate + self.vat_due_intermediate_rate + self.vat_due_normal_rate + self.vat_due_regularization_to_donate

	## Cette fonction calcule le total de la taxe due de l'acompte en régime simplifié
	@api.one
	@api.depends('tax_due_sales','tax_due_services')
	def _compute_total_taxe_due(self):
		self.total_tax_payable = self.tax_due_sales + self.tax_due_services

	## Cette fonction calcule le total de la TVA déductible selon le type de régime
	@api.one
	@api.depends('company_regime','vat_immobilization','vat_other_goods_services','vat_regularization','defferal_credit')
	def _compute_total_deductible(self):
		if self.company_regime == 'deposit':
			self.total_vat_deductible = self.vat_immobilization + self.defferal_credit
		else:
			self.total_vat_deductible = self.vat_immobilization + self.vat_other_goods_services + self.vat_regularization + self.defferal_credit

	## Cette fonction calcule le montant de la TVA ou du crédit de TVA selon les cas
	@api.one
	@api.depends('total_vat_payable','total_vat_deductible','total_tax_payable','company_regime')
	def _compute_amount_vat(self):
		diff1 = self.total_tax_payable - self.total_vat_deductible
		diff2 = self.total_vat_payable - self.total_vat_deductible

		if self.company_regime == 'deposit':
			if diff1 > 0:
				self.net_vat_due = self.total_tax_payable - self.total_vat_deductible
				self.vat_credit = 0.0
			else:
				self.vat_credit = self.total_vat_deductible - self.total_tax_payable
				self.net_vat_due = 0.0
		else:
			if diff2 > 0:
				self.net_vat_due = self.total_vat_payable - self.total_vat_deductible
				self.vat_credit = 0.0
			else:
				self.vat_credit = self.total_vat_deductible - self.total_vat_payable
				self.net_vat_due = 0.0

	## Cette fonction calcule le montant du crédit à reporter
	@api.one
	@api.depends('vat_credit','reimbursement','surplus','company_regime')
	def _compute_credit_to_reported(self):
		if self.company_regime == 'annual':
			self.credit_to_be_transferred = self.surplus - self.reimbursement
		else:
			self.credit_to_be_transferred = self.vat_credit - self.reimbursement

	## Régime annuel simplifié
	@api.one
	@api.depends('total_vat_payable','total_vat_deductible','deposit','obtained_reimbursement')
	def _compute_total_difference(self):
		diff = self.total_vat_payable - self.total_vat_deductible
		# TVA A PAYER
		if diff > 0:
			self.difference_payable_deductible = diff
			self.difference_deductible_payable = 0.0
			self.total_difference_deposit = self.difference_deductible_payable + self.deposit
			self.total_difference_reimbursement = self.difference_payable_deductible + self.obtained_reimbursement
			self.net_to_pay = self.total_difference_reimbursement - self.total_difference_deposit
			self.surplus = 0.0
		# CREDIT
		else:
			self.difference_deductible_payable = diff
			self.difference_payable_deductible = 0.0
			self.total_difference_deposit = self.difference_deductible_payable + self.deposit
			self.total_difference_reimbursement = self.difference_payable_deductible + self.obtained_reimbursement
			self.surplus = self.total_difference_deposit - self.total_difference_reimbursement
			self.net_to_pay = 0.0

	@api.one
	@api.depends('excluding_vat_sales','excluding_vat_services')
	def _compute_tax_due(self):
		self.tax_due_sales = self.excluding_vat_sales * 0.05
		self.tax_due_services = self.excluding_vat_services * 0.05

	@api.one
	@api.depends('base_reduced_rate', 'base_intermediate_rate', 'base_normal_rate', 'base_regularization_to_donate', 'company_vat_type', 'company_regime')
	def _compute_amount_transaction(self):
		if self.company_vat_type == 'cashing' and self.company_regime == 'real':
			self.account_services = self.base_intermediate_rate
		elif self.company_regime == 'annual' or (self.company_regime == 'real' and self.company_vat_type == 'bills'):
			self.account_sales = self.base_reduced_rate + self.base_normal_rate
			self.account_services = self.base_intermediate_rate
		
	_columns = {
		'name': fields.char('Declaration name', required=True, states={'done':[('readonly',True)]}),
		'date_declaration': fields.date('Declaration date', states={'done':[('readonly',True)]}),
		'account_id': fields.many2one('account.account', 'Account'),

		'no_tahiti': fields.char('No Tahiti', states={'done':[('readonly',True)]}),
		'company_id': fields.many2one('res.company','Company',required=True, states={'done':[('readonly',True)]}),
		'company_activity': fields.char('Activity', states={'done':[('readonly',True)]}),
		'company_phone': fields.char('Telephone', states={'done':[('readonly',True)]}),
		'company_street': fields.char('Street', states={'done':[('readonly',True)]}),
		'company_city': fields.char('City', states={'done':[('readonly',True)]}),
		'company_country': fields.char('Country', states={'done':[('readonly',True)]}),
		'company_email': fields.char('Email', states={'done':[('readonly',True)]}),
		'company_zip': fields.char('ZIP', states={'done':[('readonly',True)]}),
		'company_bp': fields.char('BP', states={'done':[('readonly',True)]}),
		'city_zip': fields.char('City ZIP', states={'done':[('readonly',True)]}),
		'company_regime': fields.selection([('deposit','Deposit in simplified regime'),('annual','Annual in simplified regime'),('real','Real regime')], 'Regime', states={'done':[('readonly',True)]}),
		'company_vat_type': fields.selection([('cashing','Cashing vat'),('bills','Bills vat')],'Type VAT', states={'done':[('readonly',True)]}),

		'user_id': fields.many2one('res.users','Responsible',required=True, states={'done':[('readonly',True)]}),

		'account_sales': fields.float('Sales', store=True, compute='_compute_amount_transaction', states={'done':[('readonly',True)]}),
		'account_services': fields.float('Services', store=True, compute='_compute_amount_transaction', states={'done':[('readonly',True)]}),
		'account_exports': fields.float('Exports', states={'done':[('readonly',True)]}),
		'account_other': fields.float('Other', states={'done':[('readonly',True)]}),

		'base_reduced_rate': fields.float('Base reduced rate', store=True, compute='_compute_amount_base', states={'done':[('readonly',True)]}),
		'base_intermediate_rate': fields.float('Base intermediate rate', store=True, compute='_compute_amount_base', states={'done':[('readonly',True)]}),
		'base_normal_rate': fields.float('Base normal rate', store=True, compute='_compute_amount_base', states={'done':[('readonly',True)]}),
		'base_regularization_to_donate': fields.float('Base regularization to donate', states={'done':[('readonly',True)]}),

		'vat_due_reduced_rate': fields.float('Vat due reduced rate', states={'done':[('readonly',True)]}),
		'vat_due_intermediate_rate': fields.float('Vat due intermediate rate', states={'done':[('readonly',True)]}),
		'vat_due_normal_rate': fields.float('Vat due normal rate', states={'done':[('readonly',True)]}),
		'vat_due_regularization_to_donate': fields.float('Vat due regularization to donate', states={'done':[('readonly',True)]}),
		'total_vat_payable': fields.float('Total vat payable', store=True, compute='_compute_total_due', states={'done':[('readonly',True)]}),

		'vat_immobilization': fields.float('Vat immobilization', states={'done':[('readonly',True)]}),
		'vat_other_goods_services': fields.float('Vat other goods and services', states={'done':[('readonly',True)]}),
		'vat_regularization': fields.float('Regularization', states={'done':[('readonly',True)]}),
		'defferal_credit': fields.float('Defferal credit', states={'done':[('readonly',True)]}),
		'total_vat_deductible': fields.float('Total vat deductible', store=True, compute='_compute_total_deductible', states={'done':[('readonly',True)]}),

		'vat_credit': fields.float('Vat credit', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)]}),
		'reimbursement': fields.float('Reimbursement', states={'done':[('readonly',True)]}),
		'credit_to_be_transferred': fields.float('Credit to be transferred', store=True, compute='_compute_credit_to_reported', states={'done':[('readonly',True)]}),
		'net_vat_due': fields.float('Net vat due', store=True, compute='_compute_amount_vat',states={'done':[('readonly',True)]}),

		'excluding_vat_sales': fields.float('Excluding vat sales', states={'done':[('readonly',True)]}),
		'excluding_vat_services': fields.float('Excluding vat services', states={'done':[('readonly',True)]}),
		'tax_due_sales': fields.float('Tax due sales', store=True, compute='_compute_tax_due', states={'done':[('readonly',True)]}),
		'tax_due_services': fields.float('Tax due services', store=True, compute='_compute_tax_due', states={'done':[('readonly',True)]}),
		'total_tax_payable': fields.float('Total tax payable', store=True, compute='_compute_total_taxe_due', states={'done':[('readonly',True)]}),

		'difference_deductible_payable': fields.float('Difference', store=True, compute='_compute_total_difference', states={'done':[('readonly',True)]}),
		'deposit': fields.float('Deposit', states={'done':[('readonly',True)]}),
		'total_difference_deposit': fields.float('Total', store=True, compute='_compute_total_difference', states={'done':[('readonly',True)]}),
		'surplus': fields.float('Surplus', store=True, compute='_compute_total_difference', states={'done':[('readonly',True)]}),
		'difference_payable_deductible': fields.float('Difference', store=True, compute='_compute_total_difference', states={'done':[('readonly',True)]}),
		'obtained_reimbursement': fields.float('Reimbursement obtained', states={'done':[('readonly',True)]}),
		'total_difference_reimbursement': fields.float('Total', store=True, compute='_compute_total_difference', states={'done':[('readonly',True)]}),

		'net_to_pay': fields.float('Net to pay', store=True, compute='_compute_total_difference', states={'done':[('readonly',True)]}),

		'date': fields.date('Signature Date', required=True, states={'done':[('readonly',True)]}),
		'place': fields.char('Signature Place', required=True, states={'done':[('readonly',True)]}),
		'means_of_payment': fields.selection([('check','Check'),('cash','Cash'),('transfert','Transfert')], 'Means of payment', required=True, states={'done':[('readonly',True)]}),
		'fiscalyear': fields.many2one('account.fiscalyear', 'Fiscal year'),
		'period_from': fields.many2one('account.period', 'Start period'),
		'period_to': fields.many2one('account.period', 'End period'),
		'target_move': fields.selection([('posted', 'All Posted Entries'),('all', 'All Entries')], 'Target Moves'),

		'state': fields.selection([('draft','Draft'),('simulate','Simulate'),('done','Done')], 'Status', required=True, copy=False)
	}
	_defaults = {
		'date_declaration': lambda obj, cr, uid, context: time.strftime('%Y-%m-%d'),
		'date': lambda obj, cr, uid, context: time.strftime('%Y-%m-%d'),
		'place': 'Papeete',
		'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'l10n.pf.account.vat.declaration', context=context),
		'means_of_payment': 'check',
		'target_move': 'all',
		'fiscalyear': _get_fiscalyear,
		'state': 'draft'
	}

	## Cette méthode saisit les écritures comptables
	def enter_journal_items(self, cr, uid, ids, context=None):
		import pdb
		pdb.set_trace()
		ac_mv_line_obj = self.pool.get('account.move.line')
		company_obj = self.pool.get('res.company')
		for field in ['reduced_rate', 'intermediate_rate', 'normal_rate', 'regul_exigible', 'immo', 'goods_services', 'regul_deductible', 'report_credit', 'vat']:
			#Ecritures comptables pour le cas du regime simplifie annuel
			if (self.browse(cr, uid, ids, context=context).company_regime == 'annual'):
				if field == 'reduced_rate':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).reduced_rate_ids.id,
						'debit': self.browse(cr, uid, ids, context=context).vat_due_reduced_rate,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name) 
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'intermediate_rate':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).intermediate_rate_ids.id,
						'debit': self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'normal_rate':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).normal_rate_ids.id,
						'debit': self.browse(cr, uid, ids, context=context).vat_due_normal_rate,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'immo':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).immo_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_immobilization,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'goods_services':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).others_goods_services_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_other_goods_services,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'regul_deductible':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).others_goods_services_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_regularization,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'report_credit':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).credit_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).defferal_credit,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'vat':
					difference = self.browse(cr, uid, ids, context=context).total_vat_payable - self.browse(cr, uid, ids, context=context).total_vat_deductible
					# Cas du régime simplifie annuel
					if self.browse(cr, uid, ids, context=context).company_regime == 'annual':
						if difference > 0:
							vals = {
								#'state': 'valid',
								'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
								'account_id': company_obj.browse(cr, uid, uid, context=context).vat_ids.id,
								'credit': self.browse(cr, uid, ids, context=context).net_to_pay,
								'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
								'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
								'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
							}
							ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
						else:
							vals = {
								#'state': 'valid',
								'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
								'account_id': company_obj.browse(cr, uid, uid, context=context).vat_ids.id,
								'debit': self.browse(cr, uid, ids, context=context).surplus,
								'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
								'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
								'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
							}
							ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
			# Ecritures comptables pour le cas du regime reel sur les factures
			elif (self.browse(cr, uid, ids, context=context).company_regime == 'real') and (self.browse(cr, uid, ids, context=context).company_vat_type == 'bills'):
				if field == 'reduced_rate':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).reduced_rate_ids.id,
						'debit': self.browse(cr, uid, ids, context=context).vat_due_reduced_rate,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name) 
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'intermediate_rate':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).intermediate_rate_ids.id,
						'debit': self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'normal_rate':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).normal_rate_ids.id,
						'debit': self.browse(cr, uid, ids, context=context).vat_due_normal_rate,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'immo':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).immo_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_immobilization,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'goods_services':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).others_goods_services_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_other_goods_services,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'regul_deductible':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).others_goods_services_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_regularization,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'report_credit':
					vals = {
						#'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).credit_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).defferal_credit,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'vat':
					import pdb
					pdb.set_trace()
					difference = self.browse(cr, uid, ids, context=context).total_vat_payable - self.browse(cr, uid, ids, context=context).total_vat_deductible
					if difference > 0:
						vals = {
							#'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).vat_ids.id,
							'credit': self.browse(cr, uid, ids, context=context).net_vat_due,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
					else:
						vals = {
							#'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).vat_ids.id,
							'debit': self.browse(cr, uid, ids, context=context).vat_credit,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
			# Ecritures comptables pour le cas du regime reel sur les encaissements
			elif (self.browse(cr, uid, ids, context=context).company_regime == 'real') and (self.browse(cr, uid, ids, context=context).company_vat_type == 'cashing'):
				if field == 'intermediate_rate':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).intermediate_rate_ids.id,
						'debit': self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate + self.browse(cr, uid, ids, context=context).vat_due_regularization_to_donate,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'immo':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).immo_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_immobilization,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'goods_services':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).others_goods_services_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_other_goods_services,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'regul_deductible':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).others_goods_services_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_regularization,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'report_credit':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).credit_ids.id,
						'credit': self.browse(cr, uid, ids, context=context).defferal_credit,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
				elif field == 'vat':
					difference = self.browse(cr, uid, ids, context=context).total_vat_payable - self.browse(cr, uid, ids, context=context).total_vat_deductible
					if difference > 0:
						vals = {
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).vat_ids.id,
							'credit': self.browse(cr, uid, ids, context=context).net_vat_due,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)
					else:
						vals = {
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).vat_ids.id,
							'debit': self.browse(cr, uid, ids, context=context).net_vat_due,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': 'TVA ' + str(self.browse(cr, uid, ids, context=context).fiscalyear.name)
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=True)					
		return True
		
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
	
	def on_change_fiscalyear(self, cr, uid, ids, fiscalyear_id=False, context=None):
		res = {}
		if fiscalyear_id:
			start_period = end_period = False
			cr.execute('''
				SELECT * FROM (SELECT p.id
							   FROM account_period p
							   LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
							   WHERE f.id = %s
							   ORDER BY p.date_start ASC, p.special DESC
							   LIMIT 1) AS period_start
				UNION ALL
				SELECT * FROM (SELECT p.id
							   FROM account_period p
							   LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
							   WHERE f.id = %s
							   AND p.date_start < NOW()
							   ORDER BY p.date_stop DESC
							   LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
			periods =  [i[0] for i in cr.fetchall()]
			if periods:
				start_period = periods[0]
				if len(periods) > 1:
					end_period = periods[1]
			res['value'] = {'period_from': start_period, 'period_to': end_period}
		else:
			res['value'] = {'period_from': False, 'period_to': False}
		return res
