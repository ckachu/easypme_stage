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
	
	_inherit = 'account.chart'
	
	def action_fill_declaration(self, cr, uid, ids, context=None):
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
	
	
	# Cette fonction calcule le montant des bases hors TVA
	@api.one
	@api.depends('vat_due_reduced_rate','vat_due_intermediate_rate','vat_due_normal_rate','company_id','company_vat_type')
	def _compute_amount_base(self):
		if self.company_vat_type == 'cashing':
			self.base_reduced_rate = 0.0
			self.base_intermediate_rate = self.vat_due_intermediate_rate / (self.company_id.intermediate_rate / 100)
			self.base_normal_rate = 0.0
		else:
			self.base_reduced_rate = self.vat_due_reduced_rate / (self.company_id.reduced_rate / 100.0)
			self.base_intermediate_rate = self.vat_due_intermediate_rate / (self.company_id.intermediate_rate / 100)
			self.base_normal_rate = self.vat_due_normal_rate / (self.company_id.normal_rate / 100)	
				
	# Cette fonction calcule le total de la TVA exigible des régimes annuel simplifié et réel selon le type de TVA
	@api.one
	@api.depends('vat_due_reduced_rate','vat_due_intermediate_rate','vat_due_normal_rate','vat_due_regularization_to_donate','company_vat_type')
	def _compute_total_due(self):
		if self.company_vat_type == 'cashing':
			self.total_vat_payable = self.vat_due_intermediate_rate + self.vat_due_regularization_to_donate 
		else:
			self.total_vat_payable = self.vat_due_reduced_rate + self.vat_due_intermediate_rate + self.vat_due_normal_rate + self.vat_due_regularization_to_donate
	
	# Cette fonction calcule le total de la taxe due de l'acompte en régime simplifié
	@api.one
	@api.depends('tax_due_sales','tax_due_services')
	def _compute_total_taxe_due(self):
		self.total_tax_payable = self.tax_due_sales + self.tax_due_services
	
	# Cette fonction calcule le total de la TVA déductible selon le type de régime
	@api.one
	@api.depends('company_regime','vat_immobilization','vat_other_goods_services','vat_regularization','defferal_credit')
	def _compute_total_deductible(self):
		if self.company_regime == 'deposit':
			self.total_vat_deductible = self.vat_immobilization + self.defferal_credit
		else:
			self.total_vat_deductible = self.vat_immobilization + self.vat_other_goods_services + self.vat_regularization + self.defferal_credit
	
	# Cette fonction calcule le montant de la TVA ou du crédit de TVA selon les cas
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
	
	# Cette fonction calcule le montant du crédit à reporter
	@api.one
	@api.depends('vat_credit','reimbursement','surplus','company_regime')
	def _compute_credit_to_reported(self):
		if self.company_regime == 'annual':
			self.credit_to_be_transferred = self.surplus - self.reimbursement
		else:
			self.credit_to_be_transferred = self.vat_credit - self.reimbursement
	
	# Régime annuel simplifié
	@api.one
	@api.depends('total_vat_payable','total_vat_deductible','deposit','obtained_reimbursement')
	def _compute_total_difference(self):
		self.difference_deductible_payable = self.total_vat_payable - self.total_vat_deductible
		self.difference_payable_deductible = self.total_vat_deductible - self.total_vat_payable
		self.total_difference_deposit = self.difference_deductible_payable + self.deposit
		self.total_difference_reimbursement = self.difference_payable_deductible + self.reimbursement
	
	# Régime annuel simplifié
	@api.one
	@api.depends('total_difference_deposit','total_difference_reimbursement')
	def _compute_surplus_net(self):
		self.surplus = self.total_difference_deposit - self.total_difference_reimbursement
		self.net_to_pay = self.total_difference_reimbursement - self.total_difference_deposit
	
	_columns = {
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
		
		'base_reduced_rate': fields.float('Base reduced rate', store=True, compute='_compute_amount_base'),
		'base_intermediate_rate': fields.float('Base intermediate rate', store=True, compute='_compute_amount_base'),
		'base_normal_rate': fields.float('Base normal rate', store=True, compute='_compute_amount_base'),
		'base_regularization_to_donate': fields.float('Base regularization to donate'),
		
		'vat_due_reduced_rate': fields.float('Vat due reduced rate'),
		'vat_due_intermediate_rate': fields.float('Vat due intermediate rate'),
		'vat_due_normal_rate': fields.float('Vat due normal rate'),
		'vat_due_regularization_to_donate': fields.float('Vat due regularization to donate'),
		'total_vat_payable': fields.float('Total vat payable', store=True, compute='_compute_total_due'),
		
		'vat_immobilization': fields.float('Vat immobilization'),
		'vat_other_goods_services': fields.float('Vat other goods and services'),
		'vat_regularization': fields.float('Regularization'),
		'defferal_credit': fields.float('Defferal credit'),
		'total_vat_deductible': fields.float('Total vat deductible', store=True, compute='_compute_total_deductible'),
		
		'vat_credit': fields.float('Vat credit', store=True, compute='_compute_amount_vat'),
		'reimbursement': fields.float('Reimbursement'),
		'credit_to_be_transferred': fields.float('Credit to be transferred', store=True, compute='_compute_credit_to_reported'),
		'net_vat_due': fields.float('Net vat due'),
		
		'excluding_vat_sales': fields.float('Excluding vat sales'),
		'excluding_vat_services': fields.float('Excluding vat services'),
		'tax_due_sales': fields.float('Tax due sales'),
		'tax_due_services': fields.float('Tax due services'),
		'total_tax_payable': fields.float('Total tax payable', store=True, compute='_compute_total_taxe_due'),
		
		'difference_deductible_payable': fields.float('Difference', store=True, compute='_compute_total_difference'),
		'deposit': fields.float('Deposit'),
		'total_difference_deposit': fields.float('Total', store=True, compute='_compute_total_difference'),
		'surplus': fields.float('Surplus', store=True, compute='_compute_surplus_net'),
		'difference_payable_deductible': fields.float('Difference', store=True, compute='_compute_total_difference'),
		'obtained_reimbursement': fields.float('Reimbursement obtained'),
		'total_difference_reimbursement': fields.float('Total', store=True, compute='_compute_total_difference'),
		
		'net_to_pay': fields.float('Net to pay', store=True, compute='_compute_surplus_net'),
		
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
	
