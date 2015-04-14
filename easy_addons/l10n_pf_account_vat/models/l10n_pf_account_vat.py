# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta
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
		if context is None:
			context = {}
		for decl in self.browse(cr, uid, ids, context=context):
			for field in ['exports_ids', 'others_ids', 'reduced_rate_ids', 'intermediate_rate_ids', 'normal_rate_ids', \
			'immo_ids', 'others_goods_services_ids', 'sales_ids', 'services_ids', 'credit_ids', 'deposit']:
				res = 0.0
				if decl.company_regime == 'deposit':
					if field == 'sales_ids':
						for i in decl.company_id.sales_ids:
							res = res + i.balance
							print res
						if res >= 0:
							decl.update({'excluding_vat_sales': res})
						else:
							decl.update({'excluding_vat_sales': -res})
					elif field == 'services_ids':
						for i in decl.company_id.services_ids:
							res = res + i.balance
							print res
						if res >= 0:
							decl.update({'excluding_vat_services': res})
						else:
							decl.update({'excluding_vat_services': -res})
					elif field == 'immo_ids':
						for i in decl.company_id.immo_ids:
							res = res + i.balance
							print res
						if res >= 0:
							decl.update({'vat_immobilization': res})
						else:
							decl.update({'vat_immobilization': -res})
					elif field == 'credit_ids':
						#pdb.set_trace()
						search_ids = self.search(cr, uid, [('company_regime','=','deposit'),('state','=','done')])
						for obj in self.browse(cr, uid, search_ids, context=context):
							d1 = datetime.strptime(decl.date_declaration, '%Y-%m-%d')
							d2 = datetime.strptime(obj.date_declaration, '%Y-%m-%d')
							if (str(d1.year) == str(d2.year + 1)):
								decl.update({'defferal_credit': obj.vat_credit})
								print obj.vat_credit
				elif decl.company_regime == 'annual':
					#TODO: Modifier pour correspondre à ce cas
					if field == 'exports_ids':
						for i in  decl.company_id.exports_ids:
							res = res + i.balance
							print res
						if res >= 0:
							decl.update({'account_exports': res})
						else:
							decl.update({'account_exports': -res})
					elif field == 'others_ids':
						for i in decl.company_id.others_ids:
							res = res + i.balance
							print res
						if res >= 0:
							decl.update({'account_other': res})
						else:
							decl.update({'account_other': -res})
					elif field == 'reduced_rate_ids':
						#for i in decl.company_id.reduced_rate_ids:
							#res = res + i.balance
							#print res
						
						my_list = []
						# On définit un nouveau context avec FROM: Période d'ouverture et TO: Période de fin de la période actuelle
						ctx = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.period_to.id,
							'target_move': decl.target_move
						}
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in self.browse(cr, uid, ids, context=ctx).company_id.tax_reduced_rate_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						
						if res >= 0:
							decl.update({'vat_due_reduced_rate': res})
						else:
							decl.update({'vat_due_reduced_rate': -res})
					elif field == 'intermediate_rate_ids':
						#for i in decl.company_id.intermediate_rate_ids:
							#res = res + i.balance
							#print res
						
						my_list = []
						# On définit un nouveau context avec FROM: Période d'ouverture et TO: Période de fin de la période actuelle
						ctx = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.period_to.id,
							'target_move': decl.target_move
						}
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in self.browse(cr, uid, ids, context=ctx).company_id.tax_intermediate_rate_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						
						if res >= 0:
							decl.update({'vat_due_intermediate_rate': res})
						else:
							decl.update({'vat_due_intermediate_rate': -res})
					elif field == 'normal_rate_ids':
						#for i in decl.company_id.normal_rate_ids:
							#res = res + i.balance
							#print res
						
						my_list = []
						# On définit un nouveau context avec FROM: Période d'ouverture et TO: Période de fin de la période actuelle
						ctx = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.period_to.id,
							'target_move': decl.target_move
						}
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in self.browse(cr, uid, ids, context=ctx).company_id.tax_normal_rate_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						
						if res >= 0:
							decl.update({'vat_due_normal_rate': res})
						else:
							decl.update({'vat_due_normal_rate': -res})
					elif field == 'immo_ids':
						#for i in decl.company_id.immo_ids:
							#res = res + i.balance
							#print res
						
						my_list = []
						# On définit un nouveau context avec FROM: Période d'ouverture et TO: Période de fin de la période actuelle
						ctx = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.period_to.id,
							'target_move': decl.target_move
						}
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in self.browse(cr, uid, ids, context=ctx).company_id.tax_immo_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						
						if res >= 0:
							decl.update({'vat_immobilization': res})
						else:
							decl.update({'vat_immobilization': -res})
					elif field == 'others_goods_services_ids':
						#for i in decl.company_id.others_goods_services_ids:
							#res = res + i.balance
							#print res
						
						my_list = []
						# On définit un nouveau context avec FROM: Période d'ouverture et TO: Période de fin de la période actuelle
						ctx = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.period_to.id,
							'target_move': decl.target_move
						}
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in self.browse(cr, uid, ids, context=ctx).company_id.tax_others_goods_services_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						
						if res >= 0:
							decl.update({'vat_other_goods_services': res})
						else:
							decl.update({'vat_other_goods_services': -res})
					elif field == 'deposit':
						#pdb.set_trace()
						search_ids = self.search(cr, uid, [('company_regime','=','deposit')])
						print search_ids
						for obj in self.browse(cr, uid, search_ids, context=context):
							if (decl.company_regime == 'annual') and (decl.fiscalyear.id == obj.fiscalyear.id) and (obj.state == 'done'):
								decl.update({'deposit': obj.net_vat_due})
					elif field == 'credit_ids':
						#pdb.set_trace()
						search_ids = self.search(cr, uid, [('company_regime', 'in', ('annual','real'))])
						print search_ids
						for obj in self.browse(cr, uid, search_ids, context=context):
							if decl.company_regime == 'annual':
								d1 = datetime.strptime(decl.period_to.date_start, '%Y-%m-%d')
								d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
								if (str(d1.year) == str(d2.year + 1)) and (obj.state == 'done') and (decl.company_regime == obj.company_regime):
									decl.update({'defferal_credit': obj.credit_to_be_transferred})
									print obj.credit_to_be_transferred
							elif (decl.company_regime == 'real') and (decl.company_vat_type == 'bills'):
								d1 = datetime.strptime(decl.period_to.date_start, '%Y-%m-%d')
								d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
								if str(d1.year) == str(d2.year + 1):
									if ((str(d1.month) == str(d2.month - 11)) or (str(d1.month) == str(d2.month - 9))) and \
										(obj.state == 'done') and (decl.company_regime == obj.company_regime) and \
										(decl.company_vat_type == obj.company_vat_type):
										decl.update({'defferal_credit': obj.credit_to_be_transferred})
										print obj.credit_to_be_transferred
								else:
									if ((str(d1.month - 1) == str(d2.month)) or (str(d1.month) == str(d2.month + 3))) and \
										(obj.state == 'done') and (decl.company_regime == obj.company_regime) and \
										(decl.company_vat_type == obj.company_vat_type):
										decl.update({'defferal_credit': obj.credit_to_be_transferred})
										print obj.credit_to_be_transferred
				elif (decl.company_regime == 'real') and (decl.company_vat_type == 'bills'):
					if field == 'exports_ids':
						for i in  decl.company_id.exports_ids:
							res = res + i.balance
							print res
						decl.update({'account_exports': res})
					elif field == 'others_ids':
						for i in decl.company_id.others_ids:
							res = res + i.balance
							print res
						decl.update({'account_other': res})
					elif field == 'reduced_rate_ids':						
						my_list = []
						# On définit un nouveau context avec FROM: Période d'ouverture et TO: Période de fin de la période actuelle
						ctx = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.period_to.id,
							'target_move': decl.target_move
						}
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in self.browse(cr, uid, ids, context=ctx).company_id.tax_reduced_rate_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						
						decl.update({'vat_due_reduced_rate': -res})
					elif field == 'intermediate_rate_ids':
						my_list = []
						# On définit un nouveau context avec FROM: Période d'ouverture et TO: Période de fin de la période actuelle
						ctx = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.period_to.id,
							'target_move': decl.target_move
						}
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in self.browse(cr, uid, ids, context=ctx).company_id.tax_intermediate_rate_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						
						decl.update({'vat_due_intermediate_rate': -res})
					elif field == 'normal_rate_ids':
						my_list = []
						# On définit un nouveau context avec FROM: Période d'ouverture et TO: Période de fin de la période actuelle
						ctx = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.period_to.id,
							'target_move': decl.target_move
						}
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in self.browse(cr, uid, ids, context=ctx).company_id.tax_normal_rate_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						
						decl.update({'vat_due_normal_rate': -res})
					elif field == 'immo_ids':
						my_list = []
						# On définit un nouveau context avec FROM: Période d'ouverture et TO: Période de fin de la période actuelle
						ctx = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.period_to.id,
							'target_move': decl.target_move
						}
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in self.browse(cr, uid, ids, context=ctx).company_id.tax_immo_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						
						decl.update({'vat_immobilization': res})
					elif field == 'others_goods_services_ids':
						my_list = []
						# On définit un nouveau context avec FROM: Période d'ouverture et TO: Période de fin de la période actuelle
						ctx = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.period_to.id,
							'target_move': decl.target_move
						}
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in self.browse(cr, uid, ids, context=ctx).company_id.tax_others_goods_services_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						
						decl.update({'vat_other_goods_services': res})
					elif field == 'credit_ids':
						#pdb.set_trace()
						search_ids = self.search(cr, uid, [('company_regime', 'in', ('annual','real'))])
						print search_ids
						for obj in self.browse(cr, uid, search_ids, context=context):
							if decl.company_regime == 'annual':
								d1 = datetime.strptime(decl.period_to.date_start, '%Y-%m-%d')
								d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
								if (str(d1.year) == str(d2.year + 1)) and (obj.state == 'done') and (decl.company_regime == obj.company_regime):
									decl.update({'defferal_credit': obj.credit_to_be_transferred})
									print obj.credit_to_be_transferred
							elif (decl.company_regime == 'real') and (decl.company_vat_type == 'bills'):
								d1 = datetime.strptime(decl.period_to.date_start, '%Y-%m-%d')
								d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
								if str(d1.year) == str(d2.year + 1):
									if ((str(d1.month) == str(d2.month - 11)) or (str(d1.month) == str(d2.month - 9))) and \
										(obj.state == 'done') and (decl.company_regime == obj.company_regime) and \
										(decl.company_vat_type == obj.company_vat_type):
										decl.update({'defferal_credit': obj.credit_to_be_transferred})
										print obj.credit_to_be_transferred
								else:
									if ((str(d1.month - 1) == str(d2.month)) or (str(d1.month) == str(d2.month + 3))) and \
										(obj.state == 'done') and (decl.company_regime == obj.company_regime) and \
										(decl.company_vat_type == obj.company_vat_type):
										decl.update({'defferal_credit': obj.credit_to_be_transferred})
										print obj.credit_to_be_transferred
				elif (decl.company_regime == 'real' and decl.company_vat_type == 'cashing'):
					if field == 'exports_ids':
						for i in  decl.company_id.exports_ids:
							res = res + i.balance
							print res
						decl.update({'account_exports': res})
					elif field == 'others_ids':
						for i in decl.company_id.others_ids:
							res = res + i.balance
							print res
						decl.update({'account_other': res})	
					elif field == 'intermediate_rate_ids':
						compte_client_n = 0.0
						chiffre_n = 0.0
						taux_inter_n = 0.0
						compte_client_n_1 = 0.0
						somme = 0.0				
						# on recupere le montant du 411 pour l'annee N
						for i in decl.company_id.customers_ids:
							compte_client_n = compte_client_n + i.balance
						# on recupere le montant du 706 pour l'annee N
						for i in decl.company_id.turnover_ids:
							chiffre_n = chiffre_n + i.balance
						# on  recupere le montant du taux intermédiaire pour l'annee N
						#for i in decl.company_id.intermediate_rate_ids:
						#	taux_inter_n = taux_inter_n + i.balance
						my_list = []
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in decl.company_id.tax_intermediate_rate_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)	
						print my_list
						# On supprime les doublons
						my_list = list(set(my_list))
						print my_list
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index,obj in enumerate(my_list):
							taux_inter_n = taux_inter_n + my_list[index].balance						
						# on recupere la balance 411 dans la periode d'ouverture de l'annee N 
						#pdb.set_trace()
						context_prev = {
							'fiscalyear': decl.fiscalyear.id,
							'period_from': decl.fiscalyear.period_ids[0].id,
							'period_to': decl.fiscalyear.period_ids[0].id,
							'target_move': decl.target_move
						}
						#import pdb
						#pdb.set_trace()
						for i in self.browse(cr, uid, ids, context=context_prev).company_id.customers_ids:
							compte_client_n_1 = compte_client_n_1 + i.balance
						# Montant déjà déclaré
						decl_ids = self.search(cr, uid, [])
						print decl_ids
						for j in self.browse(cr, uid, decl_ids, context=context):
							if (j.fiscalyear == decl.fiscalyear) and (j.state == 'done') and (j.company_regime == 'real') and (j.company_vat_type == 'cashing'):
								somme = somme + j.vat_due_intermediate_rate
						# Calcul du montant TTC
						ttc = compte_client_n_1 + chiffre_n + taux_inter_n - compte_client_n
						# Calcul du montant HT
						ht = decl.company_id.currency_id.round(ttc / (1 + decl.company_id.tax_intermediate_rate_ids[0].amount))
						# Calcul du montant de la prestation à déclarer
						prestation = ht - somme
						# Calcul du montant de la TVA due de la prestation
						res = decl.company_id.currency_id.round(prestation * decl.company_id.tax_intermediate_rate_ids[0].amount)
						decl.update({'vat_due_intermediate_rate': -res})
					elif field == 'immo_ids':
						my_list = []
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in decl.company_id.tax_immo_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)	
						print my_list
						# On supprime les doublons
						my_list = list(set(my_list))
						print my_list
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index,obj in enumerate(my_list):
							res = res + my_list[index].balance
						decl.update({'vat_immobilization': res})
					elif field == 'others_goods_services_ids':
						my_list = []
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in decl.company_id.tax_others_goods_services_ids:
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)	
						print my_list
						# On supprime les doublons
						my_list = list(set(my_list))
						print my_list
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index,obj in enumerate(my_list):
							res = res + my_list[index].balance
						decl.update({'vat_other_goods_services': res})
					elif field == 'credit_ids':
						#import pdb
						#pdb.set_trace()
						search_ids = self.search(cr, uid, [('company_regime','=','real'),('company_vat_type','=','cashing')])
						print search_ids
						for obj in self.browse(cr, uid, search_ids, context=context):
							d1 = datetime.strptime(decl.period_to.date_start, '%Y-%m-%d')
							d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
							if ((str(d1.month) == str(d2.month + 1)) or (str(d1.month) == str(d2.month + 3))) and \
								(obj.state == 'done') and (decl.company_regime == obj.company_regime) and \
								(decl.company_vat_type == obj.company_vat_type):
								decl.update({'defferal_credit': obj.credit_to_be_transferred})
								print obj.credit_to_be_transferred

						
		return decl

	## Cette fonction calcule le montant des bases hors TVA
	@api.one
	@api.depends('vat_due_reduced_rate','vat_due_intermediate_rate','vat_due_normal_rate','company_id','company_vat_type')
	def _compute_amount_base(self):
		self.base_reduced_rate = self.company_id.currency_id.round(self.vat_due_reduced_rate / self.company_id.tax_reduced_rate_ids[0].amount)
		self.base_intermediate_rate = self.company_id.currency_id.round(self.vat_due_intermediate_rate / self.company_id.tax_intermediate_rate_ids[0].amount)
		self.base_normal_rate = self.company_id.currency_id.round(self.vat_due_normal_rate / self.company_id.tax_normal_rate_ids[0].amount)

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
	@api.depends('total_vat_payable','total_vat_deductible','total_tax_payable','company_regime','deposit','obtained_reimbursement')
	def _compute_amount_vat(self):
		diff1 = abs(self.total_tax_payable) - abs(self.total_vat_deductible)
		diff2 = abs(self.total_vat_payable) - abs(self.total_vat_deductible)

		if self.company_regime == 'deposit':
			if diff1 > 0:
				self.net_vat_due = abs(self.total_tax_payable) - abs(self.total_vat_deductible)
				self.vat_credit = 0.0
			else:
				self.vat_credit = abs(self.total_vat_deductible) - abs(self.total_tax_payable)
				self.net_vat_due = 0.0
		elif self.company_regime == 'real':
			if diff2 > 0:
				self.net_vat_due = abs(self.total_vat_payable) - abs(self.total_vat_deductible)
				self.vat_credit = 0.0
			else:
				self.vat_credit = abs(self.total_vat_deductible) - abs(self.total_vat_payable)
				self.net_vat_due = 0.0
		elif self.company_regime == 'annual':
			# TVA A PAYER
			if diff2 > 0:
				self.difference_payable_deductible = diff2
				self.difference_deductible_payable = 0.0
				self.total_difference_deposit = self.difference_deductible_payable + self.deposit
				self.total_difference_reimbursement = self.difference_payable_deductible + self.obtained_reimbursement
				self.net_vat_due = self.total_difference_reimbursement - self.total_difference_deposit
				self.surplus = 0.0
			# CREDIT
			else:
				self.difference_deductible_payable = diff2
				self.difference_payable_deductible = 0.0
				self.total_difference_deposit = self.difference_deductible_payable + self.deposit
				self.total_difference_reimbursement = self.difference_payable_deductible + self.obtained_reimbursement
				self.surplus = self.total_difference_deposit - self.total_difference_reimbursement
				self.net_vat_due = 0.0

	## Cette fonction calcule le montant du crédit à reporter
	@api.one
	@api.depends('vat_credit','reimbursement','surplus','company_regime')
	def _compute_credit_to_reported(self):
		if self.company_regime == 'annual':
			self.credit_to_be_transferred = self.surplus - self.reimbursement
		else:
			self.credit_to_be_transferred = self.vat_credit - self.reimbursement

	@api.one
	@api.depends('excluding_vat_sales','excluding_vat_services','company_id')
	def _compute_tax_due(self):
		self.tax_due_sales = self.excluding_vat_sales * self.company_id.tax_reduced_rate_ids[0].amount
		self.tax_due_services = self.excluding_vat_services * self.company_id.tax_reduced_rate_ids[0].amount

	@api.one
	@api.depends('base_reduced_rate', 'base_intermediate_rate', 'base_normal_rate', 'base_regularization_to_donate', 'company_vat_type', 'company_regime')
	def _compute_amount_transaction(self):
		if self.company_vat_type == 'cashing' and self.company_regime == 'real':
			self.account_services = self.base_intermediate_rate + self.base_regularization_to_donate
		elif self.company_regime == 'annual' or (self.company_regime == 'real' and self.company_vat_type == 'bills'):
			self.account_sales = self.base_reduced_rate + self.base_normal_rate
			self.account_services = self.base_intermediate_rate
		
	_columns = {
		'name': fields.char('Declaration name', required=True, states={'done':[('readonly',True)]}),
		'date_declaration': fields.date('Declaration date', states={'done':[('readonly',True)]}),
		'account_id': fields.many2one('account.account', 'Account'),

		'ntahiti': fields.char('No Tahiti', states={'done':[('readonly',True)]}),
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
		'company_regime': fields.selection([('deposit','Deposit in simplified regime'),('annual','Annual in simplified regime'),('real','Real regime')], 'Regime'),
		'company_vat_type': fields.selection([('cashing','Cashing vat'),('bills','Bills vat')],'Type VAT'),

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

		'difference_deductible_payable': fields.float('Difference', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)]}),
		'deposit': fields.float('Deposit', states={'done':[('readonly',True)]}),
		'total_difference_deposit': fields.float('Total', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)]}),
		'surplus': fields.float('Surplus', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)]}),
		'difference_payable_deductible': fields.float('Difference', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)]}),
		'obtained_reimbursement': fields.float('Reimbursement obtained', states={'done':[('readonly',True)]}),
		'total_difference_reimbursement': fields.float('Total', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)]}),

		'date': fields.date('Signature Date', required=True, states={'done':[('readonly',True)]}),
		'place': fields.char('Signature Place', required=True, states={'done':[('readonly',True)]}),
		'means_payment': fields.selection([('check', 'Check'),('cash', 'Cash'),('transfert','Transfert')], 'Means of payment', states={'done':[('readonly',True)]}),
		'fiscalyear': fields.many2one('account.fiscalyear', 'Fiscal year'),
		'period_from': fields.many2one('account.period', 'Start period'),
		'period_to': fields.many2one('account.period', 'End period'),
		'target_move': fields.selection([('posted', 'All Posted Entries'),('all', 'All Entries')], 'Target Moves'),

		'state': fields.selection([('draft','Draft'),('simulate','Simulate'),('done','Done')], 'Status', required=True, copy=False),
		
		'journal_entry_id': fields.many2one('account.move', 'Journal Entry', copy=False)
	}
	
	_defaults = {
		'user_id': lambda self, cr, uid, context: uid,
		'date_declaration': lambda obj, cr, uid, context: time.strftime('%Y-%m-%d'),
		'date': lambda obj, cr, uid, context: time.strftime('%Y-%m-%d'),
		'place': 'Papeete',
		'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'l10n.pf.account.vat.declaration', context=context),
		'means_payment': 'check',
		'target_move': 'all',
		'fiscalyear': _get_fiscalyear,
		'state': 'draft',
	}
	
	## Cette méthode saisit les écritures comptables
	def enter_journal_items(self, cr, uid, ids, move_id, context=None):
		#import pdb
		#pdb.set_trace()
		ac_mv_line_obj = self.pool.get('account.move.line')
		company_obj = self.pool.get('res.company')
		for field in ['reduced_rate', 'intermediate_rate', 'normal_rate', 'regul_exigible', 'immo', 'goods_services', 'regul_deductible', 'report_credit', 'vat']:
			#Ecritures comptables pour le cas du regime simplifie annuel
			if (self.browse(cr, uid, ids, context=context).company_regime == 'annual'):
				if field == 'reduced_rate':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).reduced_rate_ids[0].account_collected_id.id,
						'debit': self.browse(cr, uid, ids, context=context).vat_due_reduced_rate,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': self.browse(cr, uid, ids, context=context).name  
					}
					if vals['debit'] != 0.0:
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				elif field == 'intermediate_rate':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).intermediate_rate_ids[0].account_collected_id.id,
						'debit': self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': self.browse(cr, uid, ids, context=context).name 
					}
					if vals['debit'] != 0.0:
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				elif field == 'normal_rate':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).normal_rate_ids[0].account_collected_id.id,
						'debit': self.browse(cr, uid, ids, context=context).vat_due_normal_rate,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': self.browse(cr, uid, ids, context=context).name 
					}
					if vals['debit'] != 0.0:
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				elif field == 'immo':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).immo_ids[0].account_collected_id.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_immobilization,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': self.browse(cr, uid, ids, context=context).name 
					}
					if vals['credit'] != 0.0:
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				elif field == 'goods_services':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).others_goods_services_ids[0].account_collected_id.id,
						'credit': self.browse(cr, uid, ids, context=context).vat_other_goods_services,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': self.browse(cr, uid, ids, context=context).name 
					}
					if vals['credit'] != 0.0:
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				elif field == 'report_credit':
					vals = {
						'state': 'valid',
						'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
						'account_id': company_obj.browse(cr, uid, uid, context=context).credit_id.id,
						'credit': self.browse(cr, uid, ids, context=context).defferal_credit,
						'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
						'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
						'name': self.browse(cr, uid, ids, context=context).name 
					}
					if vals['credit'] != 0.0:
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				elif field == 'vat':
					difference = self.browse(cr, uid, ids, context=context).total_vat_payable - self.browse(cr, uid, ids, context=context).total_vat_deductible
					# Cas du régime simplifie annuel
					if self.browse(cr, uid, ids, context=context).company_regime == 'annual':
						if difference > 0:
							vals = {
								'state': 'valid',
								'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
								'account_id': company_obj.browse(cr, uid, uid, context=context).vat_id.id,
								'credit': self.browse(cr, uid, ids, context=context).net_vat_due,
								'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
								'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
								'name': self.browse(cr, uid, ids, context=context).name 
							}
							ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
						else:
							vals = {
								'state': 'valid',
								'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
								'account_id': company_obj.browse(cr, uid, uid, context=context).credit_id.id,
								'debit': self.browse(cr, uid, ids, context=context).surplus,
								'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
								'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
								'name': self.browse(cr, uid, ids, context=context).name 
							}
							ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
			# Ecritures comptables pour le cas du regime reel sur les factures
			elif (self.browse(cr, uid, ids, context=context).company_regime == 'real') and \
				(self.browse(cr, uid, ids, context=context).company_vat_type == 'bills'):
				# Saisie du taux réduit en DEBIT
				if field == 'reduced_rate':
					montant = self.browse(cr, uid, ids, context=context).vat_due_reduced_rate
					if montant > 0:						
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_reduced_rate_ids[0].account_collected_id.id,
							'debit': self.browse(cr, uid, ids, context=context).vat_due_reduced_rate,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					elif montant < 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_reduced_rate_ids[0].account_collected_id.id,
							'credit': abs(self.browse(cr, uid, ids, context=context).vat_due_reduced_rate),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				# Saisie du taux intermédiaire en DEBIT
				elif field == 'intermediate_rate':
					montant = self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate
					if montant > 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_intermediate_rate_ids[0].account_collected_id.id,
							'debit': self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					elif montant < 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_intermediate_rate_ids[0].account_collected_id.id,
							'credit': abs(self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				# Saisie du taux normal en DEBIT
				elif field == 'normal_rate':
					montant = self.browse(cr, uid, ids, context=context).vat_due_normal_rate
					if montant > 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_normal_rate_ids[0].account_collected_id.id,
							'debit': self.browse(cr, uid, ids, context=context).vat_due_normal_rate,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					elif montant < 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_normal_rate_ids[0].account_collected_id.id,
							'credit': abs(self.browse(cr, uid, ids, context=context).vat_due_normal_rate),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				# Saisie de l'immobilisation en CREDIT
				elif field == 'immo':
					montant = self.browse(cr, uid, ids, context=context).vat_immobilization
					if montant > 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_immo_ids[0].account_collected_id.id,
							'credit': self.browse(cr, uid, ids, context=context).vat_immobilization,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					elif montant < 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_immo_ids[0].account_collected_id.id,
							'debit': abs(self.browse(cr, uid, ids, context=context).vat_immobilization),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)

				# Saisie des autres biens et services en CREDIT
				elif field == 'goods_services':
					montant = self.browse(cr, uid, ids, context=context).vat_other_goods_services
					if montant > 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_others_goods_services_ids[0].account_collected_id.id,
							'credit': self.browse(cr, uid, ids, context=context).vat_other_goods_services,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					elif montant < 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_others_goods_services_ids[0].account_collected_id.id,
							'debit': abs(self.browse(cr, uid, ids, context=context).vat_other_goods_services),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				# Saisie du report de crédit en CREDIT
				elif field == 'report_credit':
					montant = self.browse(cr, uid, ids, context=context).defferal_credit
					if montant > 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).credit_id.id,
							'credit': self.browse(cr, uid, ids, context=context).defferal_credit,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					elif montant < 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).credit_id.id,
							'debit': abs(self.browse(cr, uid, ids, context=context).defferal_credit),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)

				# Saisie du crédit de TVA en DEBIT
				# Saisie de la TVA en CREDIT
				elif field == 'vat':
					#import pdb
					#pdb.set_trace()
					difference = abs(self.browse(cr, uid, ids, context=context).total_vat_payable) - abs(self.browse(cr, uid, ids, context=context).total_vat_deductible)
					# TVA
					if difference > 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).vat_id.id,
							'credit': abs(self.browse(cr, uid, ids, context=context).net_vat_due),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					# Crédit de TVA
					else:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).credit_id.id,
							'debit': abs(self.browse(cr, uid, ids, context=context).credit_to_be_transferred),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
			# Ecritures comptables pour le cas du regime reel sur les encaissements
			elif (self.browse(cr, uid, ids, context=context).company_regime == 'real') and \
				(self.browse(cr, uid, ids, context=context).company_vat_type == 'cashing'):
				# Saisie du taux intermédiaire + de sa régularisation en DEBIT
				if field == 'intermediate_rate':
					montant = self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate
					if montant > 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_intermediate_rate_ids[0].account_collected_id.id,
							'debit': self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					elif montant < 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_intermediate_rate_ids[0].account_collected_id.id,
							'credit': abs(self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				# Saisie de l'immobilisation en CREDIT
				elif field == 'immo':
					montant = self.browse(cr, uid, ids, context=context).vat_immobilization
					if montant > 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_immo_ids[0].account_collected_id.id,
							'credit': self.browse(cr, uid, ids, context=context).vat_immobilization,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					elif montant < 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_immo_ids[0].account_collected_id.id,
							'debit': abs(self.browse(cr, uid, ids, context=context).vat_immobilization),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)

				# Saisie des autres biens et services en CREDIT
				elif field == 'goods_services':
					montant = self.browse(cr, uid, ids, context=context).vat_other_goods_services
					if montant > 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_others_goods_services_ids[0].account_collected_id.id,
							'credit': self.browse(cr, uid, ids, context=context).vat_other_goods_services,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					elif montant < 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).tax_others_goods_services_ids[0].account_collected_id.id,
							'debit': abs(self.browse(cr, uid, ids, context=context).vat_other_goods_services),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				# Saisie du report de crédit en CREDIT
				elif field == 'report_credit':
					montant = self.browse(cr, uid, ids, context=context).defferal_credit
					if montant > 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).credit_id.id,
							'credit': self.browse(cr, uid, ids, context=context).defferal_credit,
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					elif montant < 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).credit_id.id,
							'debit': abs(self.browse(cr, uid, ids, context=context).defferal_credit),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)

				# Saisie du crédit de TVA en DEBIT
				# ou de la TVA nette due en CREDIT
				elif field == 'vat':
					difference = abs(self.browse(cr, uid, ids, context=context).total_vat_payable) - abs(self.browse(cr, uid, ids, context=context).total_vat_deductible)
					# TVA
					if difference >= 0:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).vat_id.id,
							'credit': abs(self.browse(cr, uid, ids, context=context).net_vat_due),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
					# Crédit de TVA
					else:
						vals = {
							'move_id': move_id,
							'state': 'valid',
							'journal_id': company_obj.browse(cr, uid, uid, context=context).journal_id.id,
							'account_id': company_obj.browse(cr, uid, uid, context=context).credit_id.id,
							'debit': abs(self.browse(cr, uid, ids, context=context).credit_to_be_transferred),
							'period_id': self.browse(cr, uid, ids, context=context).period_to.id,
							'date': self.browse(cr, uid, ids, context=context).period_to.date_stop,
							'name': self.browse(cr, uid, ids, context=context).name 
						}
						ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
		return True

	def _prepare_move(self, cr, uid, decl_line, decl_line_nb, context=None):
		return {
			'journal_id': decl_line.company_id.journal_id.id,
			'period_id': decl_line.period_to.id,
			'date': decl_line.period_to.date_stop,
			'name':decl_line_nb,
		}

	#def create_journal_items(self, cr, uid, id, mv_line_dicts, context=None):
	def create_journal_items(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		declaration_line = self.browse(cr, uid, ids, context=context)
		am_obj = self.pool.get('account.move')
		aml_obj = self.pool.get('account.move.line')
		
		# Checks
		#if declaration_line.journal_entry_id.id:
			#raise osv.except_osv(_('Error!'), _('The declaration line was already create'))
		#for mv_line_dicts in mv_line_dicts:
			#for field in ['debit', 'credit']:
				#if field not in mv_line_dict:
					#mv_line_dict[field] = 0.0
			#if mv_line_dict.get('counterpart_move_line_id'):
				#mv_line = aml_obj.browse(cr, uid, mv_line_dict.get('counterpart_move_line_id'), context=context)
				#if mv_line.reconcile_id:
					#raise osv.except_osv(_('Error!'), _('A selected move line was already create'))
		
		# Create the move
		move_name = declaration_line.name
		move_vals = self._prepare_move(cr, uid, declaration_line, move_name, context=context)
		move_id = am_obj.create(cr, uid, move_vals, context=context)
		
		self.enter_journal_items(cr, uid, ids, move_id, context=context)	
		self.write(cr, uid, ids, {'journal_entry_id': move_id}, context=context)
		
	## Cette méthode met l'état de la déclaration à "Simuler"
	## et crée les écritures comptables
	def set_to_simulate(self, cr, uid, ids, context=None):
		self.create_journal_items(cr, uid, ids, context=context)
		return self.write(cr, uid, ids, {'state':'simulate'}, context=context)
	
	## Cette méthode met l'état de la déclaration à "Brouillon"
	## et annuler les écritures comptables
	def set_to_draft(self, cr, uid, ids, context=None):
		self.cancel(cr, uid, ids, context=context)
		return self.write(cr, uid, ids, {'state':'draft'}, context=context)

	## Cette méthode valide la déclaration et met son état à "Valider"
	def validate(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		return self.write(cr, uid, ids, {'state':'done'}, context)

	def cancel(self, cr, uid, ids, context=None):
		account_move_obj = self.pool.get('account.move')
		move_ids = []
		for declaration in self.browse(cr, uid, ids, context=context):
			if declaration.journal_entry_id:
				move_ids.append(declaration.journal_entry_id.id)
		if move_ids:
			account_move_obj.button_cancel(cr, uid, move_ids, context=context)
			account_move_obj.unlink(cr, uid, move_ids, context)

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
				'ntahiti': company.ntahiti,
			}
		return {'value':values}
			
	def on_change_fiscalyear(self, cr, uid, ids, fiscalyear_id=False, context=None):
		#import pdb
		#pdb.set_trace()
		company = self.pool.get('res.company')
		period = self.pool.get('account.period')
		periods = period.search(cr, uid, [])
		
		today = datetime.now()
		res = {}
		temp_to = 0
		temp_from = 0
		is_t1 = False
		cas_m1 = False
		
		#Cas 1: Par Trimestre
		if company.browse(cr, uid, uid, context=context).period_declaration == 'trimester':
			#La déclaration se fait en janvier 01
			#if today.month == 1:
				#m_from = today.month + 9
				#m_to = today.month + 11
				#y = today.year - 1
			#else:
				#m_from = today.month - 3
				#m_to = today.month - 1
			m_from = today.month - 3
			m_to = today.month - 1
			past_to = datetime(today.year,m_to,today.day)
			past_from = datetime(today.year,m_from,today.day)
			#past_to = datetime(y,m_to,today.day)
			#past_from = datetime(y,m_from,today.day)
			#if fiscalyear_id.date_start.year > y:
			for i in period.browse(cr, uid, periods, context=context):
				d_start = datetime.strptime(i.date_start, '%Y-%m-%d')
				d_stop = datetime.strptime(i.date_stop, '%Y-%m-%d')
				if (d_start <= past_to) and (d_stop >= past_to):
					print 'TO'
					temp_to = i.id
				#Cas 1.1: T1 - ouverture à 01/XXXX
				if (d_start.month == past_from.month) and (past_from.month == d_stop.month):
					is_t1 = True
				if (d_start.month == past_from.month) and (past_from.month == d_stop.month) and (i.fiscalyear_id.id == fiscalyear_id) and (is_t1 == True):
					print 'FROM_True'
					temp_from = i.id
				elif (d_start.month == past_from.month) and (past_from.month <= d_stop.month) and (i.fiscalyear_id.id == fiscalyear_id) and (is_t1 == False):
					print 'FROM_False'
					temp_from = i.id
		# Cas 2: Par Mois
		elif company.browse(cr, uid, uid, context=context).period_declaration == 'month':
			#if today.month == 1:
				#m = today.month + 11
			#else: 
				#m = today.month - 1
			m = today.month - 1
			past = datetime(today.year,m,today.day)
			for i in period.browse(cr, uid, periods, context=context):
				is_m1 = False
				d_start = datetime.strptime(i.date_start, '%Y-%m-%d')
				d_stop = datetime.strptime(i.date_stop, '%Y-%m-%d')
				if (d_start == d_stop) and (i.fiscalyear_id.id == fiscalyear_id):
					is_m1 = True
				if (d_start == d_stop) and (past.month == d_start.month) and (past.month == d_stop.month) and (i.fiscalyear_id.id == fiscalyear_id):
					print 'From_00'
					temp_from = i.id
					cas_m1 = True
				if (d_start <= past) and (past <= d_stop) and (i.fiscalyear_id.id == fiscalyear_id):
					if cas_m1 == True:
						print 'To_01'
						temp_to = i.id
					else:
						print 'From_others'
						temp_to = i.id
						temp_from = i.id
		res['value'] = {'period_to': temp_to, 'period_from':temp_from}
		return res
