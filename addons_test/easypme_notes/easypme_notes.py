# -*- coding: utf-8
from openerp.osv import fields, osv

class easypme_notes(osv.osv):
	_inherit = "project.project"
	_columns = {
		'notes': fields.text('Notes')
	}
	
easypme_notes()
