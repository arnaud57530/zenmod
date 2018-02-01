# -*- coding: utf-8 -*-
###############################################################################
#
#
###############################################################################

from openerp import models, fields, api
import datetime
from dateutil.relativedelta import *
import time
import logging

AVAILABLE_PRIORITIES = [
    ('3', 'Normal'),
    ('2', 'Bas'),
    ('1', 'Elevé')
]


class RequestLink(models.Model):
    _name = 'gmao.request.link'
    _order = 'priority'

    name = fields.Char('Nom', required=True, translate=True)
    object = fields.Char('Objet', size=64, required=True)
    priority = fields.Integer('Priorité', default=5)


class Bon(models.Model):
    _name = "bon"
    _description = "Bon de travail"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def create(self, vals):
        if ('name' not in vals) or (vals.get('name') == '/'):
            vals['name'] = self.env['ir.sequence'].get('cmms.incident')
        rec  = super(Bon, self).create(vals)
        rec.equipment_id.compute_order_count()
        return rec

    def _links_get(self):
        obj = self.env['gmao.request.link']
        objects = obj.search([])
        return [(r['object'], r['name']) for r in objects]

    @api.multi
    def action_done(self):
        self.state = 'done'
        return True

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
        return True

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        return True

    def _set_equipment_id(self):
        if self.ref and self.ref.equipment_id:
            self.equipment_id = self.ref.equipment_id.id

    @api.onchange('ref')
    def _onchange_ref(self):
        logging.warning(str(self.ref))
        self._set_equipment_id()

    @api.one
    def _get_equipment_id(self):
        self._set_equipment_id()

    name = fields.Char('Référence du bon de travail', size=64, default='/', readonly=True)
    state = fields.Selection([('draft', u'En cours'), ('done', u'Validé'), ('cancel', u'Annulé')],
                             u'Statut',
                             required=True,
                             default='draft')
    priority = fields.Selection(AVAILABLE_PRIORITIES, 'Priorité', default=lambda *a: AVAILABLE_PRIORITIES[2][0])
    user_id = fields.Many2one('res.users', 'Manager', readonly=True, default=lambda self: self._uid)
    date = fields.Datetime('Date de la commande', default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    active = fields.Boolean('Active?', default=True)
    ref = fields.Reference(_links_get, 'Source d\'ordre de travail', required=True)
    equipment_id = fields.Many2one('machine', compute=_get_equipment_id, string='Machine', required=True, readonly=True)
    responsable = fields.Many2many('technicien', string='Technicien')

    piece_ids = fields.One2many('pieces', 'bon_id')



    def copy(self, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = self.env['ir.sequence'].get('cmms.incident')
        return super(Bon, self).copy(default=default)






