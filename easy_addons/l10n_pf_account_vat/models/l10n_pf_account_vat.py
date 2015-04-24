# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp

from openerp.osv import fields, osv
from openerp import models, api, _

class l10n_pf_account_vat_declaration(models.Model):
	_name = 'l10n.pf.account.vat.declaration'
	_description = 'Vat declaration'

	# Méthode qui retourne l'exercice N - 1
	def fiscalyear_past(self, cr, uid, context=None):
		# On récupère les exercices
		fy_obj = self.pool.get('account.fiscalyear')
		fy_ids = fy_obj.search(cr, uid, [])
		# Date actuelle
		today = datetime.now()
		# On va récupérer l'exercice N - 1
		for item in fy_obj.browse(cr, uid, fy_ids, context=context):
			if datetime.strptime(item.date_stop, '%Y-%m-%d').year == today.year - 1:
				fy = item.id
		return fy

	# Méthode qui retourne l'exercice selon le cas
	def _get_fiscalyear(self, cr, uid, context=None):
		# Récupérer la compagnie
		company_obj = self.pool.get('res.company')
		company_id = company_obj._company_default_get(cr, uid, context=context)
		company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
		
		# Exercice de la date actuelle
		fy = self.pool.get('account.fiscalyear').find(cr, uid, context=context)		
		# Date actuelle
		today = datetime.now()
		
		# Cas d'une déclaration annuelle en régime simplifié effectué le mois de mars de l'année suivante
		if (company.regime_vat == 'simplified' and today.month == 3) or (company.regime_vat == 'real' and today.month == 1):
			fy = self.fiscalyear_past(cr, uid, context=context)
		return fy

	# Méthode qui retourne la période de début selon le cas
	def _get_period_from(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		
		# Récupérer la compagnie
		company_obj = self.pool.get('res.company')
		company_id = company_obj._company_default_get(cr, uid, context=context)
		company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
		# Date actuelle
		today = datetime.now()

		# Récupérer l'exercice fiscal
		fy = self.pool.get('account.fiscalyear').find(cr, uid, context=context)
		
		# Changer l'exercice si on est dans le cas de la déclaration annuelle en régime simplifié
		if (company.regime_vat == 'simplified' and today.month == 3) or (company.regime_vat == 'real' and today.month == 1):
			fy = self.fiscalyear_past(cr, uid, context=context)
			
		# Récupérer les périodes de l'exercice en cours
		period = self.pool.get('account.period')
		periods = period.search(cr, uid, [('fiscalyear_id.id','=', fy), ('special', '=', False)])

		res = 0
		m_from = 0
		
		# Cas régime réel
		if company.regime_vat == 'real':
			# On détermine si la déclaration se fait en Janvier
			first_month = False
			if today.month == 1:
				first_month = True
			##Cas 1: Par Trimestre
			if company.period_declaration == 'trimester':
				if first_month:
					m_from = today.month + 9
				elif not first_month:
					m_from = today.month - 3
			#Cas 2: Par Mois
			elif company.period_declaration == 'month':
				if first_month:
					m_from = today.month + 11
				elif not first_month:
					m_from = today.month - 1
		# Cas régime simplifié
		elif company.regime_vat == 'simplified':
			# Acompte
			if today.month == 9:
				m_from = today.month - 8
			# Annuelle
			elif today.month == 3:
				m_from = today.month - 2
		# Récupérer la bonne période
		for i in period.browse(cr, uid, periods, context=context):
			d_stop = datetime.strptime(i.date_stop, '%Y-%m-%d')
			if (d_stop.month == m_from):
				res = i.id
		return res
	
	# Méthode qui retourne la période de fin selon le cas
	def _get_period_to(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		
		# Récupérer la compagnie
		company_obj = self.pool.get('res.company')
		company_id = company_obj._company_default_get(cr, uid, context=context)
		company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
		# Date actuelle
		today = datetime.now()

		# Récupérer l'exercice fiscal
		fy = self.pool.get('account.fiscalyear').find(cr, uid, context=context)
		
		# Changer l'exercice si on est dans le cas de la déclaration annuelle en régime simplifié
		if company.regime_vat == 'simplified' and today.month == 3 or (company.regime_vat == 'real' and today.month == 1):
			fy = self.fiscalyear_past(cr, uid, context=context)
		
		# Récupérer les périodes de l'exercice en cours
		period = self.pool.get('account.period')
		periods = period.search(cr, uid, [('fiscalyear_id.id','=', fy), ('special', '=', False)])
		
		res = 0
		# On détermine si la déclaration se fait en Janvier
		first_month = False
		if today.month == 1:
			first_month = True
		
		if first_month:
			m_to = today.month + 11
		elif not first_month:
			m_to = today.month - 1
		
		# Cas annuelle en régime simplifié
		if company.regime_vat == 'simplified' and today.month == 3:
			m_to = today.month + 9
		
		# Récupérer la bonne période
		for i in period.browse(cr, uid, periods, context=context):
			d_stop = datetime.strptime(i.date_stop, '%Y-%m-%d')
			if (d_stop.month == m_to):
				res = i.id
		return res

	# Méthode qui retourne le bonne type de déclaration selon si on est en acompte ou en annuelle
	def _get_type_simplified(self, cr, uid, ids, context=None):
		res = ''
		p_to_id = self._get_period_to(cr, uid, ids, context=context)
		p_to = self.pool.get('account.period').browse(cr, uid, p_to_id, context=context)

		if p_to_id != 0 and datetime.strptime(p_to.date_stop, '%Y-%m-%d').month == 8:
			res = 'deposit'
		elif p_to_id != 0 and datetime.strptime(p_to.date_stop, '%Y-%m-%d').month == 12:
			res = 'annual'
		return res

	def account_chart_open_window(self, cr, uid, ids, context=None):
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		period_obj = self.pool.get('account.period')
		fy_obj = self.pool.get('account.fiscalyear')
		dec_obj = self.browse(cr, uid, ids, context=context)
		if context is None:
			context = {}
		data = self.read(cr, uid, ids, context=context)[0]
		result = mod_obj.get_object_reference(cr, uid, 'account', 'action_account_tree')
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		fiscalyear_id = data.get('fiscalyear', False) and data['fiscalyear'][0] or False
		result['periods'] = []
		if data['period_from'] and data['period_to']:
			period_from = dec_obj.fiscalyear.period_ids[0].id
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
			'immo_ids', 'others_goods_services_ids', 'sales_ids', 'services_ids', 'credit_ids', 'deposit', 'reimbursement']:
				res = 0.0
				period = self.pool.get('account.period')
				special_period = period.search(cr, uid, [('fiscalyear_id.id','=', decl.fiscalyear.id), ('special', '=', True)])
				#Contexte pour calculer les balances de l'année en cours	
				ctx_n = {
					'fiscalyear': decl.fiscalyear.id,
					'period_from': special_period[0],
					'period_to': decl.period_to.id,
					'target_move': decl.target_move
				}
				# Cas régime réel (Factures et encaissements) + Cas régime simplifié (Annuelle)
				if (decl.company_regime == 'real') or (decl.company_regime == 'simplified' and decl.type_simplified == 'annual'):
					# Récupérer le montant des comptes des exportations
					if field == 'exports_ids':
						for i in (ac for ac in decl.company_id.exports_ids if ac != None):
							res = res + i.balance
						decl.update({'account_exports': -res})
					# Récupérer le montant des autres opérations non taxables
					elif field == 'others_ids':
						for i in (ac for ac in decl.company_id.others_ids if ac != None):
							res = res + i.balance
						decl.update({'account_other': -res})
					# Annuelle en régime simplifié OU Régime réel sur les factures
					if (decl.type_simplified == 'annual') or (decl.company_vat_type == 'bills'):
						if field == 'reduced_rate_ids':
							my_list = []
							# On récupère tous les comptes qui se trouvent dans la Taxe
							for i in (tx for tx in self.browse(cr, uid, ids, context=ctx_n).company_id.tax_reduced_rate_ids if tx != None):
								my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
							# On supprime les doublons
							my_list = list(set(my_list))
							# On parcourt la liste des comptes triés pour avoir le total des balances
							for index, obj in enumerate(my_list):
								res = res + my_list[index].balance
							decl.update({'vat_due_reduced_rate': -res})
						elif field == 'intermediate_rate_ids':
							my_list = []
							# On récupère tous les comptes qui se trouvent dans la Taxe
							for i in (tx for tx in self.browse(cr, uid, ids, context=ctx_n).company_id.tax_intermediate_rate_ids if tx != None):
								my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
							# On supprime les doublons
							my_list = list(set(my_list))
							# On parcourt la liste des comptes triés pour avoir le total des balances
							for index, obj in enumerate(my_list):
								res = res + my_list[index].balance
							decl.update({'vat_due_intermediate_rate': -res})
						elif field == 'normal_rate_ids':
							my_list = []
							# On récupère tous les comptes qui se trouvent dans la Taxe
							for i in (tx for tx in self.browse(cr, uid, ids, context=ctx_n).company_id.tax_normal_rate_ids if tx != None):
								my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
							# On supprime les doublons
							my_list = list(set(my_list))
							# On parcourt la liste des comptes triés pour avoir le total des balances
							for index, obj in enumerate(my_list):
								res = res + my_list[index].balance
							decl.update({'vat_due_normal_rate': -res})
						elif field == 'immo_ids':
							my_list = []
							# On récupère tous les comptes qui se trouvent dans la Taxe
							for i in (tx for tx in self.browse(cr, uid, ids, context=ctx_n).company_id.tax_immo_ids if tx != None):
								my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
							# On supprime les doublons
							my_list = list(set(my_list))
							# On parcourt la liste des comptes triés pour avoir le total des balances
							for index, obj in enumerate(my_list):
								res = res + my_list[index].balance
							decl.update({'vat_immobilization': res})
						elif field == 'others_goods_services_ids':
							my_list = []
							# On récupère tous les comptes qui se trouvent dans la Taxe
							for i in (tx for tx in self.browse(cr, uid, ids, context=ctx_n).company_id.tax_others_goods_services_ids if tx != None):
								my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
							# On supprime les doublons
							my_list = list(set(my_list))
							# On parcourt la liste des comptes triés pour avoir le total des balances
							for index, obj in enumerate(my_list):
								res = res + my_list[index].balance
							decl.update({'vat_other_goods_services': res})
						elif field == 'deposit':
							if decl.type_simplified == 'annual':
								search_ids = self.search(cr, uid, [('type_simplified','=','deposit'), ('fiscalyear', '=', decl.fiscalyear.id)])
								for obj in self.browse(cr, uid, search_ids, context=context):
									if obj.state == 'done':
										decl.update({'deposit': obj.net_vat_due})
						elif field == 'reimbursement':
							if decl.type_simplified == 'annual':
								search_ids = self.search(cr, uid, [('type_simplified','=','deposit'), ('fiscalyear', '=', decl.fiscalyear.id)])
								for obj in self.browse(cr, uid, search_ids, context=context):
									if obj.state == 'done':
										decl.update({'obtained_reimbursement': obj.reimbursement}) 
						elif field == 'credit_ids':
							# Récupérer les déclarations sur les factures et celles annuelles
							search_ids = self.search(cr, uid, ['|', ('company_vat_type', '=', 'bills'), ('type_simplified', '=', 'annual')])
							for obj in self.browse(cr, uid, search_ids, context=context):
								# Cas annuelle en régime simplifié
								if decl.type_simplified == 'annual':
									# Date de début de la période de fin de la déclaration actuelle
									d1 = datetime.strptime(decl.period_to.date_start, '%Y-%m-%d')
									# Date de début de la période de fin de la déclaration i
									d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
									# Récupérer le crédit à reporter si la déclaration est validée
									if (str(d1.year) == str(d2.year + 1)) and (obj.state == 'done') and (decl.company_regime == obj.company_regime):
										decl.update({'defferal_credit': obj.credit_to_be_transferred})
										print obj.credit_to_be_transferred
								# Cas régime réel sur les factures
								elif decl.company_vat_type == 'bills':
									# Date de début de la période de fin de la déclaration actuelle
									d1 = datetime.strptime(decl.period_to.date_start, '%Y-%m-%d')
									# Date de début de la période de fin de la déclaration i
									d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
									# Cas où on veut récupérer le report de crédit du T4 ou du M12 de l'exercice précédent
									if str(d1.year) == str(d2.year + 1):
										if decl.period_declaration == 'month' and (str(d1.month) == str(d2.month - 11)) and (obj.state == 'done'):
											decl.update({'defferal_credit': obj.credit_to_be_transferred})
										elif decl.period_declaration == 'trimester' and (str(d1.month) == str(d2.month - 9)) and (obj.state == 'done'):
											decl.update({'defferal_credit': obj.credit_to_be_transferred})
									# Autres cas
									elif str(d1.year) == str(d2.year):
										if decl.period_declaration == 'month' and (str(d1.month - 1) == str(d2.month)) and (obj.state == 'done'):
											decl.update({'defferal_credit': obj.credit_to_be_transferred})
										elif decl.period_declaration == 'trimester' and (str(d1.month) == str(d2.month + 3)) and (obj.state == 'done'):
											decl.update({'defferal_credit': obj.credit_to_be_transferred})
					# Régime réel sur les encaissements
					elif decl.company_vat_type == 'cashing':
						#Contexte pour calculer la balance au 1er jour de l'exercice
						ctx_open = {
								'fiscalyear': decl.fiscalyear.id,
								'period_from': special_period[0],
								'period_to': special_period[0],
								'target_move': decl.target_move
						}
						if field == 'intermediate_rate_ids':
							compte_client_n = 0.0
							chiffre_n = 0.0
							taux_inter_n = 0.0
							compte_client_n_1 = 0.0
							deja_declare = 0.0
							# on recupere le montant du 411 pour l'annee N
							for i in (ac for ac in self.browse(cr, uid, ids, context=ctx_n).company_id.customers_ids if ac != None):
								compte_client_n = compte_client_n + i.balance
							# on recupere le montant du 706 pour l'annee N
							for i in (ac for ac in self.browse(cr, uid, ids, context=ctx_n).company_id.turnover_ids if ac != None):
								chiffre_n = chiffre_n + i.balance
							# on  recupere le montant du taux intermédiaire pour l'annee N
							my_list = []
							# On récupère tous les comptes qui se trouvent dans la Taxe
							for i in (tx for tx in self.browse(cr, uid, ids, context=ctx_n).company_id.tax_intermediate_rate_ids if tx != None):
								my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
							print my_list
							# On supprime les doublons
							my_list = list(set(my_list))
							print my_list
							# On parcourt la liste des comptes triés pour avoir le total des balances
							for index,obj in enumerate(my_list):
								taux_inter_n = taux_inter_n + my_list[index].balance
							# on recupere la balance 411 dans la periode d'ouverture de l'annee N
							for i in (ac for ac in self.browse(cr, uid, ids, context=ctx_open).company_id.customers_ids if ac != None):
								compte_client_n_1 = compte_client_n_1 + i.balance
							# Montant déjà déclaré
							decl_ids = self.search(cr, uid, [('fiscalyear', '=', decl.fiscalyear.id), ('state', '=', 'done')])
							print decl_ids
							for j in self.browse(cr, uid, decl_ids, context=context):
								deja_declare = deja_declare + j.vat_due_intermediate_rate
							# Calcul du montant TTC
							ttc = -(compte_client_n_1 - chiffre_n - taux_inter_n - compte_client_n)
							# Calcul du montant HT
							ht = decl.company_id.tax_intermediate_rate_ids and \
								decl.company_id.currency_id.round((ttc / (1 + decl.company_id.tax_intermediate_rate_ids[0].amount)) or 0.0) or 0.0
							# Calcul du montant de la prestation à déclarer
							prestation = ht - deja_declare
							# Calcul du montant de la TVA due de la prestation
							res = decl.company_id.tax_intermediate_rate_ids and \
								decl.company_id.currency_id.round((prestation * decl.company_id.tax_intermediate_rate_ids[0].amount) or 0.0) or 0.0
							decl.update({'vat_due_intermediate_rate': -res})
						elif field == 'immo_ids':
							my_list = []
							# On récupère tous les comptes qui se trouvent dans la Taxe
							for i in (tx for tx in self.browse(cr, uid, ids, context=ctx_n).company_id.tax_immo_ids if tx != None):
								my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
							# On supprime les doublons
							my_list = list(set(my_list))
							# On parcourt la liste des comptes triés pour avoir le total des balances
							for index,obj in enumerate(my_list):
								res = res + my_list[index].balance
							decl.update({'vat_immobilization': res})
						elif field == 'others_goods_services_ids':
							my_list = []
							# On récupère tous les comptes qui se trouvent dans la Taxe
							for i in (tx for tx in self.browse(cr, uid, ids, context=ctx_n).company_id.tax_others_goods_services_ids if tx != None):
								my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
							# On supprime les doublons
							my_list = list(set(my_list))
							# On parcourt la liste des comptes triés pour avoir le total des balances
							for index,obj in enumerate(my_list):
								res = res + my_list[index].balance
							decl.update({'vat_other_goods_services': res})
						elif field == 'credit_ids':
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
				# Cas régime simplifié (Acompte)
				elif (decl.company_regime == 'simplified' and decl.type_simplified == 'deposit'):
					if field == 'sales_ids':
						for i in (ac for ac in decl.company_id.sales_ids if ac != None):
							res = res + i.balance
						decl.update({'excluding_vat_sales': -res})
					elif field == 'services_ids':
						for i in (ac for ac in decl.company_id.services_ids if ac != None):
							res = res + i.balance
						decl.update({'excluding_vat_services': -res})
					elif field == 'immo_ids':
						my_list = []
						# On récupère tous les comptes qui se trouvent dans la Taxe
						for i in (tx for tx in self.browse(cr, uid, ids, context=ctx_n).company_id.tax_immo_ids if tx != None):
							my_list = my_list + list(i.account_collected_id) + list(i.account_paid_id)
						# On supprime les doublons
						my_list = list(set(my_list))
						# On parcourt la liste des comptes triés pour avoir le total des balances
						for index, obj in enumerate(my_list):
							res = res + my_list[index].balance
						decl.update({'vat_immobilization': res})
					elif field == 'credit_ids':
						# Récupérer les déclarations sur les factures et celles annuelles
						search_ids = self.search(cr, uid, [('type_simplified', '=', 'deposit')])
						for obj in self.browse(cr, uid, search_ids, context=context):
							# Date de début de la période de fin de la déclaration actuelle
							d1 = datetime.strptime(decl.period_to.date_start, '%Y-%m-%d')
							# Date de début de la période de fin de la déclaration i
							d2 = datetime.strptime(obj.period_to.date_start, '%Y-%m-%d')
							# Récupérer le crédit à reporter si la déclaration est validée
							if (str(d1.year) == str(d2.year + 1)) and (obj.state == 'done'):
								decl.update({'defferal_credit': obj.vat_credit})
		decl.update({'state': 'fill'})				
		return True

	## Cette fonction calcule le montant des bases hors TVA
	@api.one
	@api.depends('vat_due_reduced_rate','vat_due_intermediate_rate','vat_due_normal_rate','company_id','company_vat_type')
	def _compute_amount_base(self):
		self.base_reduced_rate = self.company_id.tax_reduced_rate_ids and self.company_id.currency_id.round((self.vat_due_reduced_rate / self.company_id.tax_reduced_rate_ids[0].amount) or 0.0) or 0.0
		self.base_intermediate_rate = self.company_id.tax_intermediate_rate_ids and self.company_id.currency_id.round((self.vat_due_intermediate_rate / self.company_id.tax_intermediate_rate_ids[0].amount) or 0.0) or 0.0
		self.base_normal_rate = self.company_id.tax_normal_rate_ids and self.company_id.currency_id.round((self.vat_due_normal_rate / self.company_id.tax_normal_rate_ids[0].amount) or 0.0) or 0.0

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
	@api.depends('type_simplified','vat_immobilization','vat_other_goods_services','vat_regularization','defferal_credit')
	def _compute_total_deductible(self):
		if self.type_simplified == 'deposit':
			self.total_vat_deductible = self.vat_immobilization + self.defferal_credit
		else:
			self.total_vat_deductible = self.vat_immobilization + self.vat_other_goods_services + self.vat_regularization + self.defferal_credit

	## Cette fonction calcule le montant de la TVA ou du crédit de TVA selon les cas
	@api.one
	@api.depends('total_vat_payable','total_vat_deductible','total_tax_payable','type_simplified','deposit','obtained_reimbursement')
	def _compute_amount_vat(self):
		# Différence pour l'acompte
		diff1 = abs(self.total_tax_payable) - abs(self.total_vat_deductible)
		# Différence pour l'annuelle et les réels
		diff2 = abs(self.total_vat_payable) - abs(self.total_vat_deductible)

		# Cas de l'acompte
		if self.type_simplified == 'deposit':
			if diff1 > 0:
				self.net_vat_due = abs(self.total_tax_payable) - abs(self.total_vat_deductible)
				self.vat_credit = 0.0
			elif diff1 < 0:
				self.vat_credit = abs(self.total_vat_deductible) - abs(self.total_tax_payable)
				self.net_vat_due = 0.0
		# Cas du régime réel
		elif self.company_regime == 'real':
			if diff2 > 0:
				self.net_vat_due = abs(self.total_vat_payable) - abs(self.total_vat_deductible)
				self.vat_credit = 0.0
			elif diff2 < 0:
				self.vat_credit = abs(self.total_vat_deductible) - abs(self.total_vat_payable)
				self.net_vat_due = 0.0
		# Cas de l'annuelle
		elif self.type_simplified == 'annual':
			# TVA A PAYER
			if diff2 > 0:
				self.difference_payable_deductible = diff2
				self.difference_deductible_payable = 0.0
				self.total_difference_deposit = self.difference_deductible_payable + self.deposit
				self.total_difference_reimbursement = self.difference_payable_deductible + self.obtained_reimbursement
				self.net_vat_due = self.total_difference_reimbursement - self.total_difference_deposit
				self.surplus = 0.0
			# CREDIT
			elif diff2 < 0:
				self.difference_deductible_payable = -diff2
				self.difference_payable_deductible = 0.0
				self.total_difference_deposit = self.difference_deductible_payable + self.deposit
				self.total_difference_reimbursement = self.difference_payable_deductible + self.obtained_reimbursement
				self.surplus = self.total_difference_deposit - self.total_difference_reimbursement
				self.net_vat_due = 0.0

	## Cette fonction calcule le montant du crédit à reporter
	@api.one
	@api.depends('vat_credit', 'reimbursement', 'surplus', 'company_regime', 'type_simplified')
	def _compute_credit_to_reported(self):
		if self.type_simplified == 'annual':
			self.credit_to_be_transferred = self.surplus - self.reimbursement
		elif self.company_regime == 'real' or self.type_simplified == 'deposit':
			self.credit_to_be_transferred = self.vat_credit - self.reimbursement

	@api.one
	@api.depends('excluding_vat_sales','excluding_vat_services','company_id')
	def _compute_tax_due(self):
		# Le coefficient de l'entreprise correspond à celui donné par le DICP (Actuellement à 5%)
		self.tax_due_sales = self.excluding_vat_sales * 0.05 or 0.0
		self.tax_due_services = self.excluding_vat_services * 0.05 or 0.0

	@api.one
	@api.depends('base_reduced_rate', 'base_intermediate_rate', 'base_normal_rate', 'base_regularization_to_donate', 'company_vat_type', 'company_regime', 'type_simplified')
	def _compute_amount_transaction(self):
		if self.company_vat_type == 'cashing' and self.company_regime == 'real':
			self.account_services = self.base_intermediate_rate + self.base_regularization_to_donate
		elif self.type_simplified == 'annual' or (self.company_regime == 'real' and self.company_vat_type == 'bills'):
			self.account_sales = self.base_reduced_rate + self.base_normal_rate
			self.account_services = self.base_intermediate_rate

	_columns = {
		'name': fields.char('Declaration name', required=True, states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'date_declaration': fields.date('Declaration date', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'account_id': fields.many2one('account.account', 'Account'),

		'ntahiti': fields.char('No Tahiti', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'company_id': fields.many2one('res.company','Company',required=True, states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'company_activity': fields.char('Activity', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'company_phone': fields.char('Telephone', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'company_street': fields.char('Street', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'company_city': fields.char('City', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'company_country': fields.char('Country', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'company_email': fields.char('Email', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'company_zip': fields.char('ZIP', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'company_bp': fields.char('BP', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'city_zip': fields.char('City ZIP', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'company_regime': fields.selection([('simplified', 'Simplified regime'),('real', 'Real regime')], 'Regime', \
							states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}, required=True),
		'company_vat_type': fields.selection([('cashing', 'Cashing vat'), ('bills', 'Bills vat')], 'Type VAT', \
							states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		
		'type_simplified': fields.selection([('deposit', 'Deposit in simplified regime'), ('annual', 'Annual in simplified regime')], \
							'Type simplified', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		
		'period_declaration': fields.selection([('month', 'Month'), ('trimester', 'Trimester')], 'Declaration period', \
								states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),

		'user_id': fields.many2one('res.users','Responsible',required=True, states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),

		'account_sales': fields.float('Sales', store=True, compute='_compute_amount_transaction', \
							states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'account_services': fields.float('Services', store=True, compute='_compute_amount_transaction', \
							states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'account_exports': fields.float('Exports', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'account_other': fields.float('Other', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),

		'base_reduced_rate': fields.float('Base reduced rate', store=True, compute='_compute_amount_base', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'base_intermediate_rate': fields.float('Base intermediate rate', store=True, compute='_compute_amount_base', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'base_normal_rate': fields.float('Base normal rate', store=True, compute='_compute_amount_base', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'base_regularization_to_donate': fields.float('Base regularization to donate', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),

		'vat_due_reduced_rate': fields.float('Vat due reduced rate', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'vat_due_intermediate_rate': fields.float('Vat due intermediate rate', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'vat_due_normal_rate': fields.float('Vat due normal rate', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'vat_due_regularization_to_donate': fields.float('Vat due regularization to donate', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'total_vat_payable': fields.float('Total vat payable', store=True, compute='_compute_total_due', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),

		'vat_immobilization': fields.float('Vat immobilization', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'vat_other_goods_services': fields.float('Vat other goods and services', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'vat_regularization': fields.float('Regularization', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'defferal_credit': fields.float('Defferal credit', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'total_vat_deductible': fields.float('Total vat deductible', store=True, compute='_compute_total_deductible', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),

		'vat_credit': fields.float('Vat credit', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'reimbursement': fields.float('Reimbursement', states={'done':[('readonly',True)]}),
		'credit_to_be_transferred': fields.float('Credit to be transferred', store=True, compute='_compute_credit_to_reported', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'net_vat_due': fields.float('Net vat due', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),

		'excluding_vat_sales': fields.float('Excluding vat sales', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'excluding_vat_services': fields.float('Excluding vat services', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'tax_due_sales': fields.float('Tax due sales', store=True, compute='_compute_tax_due', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'tax_due_services': fields.float('Tax due services', store=True, compute='_compute_tax_due', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'total_tax_payable': fields.float('Total tax payable', store=True, compute='_compute_total_taxe_due', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),

		'difference_deductible_payable': fields.float('Difference', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'deposit': fields.float('Deposit', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'total_difference_deposit': fields.float('Total', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'surplus': fields.float('Surplus', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'difference_payable_deductible': fields.float('Difference', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'obtained_reimbursement': fields.float('Reimbursement obtained', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'total_difference_reimbursement': fields.float('Total', store=True, compute='_compute_amount_vat', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),

		'date': fields.date('Signature Date', required=True, states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'place': fields.char('Signature Place', required=True, states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'means_payment': fields.selection([('check', 'Check'),('cash', 'Cash'),('transfert','Transfert')], 'Means of payment', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'fiscalyear': fields.many2one('account.fiscalyear', 'Fiscal year', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'period_from': fields.many2one('account.period', 'Start period', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'period_to': fields.many2one('account.period', 'End period', states={'done':[('readonly',True)], 'simulate':[('readonly',True)]}),
		'target_move': fields.selection([('posted', 'All Posted Entries'),('all', 'All Entries')], 'Target Moves'),

		'state': fields.selection([('draft', 'Draft'), ('fill', 'Fill'), ('simulate', 'Simulate'), ('done', 'Done')], 'Status', required=True, copy=False),

		'journal_entry_id': fields.many2one('account.move', 'Journal Entry', copy=False, readonly=True, index=True, help='Link to the automatically generated journal items'),
		
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
		'period_from': _get_period_from,
		'period_to': _get_period_to,
		'type_simplified': _get_type_simplified,
	}
	
	@api.multi
	def unlink(self):
		for declaration in self:
			if declaration.state not in ('draft'):
				raise Warning(_('You cannot delete an declaration which is not draft.'))
			elif declaration.journal_entry_id:
				raise Warning(_('You cannot delete a declaration after it has been validated.'))
		return super(l10n_pf_account_vat_declaration, self).unlink()

	def cancel(self, cr, uid, ids, context=None):
		account_move_obj = self.pool.get('account.move')
		move_ids = []
		for declaration in self.browse(cr, uid, ids, context=context):
			if declaration.journal_entry_id:
				move_ids.append(declaration.journal_entry_id.id)
		if move_ids:
			account_move_obj.button_cancel(cr, uid, move_ids, context=context)
			account_move_obj.unlink(cr, uid, move_ids, context)

	## Cette méthode met l'état de la déclaration à "Brouillon"
	## et annuler les écritures comptables si elles ne sont pas comptabilisées
	def set_to_draft(self, cr, uid, ids, context=None):
		declaration = self.browse(cr, uid, ids, context=context)
		if declaration.journal_entry_id.state == 'posted':
			raise Warning(_('Vous ne pouvez pas supprimer des écritures déjà comptabilisées. \
								Vous devez d abord annuler les entrées qui se trouvent dans le journal.'))
		elif declaration.journal_entry_id.state == 'draft':
			self.cancel(cr, uid, ids, context=context)
		return self.write(cr, uid, ids, {'state':'draft'}, context=context)

	## Cette méthode valide la déclaration et met son état à "Valider"
	def validate(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		declaration = self.browse(cr, uid, ids, context=context)
		if declaration.journal_entry_id.state != 'posted' and declaration.type_simplified != 'deposit':
			raise Warning(_('Vous devez comptabiliser les écritures avant de valider la déclaration.'))
		elif declaration.journal_entry_id.state == 'posted' or declaration.type_simplified == 'deposit':
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
				'ntahiti': company.ntahiti,
				'period_declaration': company.period_declaration,
			}
		return {'value': values}
