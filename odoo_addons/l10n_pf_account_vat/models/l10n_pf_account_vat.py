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

	#_inherit = 'account.chart'

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

	def __compute(self, cr, uid, ids, field_names, arg=None, context=None, query='', query_params=()):
		import pdb
		pdb.set_trace()
		#children_and_consolidated = self._get_exports_ids(cr, uid, ids, context=context)
		#return super(account_account, self).__compute(cr, uid, ids, field_names, arg, context, query, query_params)
		

	def action_fill_declaration(self, cr, uid, ids, context=None):
		import pdb
		pdb.set_trace()
		company = self.pool.get('res.company')
		ids1 = []
		for ei in company.browse(cr, uid, uid, context=context).intermediate_rate_ids:
			ids1 = ids1 + list(ei)
		print ids1
		
            
	### Cette méthode récupère les comptes des exportations
	#def _get_exports_ids(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#company = self.pool.get('res.company')
		#ids1 = []
		#for ei in company.browse(cr, uid, uid, context=context).exports_ids:
			#ids1 = ids1 + list(ei)
		#print ids1
		#return ids1

	### Cette méthode récupère les comptes des autres opérations non taxables
	#def _get_others_ids(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#company = self.pool.get('res.company')
		#ids1 = []
		#for oi in company.browse(cr, uid, uid, context=context).others_ids:
			#ids1 = ids1 + list(oi)
		#return ids1

	### Cette méthode récupère les comptes du taux réduit
	#def _get_reduced_rate_ids(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#company = self.pool.get('res.company')
		#ids1 = []
		#for ri in company.browse(cr, uid, uid, context=context).reduced_rate_ids:
			#ids1 = ids1 + list(ri)
		#return ids1

	### Cette méthode récupère les comptes du taux intermédiaire
	#def _get_intermediate_rate_ids(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#company = self.pool.get('res.company')
		#ids1 = []
		#for ii in company.browse(cr, uid, uid, context=context).intermediate_rate_ids:
			#ids1 = ids1 + list(ii)
		#return ids1

	### Cette méthode récupère les comptes du taux normal
	#def _get_normal_rate_ids(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#company = self.pool.get('res.company')
		#ids1 = []
		#for ni in company.browse(cr, uid, uid, context=context).normal_rate_ids:
			#ids1 = ids1 + list(ni)
		#return ids1

	### Cette méthode récupère les comptes des immobilisations
	#def _get_immo_ids(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#company = self.pool.get('res.company')
		#ids1 = []
		#for im in company.browse(cr, uid, uid, context=context).immo_ids:
			#ids1 = ids1 + list(im)
		#return ids1

	### Cette méthode récupère les comptes des autres biens et services
	#def _get_others_goods_services_ids(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#company = self.pool.get('res.company')
		#ids1 = []
		#for gs in company.browse(cr, uid, uid, context=context).others_goods_services_ids:
			#ids1 = ids1 + list(gs)
		#return ids1

	### Cette méthode récupère les comptes clients
	#def _get_customers_ids(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#company = self.pool.get('res.company')
		#ids1 = []
		#for ci in company.browse(cr, uid, uid, context=context).customers_ids:
			#ids1 = ids1 + list(ci)
		#return ids1

	### Cette méthode récupère les comptes du chiffre d'affaires
	#def _get_turnover_ids(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#company = self.pool.get('res.company')
		#ids1 = []
		#for ti in company.browse(cr, uid, uid, context=context).turnover_ids:
			#ids1 = ids1 + list(ti)
		#return ids1

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
		self.difference_deductible_payable = self.total_vat_payable - self.total_vat_deductible
		self.difference_payable_deductible = self.total_vat_deductible - self.total_vat_payable
		self.total_difference_deposit = self.difference_deductible_payable + self.deposit
		self.total_difference_reimbursement = self.difference_payable_deductible + self.reimbursement

	## Régime annuel simplifié
	@api.one
	@api.depends('total_difference_deposit','total_difference_reimbursement')
	def _compute_surplus_net(self):
		self.surplus = self.total_difference_deposit - self.total_difference_reimbursement
		self.net_to_pay = self.total_difference_reimbursement - self.total_difference_deposit

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

		'account_sales': fields.float('Sales', states={'done':[('readonly',True)]}),
		'account_services': fields.float('Services', states={'done':[('readonly',True)]}),
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
		'net_vat_due': fields.float('Net vat due', states={'done':[('readonly',True)]}),

		'excluding_vat_sales': fields.float('Excluding vat sales', states={'done':[('readonly',True)]}),
		'excluding_vat_services': fields.float('Excluding vat services', states={'done':[('readonly',True)]}),
		'tax_due_sales': fields.float('Tax due sales', states={'done':[('readonly',True)]}),
		'tax_due_services': fields.float('Tax due services', states={'done':[('readonly',True)]}),
		'total_tax_payable': fields.float('Total tax payable', store=True, compute='_compute_total_taxe_due', states={'done':[('readonly',True)]}),

		'difference_deductible_payable': fields.float('Difference', store=True, compute='_compute_total_difference', states={'done':[('readonly',True)]}),
		'deposit': fields.float('Deposit', states={'done':[('readonly',True)]}),
		'total_difference_deposit': fields.float('Total', store=True, compute='_compute_total_difference', states={'done':[('readonly',True)]}),
		'surplus': fields.float('Surplus', store=True, compute='_compute_surplus_net', states={'done':[('readonly',True)]}),
		'difference_payable_deductible': fields.float('Difference', store=True, compute='_compute_total_difference', states={'done':[('readonly',True)]}),
		'obtained_reimbursement': fields.float('Reimbursement obtained', states={'done':[('readonly',True)]}),
		'total_difference_reimbursement': fields.float('Total', store=True, compute='_compute_total_difference', states={'done':[('readonly',True)]}),

		'net_to_pay': fields.float('Net to pay', store=True, compute='_compute_surplus_net', states={'done':[('readonly',True)]}),

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
		'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'l10n.pf.account.vat.declaration', context=context),
		'means_of_payment': 'check',
		'target_move': 'all',
		'fiscalyear': _get_fiscalyear,
		'state': 'draft'
	}

	## Cette méthode saisit les écritures comptables
	#def enter_journal_items(self, cr, uid, ids, context=None):


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
