# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

class l10n_pf_account_vat_fill(osv.osv_memory):
	_name = "l10n.pf.account.vat.fill"
	
	def _get_account(self, cr, uid, context=None):
		user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', user.company_id.id)], limit=1)
		return accounts and accounts[0] or False
	
	_columns = {
		'chart_account_id': fields.many2one('account.account', 'Chart of Account', required=True),
		'fiscalyear': fields.many2one('account.fiscalyear', 'Fiscal year'),
		'target_move': fields.selection([('posted', 'All Posted Entries'),('all','All Entries')], 'Target Moves', required=True),
		'period_from': fields.many2one('account.period', 'Start Period'),
		'period_to': fields.many2one('account.period', 'End Period'),
		'regime_vat': fields.selection([('deposit','Deposit in simplified regime'),('annual','Annual in simplified regime'),('real','Real regime')], 'Regime Vat'),
		'type_vat': fields.selection([('cashing','Cashing vat'),('bills','Bills vat')],'Type vat'),
		'exports_ids': fields.many2many('account.account', 'account_account_exports', 'exports_id', 'account_id', 'Exports accounts'),
		'others_ids': fields.many2many('account.account', 'account_account_others', 'others_id', 'account_id', 'Others accounts'),
		'reduced_rate_ids': fields.many2many('account.account', 'account_account_reduced', 'reduced_rate_id', 'account_id', 'Reduced rate accounts'),
		'intermediate_rate_ids': fields.many2many('account.account', 'account_account_intermediate', 'intermediate_rate_id', 'account_id', 'Intermediate rate accounts'),
		'normal_rate_ids': fields.many2many('account.account', 'account_account_normal', 'normal_rate_id', 'account_id', 'Normal rate accounts'),
		'immo_ids': fields.many2many('account.account', 'account_account_immo', 'immo_id', 'account_id', 'Immo accounts'),
		'others_goods_services_ids': fields.many2many('account.account', 'account_account_goods_services', 'others_goods_services_id', 'account_id', 'Others goods and services accounts'),
		'customers_ids': fields.many2many('account.account', 'account_account_customers', 'customers_id', 'account_id', 'Customers accounts'),
		'turnover_ids': fields.many2many('account.account', 'account_account_turnover', 'turnover_id', 'account_id', 'Turnover accounts'),
	}
	
	_defaults = {
		'chart_account_id': _get_account,
	}
	
	def default_get(self, cr, uid, fields, context=None):
		import pdb
		pdb.set_trace()
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
		if 'fiscalyear' in fields:
			res.update({'fiscalyear': declaration.fiscalyear.id})
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
	
	#def _build_contexts(self, cr, uid, ids, data, context=None):
		#if context is None:
			#context = {}
		#result = {}
		#result['fiscalyear'] = 'fiscalyear' in data['form'] and	data['form']['fiscalyear'] or False
		#result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
		#return result
		
	#def fill_declaration(self, cr, uid, ids, context=None):
		#import pdb
		#pdb.set_trace()
		#if context is None:
			#context = {}
		#data = {}
		#data['ids'] = context.get('active_ids', [])
		#data['model'] = context.get('active_model', 'ir.ui.menu')
		#data['form'] = self.read(cr, uid, ids, ['chart_account_id', 'fiscalyear', 'target_move', 'period_from', 'period_to', 'regime_vat', 'type_vat', 'exports_ids', 'others_ids', 'reduced_rate_ids', 'intermediate_rate_ids', 'normal_rate_ids', 'immo_ids', 'other_goods_services_ids', 'customers_ids', 'turnover_ids'])
		#for field in ['fiscalyear', 'chart_account_id', 'period_from', 'period_to']:
			#if isinstance(data['form'][field], tuple):
				#data['form'][field] = data['form'][field][0]
		#used_context = self._build_contexts(cr, uid, ids, data, context=context)
		#data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
		#data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
