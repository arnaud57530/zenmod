# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import  _
from dateutil.relativedelta import relativedelta
import datetime
import time
from lxml import etree
import logging


class PreventiveState(models.Model):
    _name = 'preventive.state'
    _description = "Etat de l'intervention"
    _order = 'sequence'

    def _get_default_intervention_ids(self):
        project_id = self.env['preventive']._get_default_preventive_id()
        if project_id:
            return [project_id]
        return None

    name = fields.Char('Etat', required=True, translate=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=1)
    case_default = fields.Boolean('Default for New Projects',
        help="Si vous cochez ce champ, cette étape sera proposée par défaut sur chaque nouvelle maintenance."
             "Il n'attribuera pas cette étape aux maintenances existants.")
    project_ids = fields.Many2many('preventive',
                                   'preventive_state_rel',
                                   'state_id',
                                   'preventive_id',
                                   'Maintenaces preventives',
                                   default=_get_default_intervention_ids)
    fold = fields.Boolean('Plié dans la vue Kanban',
                               help='Cette étape est repliée dans la vue kanban lorsque '
                               "il n'y a pas d'enregistrements à cet etat pour afficher .")

    
class Preventive(models.Model):
    _name = "preventive"
    _description = "Preventive Maintenance System"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def stage_groups(self, present_ids, domain, **kwargs):
        states_obj = self.env['preventive.state'].search([])
        unfold_states = [inter.state.id for inter in self.search([('state', '!=', False)])]
        states = states_obj.name_get()
        folded = {state.id: True for state in states_obj if state.id not in unfold_states}
        return states, folded

    _group_by_full = {'state': stage_groups, }

    @api.one
    @api.depends('meter', 'days_interval', 'days_last_done')
    def _days_next_due(self):
        if self.meter == "mois" and self.days_interval and self.days_last_done:
            interval = relativedelta(days=self.days_interval)
            last_done = fields.Date.from_string(self.days_last_done)
            next_due = last_done + interval
            self.days_next_due = next_due.strftime(DEFAULT_SERVER_DATE_FORMAT)

    # @api.one
    # @api.depends('meter', 'days_interval', 'days_last_done')
    # def _days_due(self):
    #     if self.meter == "mois":
    #         interval = datetime.timedelta(days=self.days_interval)
    #         last_done = fields.Datetime.from_string(self.days_last_done)
    #         next_due = last_done + interval
    #         now = datetime.datetime.now()
    #         due_days = next_due - now
    #         self.days_left = due_days.days

    @api.one
    @api.depends('days_next_due', 'days_last_done')
    def _days_due(self):
        if self.days_next_due and self.days_last_done:
            last_done = fields.Date.from_string(self.days_last_done)
            next_due = fields.Date.from_string(self.days_next_due)
            self.days_left = (next_due - last_done).days

    @api.one
    @api.depends('meter', 'days_left', 'days_warn_period')
    def _get_state(self):
        if self.meter == u'days':
            if self.days_left <= 0:
                state = u'Dépassé'
            elif self.days_left <= self.days_warn_period:
                state = u'Approché'
            else:
                state = u'OK'
            self.state = state

    @api.one
    @api.depends('hours_interval', 'rate_of_use')
    def _compute_days_interval(self):
        if self.rate_of_use:
            self.days_interval = self.hours_interval / self.rate_of_use

    @api.multi
    def pm_end(self):
        return {
            'name': _('Clôture'),
            'type': 'ir.actions.act_window',
            'res_model': 'pm.close.wizard',
            'view_mode': 'form',
            'context': {'default_user_id': self.equipment_id.nom_instal.id,
                        'default_pm_id': self.id,
                        'default_date': self.days_next_due or fields.Date.now()
                        },
            'target': 'new'
        }

    @api.multi
    def creer_bon_travail(self):
        return {
            'name': _('Bon de travail'),
            'type': 'ir.actions.act_window',
            'res_model': 'bon',
            'view_mode': 'form',
            'context': {'default_equipment_id': self.equipment_id.id,
                        'default_ref': 'preventive,{}'.format(self.id)
                        },
            'target': 'current'
        }

    @api.one
    def cloturer(self):
        state = self.state.search([], order='sequence desc', limit=1)
        if state:
            self.state = state.id
            self.state_end = True

    @api.one
    @api.depends('seq', 'hours_interval')
    def _compute_hour_interval(self):
        self.hour_interval = self.seq * self.hours_interval


    
    @api.multi   
    def write(self, vals):
        print "write values : ", vals
        rec = super(Preventive, self).write(vals)
        if not(rec):
            rec.equipment_id.compute_pm_count()
        return rec    

    @api.model
    def create(self, values):
        if ('name' not in values) or (values.get('name') == '/'):
            values['name'] = self.env['ir.sequence'].get('cmms.pm')
        rec = super(Preventive, self).create(values)
        rec.equipment_id.compute_pm_count()
        return rec
    
    @api.multi
    def unlink(self):
        for record in self:
            if record.state.sequence == record.state.search([], order='sequence desc', limit=1).sequence:
                raise Warning(_(u"Vous ne pouvez pas supprimer un enregistrement dans l'état %s" % record.state.name))
        
        rec = super(Preventive, record).unlink()
        return rec
    
        
    def _get_default_state_id(self):
        """ Gives default state """
        # project_id = self._get_default_preventive_id()
        return self.state_find([('fold', '=', False)])

    def state_find(self, domain=[], order='sequence asc'):
        # perform search, return the first found
        state = self.env['preventive.state'].search(domain, order=order, limit=1)
        if state:
            return state.id
        return False

    def _get_default_preventive_id(self):
        return self._resolve_preventive_id_from_context() or False

    def _resolve_preventive_id_from_context(self):
        context = self._context.copy()
        if type(context.get('default_preventive_id')) in (int, long):
            return context['default_preventive_id']
        if isinstance(context.get('default_preventive_id'), basestring):
            preventive_name = context['default_preventive_id']
            preventive_ids = self.env['project.project'].name_search(name=preventive_name)
            if len(preventive_ids) == 1:
                return preventive_ids[0][0]
        return None

    @api.onchange('equipment_id')
    def change_days_last_done(self):
        if self.equipment_id.date_ser:
            self.days_last_done = self.equipment_id.date_ser

    name = fields.Char('Ref PM', size=20, required=True, default=lambda *a: '/', readonly=True)
    equipment_id = fields.Many2one('machine', 'Machine', required=True)
    meter = fields.Selection([('jour', 'jour'), ('mois', 'mois')],
                             u'Unité de mesure',
                             default='mois')
    recurrent = fields.Boolean(u'Récurrent ?', help=u"Marquer cette option si MP est périodique", default=True)
    hours_interval = fields.Integer(string="Nombre d'heures")
    rate_of_use = fields.Integer(string="La cadence")
    days_interval = fields.Integer('Intervalle', compute=_compute_days_interval)
    days_last_done = fields.Date('Commencé le') #  , required=True, default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    days_next_due = fields.Date(compute=_days_next_due, string='Prochaine date')
    days_warn_period = fields.Integer(u'Date d\'alerte')
    user_id = fields.Many2one('technicien', 'Technicien')
    days_left = fields.Integer(compute=_days_due, string='Jours restants')
    # state = fields.Char(compute=_get_state, string=u'État')
    classification = fields.Text(String=u"Classification de l'intervention (non-conformité d’équipement"
                                        u"ou d’installation, remplacement dans le cadre de la garantie) ")
    color = fields.Integer('Color Index', default=0)
    state = fields.Many2one('preventive.state',
                            default=_get_default_state_id,
                            select=True,
                            track_visibility='onchange',
                            copy=False)
    kanban_state = fields.Selection(
        [('normal', 'En cours '), ('blocked', u'Bloqué '), ('done', 'Prêt pour la prochaine étape ')], 'État du Kanban',
        track_visibility='onchange',
        help="L'état kanban d'une maintenance preventive indique des situations particulières qui l'affectent :\n"
             " * Normal est la situation par défaut\n"
             " * Bloqué indique que quelque chose empêche la progression de cette maintenance\n"
             " * Prêt pour l'étape suivante indique que la maintenance preventive est prête à être tirée à l'étape suivante ",
        required=False, copy=False)
    intervention_id = fields.Many2one('intervention', 'Intervention')
    state_end = fields.Boolean()

    seq = fields.Integer(string="Séquence")
    hour_interval = fields.Integer('Nombre d\'heures', compute=_compute_hour_interval)

    def copy(self, default=None):
        if default is None:
            default = {}
            default = default.copy()
            default['name'] = self.env['ir.sequence'].get('cmms.pm')
        return super(Preventive, self).copy(default=default)


class PmCloseWizard(models.Model):
    _name = 'pm.close.wizard'

    date = fields.Date()
    user_id = fields.Many2one('technicien', 'Technicien')
    pm_id = fields.Many2one('preventive', 'pm ref')

    @api.multi
    def proceed(self):
        self.pm_id.cloturer()
        self.pm_id.days_next_due = self.date
        pm = self.env['preventive'].search([('equipment_id', '=', self.pm_id.equipment_id.id),
                                            ('id', '=', self.pm_id.id + 1)],
                                           limit=1)
        if pm and self.date:
            pm.days_last_done = self.date

        return {
            'name': _('Machine'),
            'type': 'ir.actions.act_window',
            'res_model': 'machine',
            'res_id': self.pm_id.equipment_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('GMAO.view_machine_form').id,
            'target': 'current'
        }
