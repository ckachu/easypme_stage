# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class res_company(osv.osv):
	_inherit = "res.company"
	_columns = {
		'bp': fields.char('BP'),
		'city_zip': fields.char('City Zip'),	
		'activity': fields.char('Company activity'),
		'regime_vat': fields.selection([('deposit','Deposit in simplified regime'),('annual','Annual in simplified regime'),('real','Real regime')], 'Regime Vat'),
		'type_vat': fields.selection([('cashing','Cashing vat'),('bills','Bills vat')],'Type vat'),
	}

	#def on_change_company_regime(self, cr, uid, ids, regime_vat, context=None):
	#	values = {}
	#	if regime_vat == 'deposit':
	#		regime = self.pool.get('res.company').browse(cr, uid, regime_vat, context=context)
	#		values = {
	#			'type_vat': None
	#		}
	#	return {'value':values}
