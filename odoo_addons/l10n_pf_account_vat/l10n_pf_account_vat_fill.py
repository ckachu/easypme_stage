# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv

class l10n_pf_account_vat_fill(osv.osv_memory):
	_name = "l10n.pf.account.vat.fill"
	#_inherit = "account.account"
	
	def _get_account(self, cr, uid, context=None):
		user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', user.company_id.id)], limit=1)
		return accounts and accounts[0] or False
	
	_columns = {
		'chart_account_id': fields.many2one('account.account', 'Chart of Account'),
		'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal year'),
		'target_move': fields.selection([('posted', 'All Posted Entries'),('all','All Entries')], 'Target Moves'),
		'period_from': fields.many2one('account.period', 'Start Period'),
		'period_to': fields.many2one('account.period', 'End Period'),
		'regime_vat': fields.selection([('deposit','Deposit in simplified regime'),('annual','Annual in simplified regime'),('real','Real regime')], 'Regime Vat'),
		'type_vat': fields.selection([('cashing','Cashing vat'),('bills','Bills vat')],'Type vat'),
		'exports_ids': fields.many2many('account.account', string='Exports accounts'),
		'others_ids': fields.many2many('account.account', string='Others accounts'),
		'reduced_rate_ids': fields.many2many('account.account', string='Reduced rate accounts'),
		'intermediate_rate_ids': fields.many2many('account.account', string='Intermediate rate accounts'),
		'normal_rate_ids': fields.many2many('account.account', string='Normal rate accounts'),
		'immo_ids': fields.many2many('account.account', string='Immo accounts'),
		'others_goods_services_ids': fields.many2many('account.account', string='Others goods and services accounts'),
		'customers_ids': fields.many2many('account.account', string='Customers accounts'),
		'turnover_ids': fields.many2many('account.account', string='Turnover accounts'),
		'journal_ids': fields.many2many('account.journal', string='Journals'),
	}
	
	def _get_all_journal(self, cr, uid, context=None):
		return self.pool.get('account.journal').search(cr, uid, [])
	
	_defaults = {
		'journal_ids': _get_all_journal,
		'chart_account_id': _get_account,
	}
	
	def default_get(self, cr, uid, fields, context=None):
		if not context:
			context = {}
		declaration_obj = self.pool.get('l10n.pf.account.vat.declaration')
		res = super(l10n_pf_account_vat_fill, self).default_get(cr, uid, fields, context=context)
		declaration_id = context.get('active_id', False)
		declaration = declaration_obj.browse(cr, uid, declaration_id, context=context)
		if 'target_move' in fields:
			res.update({'target_move': declaration.target_move})
		if 'regime_vat' in fields:
			res.update({'regime_vat': declaration.company_regime})
		if 'type_vat' in fields:
			res.update({'type_vat': declaration.company_vat_type})
		if 'fiscalyear_id' in fields:
			res.update({'fiscalyear_id': declaration.fiscalyear.id})
		if 'period_from' in fields:
			res.update({'period_from': declaration.period_from.id})
		if 'period_to' in fields:
			res.update({'period_to': declaration.period_to.id})
		if 'exports_ids' in fields:
			res.update({'exports_ids': [(6, 0, [ei.id for ei in declaration.company_id.exports_ids])]})
		if 'others_ids' in fields:
			res.update({'others_ids': [(6, 0, [oi.id for oi in declaration.company_id.others_ids])]})
		if 'reduced_rate_ids' in fields:
			res.update({'reduced_rate_ids': [(6, 0, [ri.id for ri in declaration.company_id.reduced_rate_ids])]})
		if 'intermediate_rate_ids' in fields:
			res.update({'intermediate_rate_ids': [(6, 0, [ri.id for ri in declaration.company_id.intermediate_rate_ids])]})
		if 'normal_rate_ids' in fields:
			res.update({'normal_rate_ids': [(6, 0, [ni.id for ni in declaration.company_id.normal_rate_ids])]})
		if 'immo_ids' in fields:
			res.update({'immo_ids': [(6, 0, [ii.id for ii in declaration.company_id.immo_ids])]})
		if 'others_goods_services_ids' in fields:
			res.update({'others_goods_services_ids': [(6, 0, [gs.id for gs in declaration.company_id.others_goods_services_ids])]})
		if 'customers_ids' in fields:
			res.update({'customers_ids': [(6, 0, [ci.id for ci in declaration.company_id.customers_ids])]})
		if 'turnover_ids' in fields:
			res.update({'turnover_ids': [(6, 0, [ti.id for ti in declaration.company_id.turnover_ids])]})
		return res

	def fill_declaration(self, cr, uid, ids, context=None):
		import pdb
		pdb.set_trace()
		if context is None:
			context = {}
		ac_obj = self.pool.get('l10n.pf.account.vat.declaration')
		declaration_id = context.get('active_id', False)
		declaration = ac_obj.browse(cr, uid, declaration_id, context=context)
		for field in ['exports_ids', 'others_ids', 'reduced_rate_ids', 'intermediate_rate_ids', 'normal_rate_ids', 'immo_ids', 'others_goods_services_ids', 'sales_ids', 'services_ids', 'credit_ids', 'deposit']:
			res = 0.0
			if declaration.company_regime == 'deposit':
				if field == 'sales_ids':
					for i in declaration.company_id.sales_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'excluding_vat_sales': res})
					else:
						declaration.update({'excluding_vat_sales': -res})
				elif field == 'services_ids':
					for i in declaration.company_id.services_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'excluding_vat_services': res})
					else:
						declaration.update({'excluding_vat_services': -res})
				elif field == 'immo_ids':
					for i in declaration.company_id.immo_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'vat_immobilization': res})
					else:
						declaration.update({'vat_immobilization': -res})
				elif field == 'credit_ids':
					pdb.set_trace()
					search_ids = self.pool.get("l10n.pf.account.vat.declaration").search(cr, uid, [('company_regime','=','deposit'),('state','=','done')])
					for obj in ac_obj.browse(cr, uid, search_ids, context=context):
						d1 = datetime.strptime(declaration.date_declaration, '%Y-%m-%d')
						d2 = datetime.strptime(obj.date_declaration, '%Y-%m-%d')
						if (str(d1.year) == str(d2.year + 1)):
							declaration.update({'defferal_credit': obj.vat_credit})
							print obj.vat_credit
			elif (declaration.company_regime == 'annual' or (declaration.company_regime == 'real' and declaration.company_vat_type == 'bills')):
				if field == 'exports_ids':
					for i in  declaration.company_id.exports_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'account_exports': res})
					else:
						declaration.update({'account_exports': -res})
				elif field == 'others_ids':
					for i in declaration.company_id.others_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'account_other': res})
					else:
						declaration.update({'account_other': -res})
				elif field == 'reduced_rate_ids':
					for i in declaration.company_id.reduced_rate_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'vat_due_reduced_rate': res})
					else:
						declaration.update({'vat_due_reduced_rate': -res})
				elif field == 'intermediate_rate_ids':
					for i in declaration.company_id.intermediate_rate_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'vat_due_intermediate_rate': res})
					else:
						declaration.update({'vat_due_intermediate_rate': -res})
				elif field == 'normal_rate_ids':
					for i in declaration.company_id.normal_rate_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'vat_due_normal_rate': res})
					else:
						declaration.update({'vat_due_normal_rate': -res})
				elif field == 'immo_ids':
					for i in declaration.company_id.immo_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'vat_immobilization': res})
					else:
						declaration.update({'vat_immobilization': -res})
				elif field == 'others_goods_services_ids':
					for i in declaration.company_id.others_goods_services_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'vat_other_goods_services': res})
					else:
						declaration.update({'vat_other_goods_services': -res})
				elif field == 'deposit':
					pdb.set_trace()
					search_ids = self.pool.get("l10n.pf.account.vat.declaration").search(cr, uid, [('company_regime','=','deposit')])
					print search_ids
				elif field == 'credit_ids':
					pdb.set_trace()
					search_ids = self.pool.get("l10n.pf.account.vat.declaration").search(cr, uid, [('company_regime', 'in', ('annual','real'))])
					print search_ids
					for obj in ac_obj.browse(cr, uid, search_ids, context=context):
						if declaration.company_regime == 'annual':
							d1 = datetime.strptime(declaration.period_to.date_start, '%Y-%m-%d')
							d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
							if (str(d1.year) == str(d2.year + 1)) and (obj.state == 'done') and (declaration.company_regime == obj.company_regime):
								declaration.update({'defferal_credit': obj.credit_to_be_transferred})
								print obj.credit_to_be_transferred
						elif (declaration.company_regime == 'real') and (declaration.company_vat_type == 'bills'):
							d1 = datetime.strptime(declaration.period_to.date_start, '%Y-%m-%d')
							d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
							if str(d1.year) == str(d2.year + 1):
								if ((str(d1.month) == str(d2.month - 11)) or (str(d1.month) == str(d2.month - 9))) and (obj.state == 'done') and (declaration.company_regime == obj.company_regime) and (declaration.company_vat_type == obj.company_vat_type):
									declaration.update({'defferal_credit': obj.credit_to_be_transferred})
									print obj.credit_to_be_transferred
							else:
								if ((str(d1.month - 1) == str(d2.month)) or (str(d1.month) == str(d2.month + 3))) and (obj.state == 'done') and (declaration.company_regime == obj.company_regime) and (declaration.company_vat_type == obj.company_vat_type):
									declaration.update({'defferal_credit': obj.credit_to_be_transferred})
									print obj.credit_to_be_transferred
			elif (declaration.company_regime == 'real' and declaration.company_vat_type == 'cashing'):
				compte_client_n = 0.0
				chiffre_n = 0.0
				taux_inter_n = 0.0
				compte_client_n_1 = 0.0
				deb = 0.0
				cre = 0.0
				
				# on recupere le montant du 411 pour l'annee N
				for i in declaration.company_id.customers_ids:
					compte_client_n = compte_client_n + i.balance
				# on recupere le montant du 706 pour l'annee N
				for i in declaration.company_id.turnover_ids:
					chiffre_n = chiffre_n + i.balance
				# on  recupere le montant du taux intermédiaire pour l'annee N
				for i in declaration.company_id.intermediate_rate_ids:
					taux_inter_n = taux_inter_n + i.balance
				# on recupere le credit et le debit du 411 dans la periode d'ouverture de l'annee N
					
				
				if field == 'exports_ids':
					for i in  declaration.company_id.exports_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'account_exports': res})
					else:
						declaration.update({'account_exports': -res})
				elif field == 'others_ids':
					for i in declaration.company_id.others_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'account_other': res})
					else:
						declaration.update({'account_other': -res})	
				elif field == 'intermediate_rate_ids':
					for i in declaration.company_id.intermediate_rate_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'vat_due_intermediate_rate': res})
					else:
						declaration.update({'vat_due_intermediate_rate': -res})
				elif field == 'immo_ids':
					for i in declaration.company_id.immo_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'vat_immobilization': res})
					else:
						declaration.update({'vat_immobilization': -res})
				elif field == 'others_goods_services_ids':
					for i in declaration.company_id.others_goods_services_ids:
						res = res + i.balance
						print res
					if res >= 0:
						declaration.update({'vat_other_goods_services': res})
					else:
						declaration.update({'vat_other_goods_services': -res})
				elif field == 'credit_ids':
					pdb.set_trace()
					search_ids = self.pool.get("l10n.pf.account.vat.declaration").search(cr, uid, [('company_regime','=','real'),('company_vat_type','=','cashing')])
					print search_ids
					for obj in ac_obj.browse(cr, uid, search_ids, context=context):
						d1 = datetime.strptime(declaration.period_to.date_start, '%Y-%m-%d')
						d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
						if ((str(d1.month) == str(d2.month + 1)) or (str(d1.month) == str(d2.month + 3))) and (obj.state == 'done') and (declaration.company_regime == obj.company_regime) and (declaration.company_vat_type == obj.company_vat_type):
							declaration.update({'defferal_credit': obj.credit_to_be_transferred})
							print obj.credit_to_be_transferred
							
		return declaration
