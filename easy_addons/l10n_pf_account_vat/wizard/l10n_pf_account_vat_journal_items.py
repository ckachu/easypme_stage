# -*- coding: utf-8 -*-

from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import models, fields, api

class l10n_pf_account_vat_journal_items(models.TransientModel):
	"""
	For create Journal Items
	"""
	_name = "l10n.pf.account.vat.journal.items"
	_description = "L10n Pf Account Vat Journal Items"

	# TODO: Mettre une alerte si l'utilisateur ne choisit aucun compte pour les régul

	## Champs
	vat_due_reduced_rate = fields.Float(string="Vat due reduced rate", readonly=True)
	vat_due_intermediate_rate = fields.Float(string="Vat due intermediate rate", readonly=True)
	vat_due_normal_rate = fields.Float(string="Vat due normal rate", readonly=True)
	vat_due_regularization_to_donate = fields.Float(string="Vat due regularization to donate", readonly=True)
	vat_immobilization = fields.Float(string="Vat immobilization", readonly=True)
	vat_other_goods_services = fields.Float(string="Vat other goods and services", readonly=True)
	vat_regularization = fields.Float(string="Vat regularization to deduced", readonly=True)
	defferal_credit = fields.Float(string="Defferal credit", readonly=True) 
	credit_or_vat = fields.Float(string="Credit or Vat", readonly=True)
	account_regul_due = fields.Many2one('account.account', string="Account for regularization due")
	account_regul_deduc = fields.Many2one('account.account', string="Account for regularization deductible")
	
	def default_get(self, cr, uid, fields, context=None):
		if context is None:
			context = {}
		declaration_obj = self.pool.get('l10n.pf.account.vat.declaration')
		res = super(l10n_pf_account_vat_journal_items, self).default_get(cr, uid, fields, context=context)
		declaration_id = context.get('active_id', False)
		declaration = declaration_obj.browse(cr, uid, declaration_id, context=context)
		if 'vat_due_reduced_rate' in fields:
			res.update({'vat_due_reduced_rate': declaration.vat_due_reduced_rate})
		if 'vat_due_intermediate_rate' in fields:
			res.update({'vat_due_intermediate_rate': declaration.vat_due_intermediate_rate})
		if 'vat_due_normal_rate' in fields:
			res.update({'vat_due_normal_rate': declaration.vat_due_normal_rate})
		if declaration.vat_due_regularization_to_donate != 0.0:
			if 'vat_due_regularization_to_donate' in fields:
				res.update({'vat_due_regularization_to_donate': declaration.vat_due_regularization_to_donate})
		if 'vat_immobilization' in fields:
			res.update({'vat_immobilization': declaration.vat_immobilization})
		if 'vat_other_goods_services' in fields:
			res.update({'vat_other_goods_services': declaration.vat_other_goods_services})
		if declaration.vat_regularization != 0.0:
			if 'vat_regularization' in fields:
				res.update({'vat_regularization': declaration.vat_regularization})
		if 'defferal_credit' in fields:
			res.update({'defferal_credit': declaration.defferal_credit})
		if 'credit_or_vat' in fields:
			if (declaration.total_vat_payable - declaration.total_vat_deductible) > 0:
				res.update({'credit_or_vat': declaration.net_vat_due})
			elif (declaration.total_vat_payable - declaration.total_vat_deductible) < 0:
				res.update({'credit_or_vat': declaration.type_simplified == 'annual' and declaration.surplus or declaration.vat_credit})
		return res

	def _prepare_move(self, cr, uid, decl_line, decl_line_nb, context=None):
		if not decl_line.company_id.journal_id:
			raise Warning('You cannot create journal items. Missing journal.')
		return {
			'journal_id': decl_line.company_id.journal_id.id,
			'period_id': decl_line.period_to.id,
			'date': decl_line.period_to.date_stop,
			'ref':decl_line_nb,
		}

	def enter_journal_items(self, cr, uid, ids, move_id, decl_id, context=None):
		ac_mv_line_obj = self.pool.get('account.move.line')
		company_obj = self.pool.get('res.company')
		comp_id = company_obj._company_default_get(cr, uid, context=context)
		for field in ['reduced_rate', 'intermediate_rate', 'normal_rate', 'regul_exigible', 'immo', \
						'goods_services', 'regul_deductible', 'report_credit', 'vat']:
			# Saisie du taux réduit
			if field == 'reduced_rate':
				montant = self.browse(cr, uid, ids, context=context).vat_due_reduced_rate
				account = company_obj.browse(cr, uid, comp_id, context=context).tax_reduced_rate_ids and \
						company_obj.browse(cr, uid, comp_id, context=context).tax_reduced_rate_ids[0].account_collected_id.id or False
				if account and montant != 0:
					vals = {
						'declaration_id': decl_id.id,
						'move_id': move_id,
						'account_id': company_obj.browse(cr, uid, comp_id, context=context).tax_reduced_rate_ids[0].account_collected_id.id,
						'debit': montant > 0 and montant or 0.0,
						'credit': montant < 0 and -montant or 0.0,
						'name': decl_id.name
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
			# Saisie du taux intermédiaire
			elif field == 'intermediate_rate':
				montant = self.browse(cr, uid, ids, context=context).vat_due_intermediate_rate
				account = company_obj.browse(cr, uid, comp_id, context=context).tax_intermediate_rate_ids and \
						company_obj.browse(cr, uid, comp_id, context=context).tax_intermediate_rate_ids[0].account_collected_id.id or False
				if account and montant != 0:
					vals = {
						'declaration_id': decl_id.id,
						'move_id': move_id,
						'account_id': company_obj.browse(cr, uid, comp_id, context=context).tax_intermediate_rate_ids[0].account_collected_id.id,
						'debit': montant > 0 and montant or 0.0,
						'credit': montant < 0 and -montant or 0.0,
						'name': decl_id.name
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
			# Saisie du taux normal
			elif field == 'normal_rate':
				montant = self.browse(cr, uid, ids, context=context).vat_due_normal_rate
				account = company_obj.browse(cr, uid, comp_id, context=context).tax_normal_rate_ids and \
						company_obj.browse(cr, uid, comp_id, context=context).tax_normal_rate_ids[0].account_collected_id.id or False
				if account and montant != 0:
					vals = {
						'declaration_id': decl_id.id,
						'move_id': move_id,
						'account_id': company_obj.browse(cr, uid, comp_id, context=context).tax_normal_rate_ids[0].account_collected_id.id,
						'debit': montant > 0 and montant or 0.0,
						'credit': montant < 0 and -montant or 0.0,
						'name': decl_id.name
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
			# Saisie de la régularisation de la TVA à reverser
			elif field == 'regul_exigible':
				montant = self.browse(cr, uid, ids, context=context).vat_due_regularization_to_donate
				account = self.browse(cr, uid, ids, context=context) and \
						self.browse(cr, uid, ids, context=context).account_regul_due.id or False
				if account and montant != 0:
					vals = {
						'declaration_id': decl_id.id,
						'move_id': move_id,
						'account_id': self.browse(cr, uid, ids, context=context).account_regul_due.id,
						'debit': montant > 0 and montant or 0.0,
						'credit': montant < 0 and -montant or 0.0,
						'name': decl_id.name
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
			# Saisie de l'immobilisation
			elif field == 'immo':
				montant = self.browse(cr, uid, ids, context=context).vat_immobilization
				account = company_obj.browse(cr, uid, comp_id, context=context).tax_immo_ids and \
						company_obj.browse(cr, uid, comp_id, context=context).tax_immo_ids[0].account_collected_id.id or False
				if account and montant != 0:
					vals = {
						'declaration_id': decl_id.id,
						'move_id': move_id,
						'account_id': company_obj.browse(cr, uid, comp_id, context=context).tax_immo_ids[0].account_collected_id.id,
						'credit': montant > 0 and montant or 0.0,
						'debit': montant < 0 and -montant or 0.0,
						'name': decl_id.name
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
			# Saisie des autres biens et services
			elif field == 'goods_services':
				montant = self.browse(cr, uid, ids, context=context).vat_other_goods_services
				account = company_obj.browse(cr, uid, comp_id, context=context).tax_others_goods_services_ids and \
						company_obj.browse(cr, uid, comp_id, context=context).tax_others_goods_services_ids[0].account_collected_id.id or False
				if account and montant != 0:
					vals = {
						'declaration_id': decl_id.id,
						'move_id': move_id,
						'account_id': company_obj.browse(cr, uid, comp_id, context=context).tax_others_goods_services_ids[0].account_collected_id.id,
						'credit': montant > 0 and montant or 0.0,
						'debit': montant < 0 and -montant or 0.0,
						'name': decl_id.name
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
			# Saisie de la régularisation de la TVA à déduire
			elif field == 'regul_deductible':
				montant = self.browse(cr, uid, ids, context=context).vat_regularization
				account = self.browse(cr, uid, ids, context=context) and \
						self.browse(cr, uid, ids, context=context).account_regul_deduc.id or False
				if account and montant != 0:
					vals = {
						'declaration_id': decl_id.id,
						'move_id': move_id,
						'account_id': self.browse(cr, uid, ids, context=context).account_regul_deduc.id,
						'credit': montant > 0 and montant or 0.0,
						'debit': montant < 0 and -montant or 0.0,
						'name': decl_id.name
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
			# Saisie du report de crédit
			elif field == 'report_credit':
				montant = self.browse(cr, uid, ids, context=context).defferal_credit
				account = company_obj.browse(cr, uid, comp_id, context=context).credit_id and \
						company_obj.browse(cr, uid, comp_id, context=context).credit_id.id or False
				if not account:
					raise Warning('You cannot create journal items. Missing account credit report. Check your configuration.')
				if account and montant != 0:
					vals = {
						'declaration_id': decl_id.id,
						'move_id': move_id,
						'account_id': company_obj.browse(cr, uid, comp_id, context=context).credit_id.id,
						'credit': montant > 0 and montant or 0.0,
						'debit': montant < 0 and -montant or 0.0,
						'name': decl_id.name
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
			# Saisie du crédit de TVA en DEBIT
			# Saisie de la TVA en CREDIT
			elif field == 'vat':
				difference = abs(decl_id.total_vat_payable) - abs(decl_id.total_vat_deductible)
				account_vat = company_obj.browse(cr, uid, comp_id, context=context).vat_id and \
							company_obj.browse(cr, uid, comp_id, context=context).vat_id.id or False
				account_credit = company_obj.browse(cr, uid, comp_id, context=context).credit_id and \
							company_obj.browse(cr, uid, comp_id, context=context).credit_id.id or False
				if not account_vat or not account_credit:
					raise Warning('You cannot create journal items. Missing account credit report or vat. Check your configuration.')
				# TVA
				if difference > 0 and account_vat:
					vals = {
						'declaration_id': decl_id.id,
						'move_id': move_id,
						'account_id': company_obj.browse(cr, uid, comp_id, context=context).vat_id.id,
						'credit': decl_id.net_vat_due,
						'debit': 0.0,
						'name': decl_id.name
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
				# Crédit de TVA
				elif difference < 0 and account_credit:
					vals = {
						'declaration_id': decl_id.id,
						'move_id': move_id,
						'account_id': company_obj.browse(cr, uid, comp_id, context=context).credit_id.id,
						'debit': decl_id.type_simplified == 'annual' and decl_id.surplus or decl_id.vat_credit,
						'credit': 0.0,
						'name': decl_id.name
					}
					ac_mv_line_obj.create(cr, uid, vals, context=context, check=False)
		return True

	def generate_journal_items(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		declaration = self.pool.get('l10n.pf.account.vat.declaration')
		dec_id = context.get('active_id', False)
		declaration_line = declaration.browse(cr, uid, dec_id, context=context)
		am_obj = self.pool.get('account.move')
		aml_obj = self.pool.get('account.move.line')

		# Create the move
		move_name = declaration_line.name
		move_vals = self._prepare_move(cr, uid, declaration_line, move_name, context=context)
		move_id = am_obj.create(cr, uid, move_vals, context=context)
		
		self.enter_journal_items(cr, uid, ids, move_id, declaration_line, context=context)
		declaration_line.write({'journal_entry_id': move_id})
		return declaration_line.write({'state':'simulate'})
