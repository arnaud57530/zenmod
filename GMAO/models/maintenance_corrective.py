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
import datetime
import time
from openerp.tools.translate import  _
import logging
import math




class CorrectiveState(models.Model):
    _name = 'corrective.state'
    _description = "Etat de l'intervention"
    _order = 'sequence'

    def _get_default_intervention_ids(self):
        project_id = self.env['corrective']._get_default_corrective_id()
        if project_id:
            return [project_id]
        return None

    name = fields.Char('Etat', required=True, translate=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=1)
    case_default = fields.Boolean('Default for New Projects',
        help="Si vous cochez ce champ, cette étape sera proposée par défaut sur chaque nouvelle maintenance."
             "Il n'attribuera pas cette étape aux maintenances existants.")
    project_ids = fields.Many2many('corrective',
                                   'corrective_state_rel',
                                   'state_id',
                                   'corrective_id',
                                   'Maintenaces correctives',
                                   default=_get_default_intervention_ids)
    fold = fields.Boolean('Plié dans la vue Kanban',
                               help='Cette étape est repliée dans la vue kanban lorsque '
                               "il n'y a pas d'enregistrements à cet etat pour afficher .")


class Corrective(models.Model):
    _name = "corrective"
    _rec_name = "ref_mnt_corr"
    _description = "Corrective Maintenance System"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def stage_groups(self, present_ids, domain, **kwargs):
        states_obj = self.env['corrective.state'].search([])
        unfold_states = [inter.state.id for inter in self.search([('state', '!=', False)])]
        states = states_obj.name_get()
        folded = {state.id: True for state in states_obj if state.id not in unfold_states}
        return states, folded

    _group_by_full = {'state': stage_groups, }

    def _get_default_state_id(self):
        """ Gives default state """
        project_id = self._get_default_corrective_id()
        return self.state_find([('fold', '=', False)])

    def state_find(self, domain=[], order='sequence asc'):
        # perform search, return the first found
        state = self.env['corrective.state'].search(domain, order=order, limit=1)
        if state:
            return state.id
        return False

    def _get_default_corrective_id(self):
        return self._resolve_corrective_id_from_context() or False

    def _resolve_corrective_id_from_context(self):
        context = self._context.copy()
        if type(context.get('default_corrective_id')) in (int, long):
            return context['default_corrective_id']
        if isinstance(context.get('default_corrective_id'), basestring):
            corrective_name = context['default_corrective_id']
            corrective_ids = self.env['project.project'].name_search(name=corrective_name)
            if len(corrective_ids) == 1:
                return corrective_ids[0][0]
        return None

    @api.multi
    def creer_bon_travail(self):

        bon_obj = self.env['bon']

        bon_id = bon_obj.create(
            {'equipment_id': self.equipment_id.id,
             'ref': 'corrective,{}'.format(self.id),
             'responsable': [(4, self.responsable.ids)]
             })
        self.bon_id = bon_id.id
        return {
            'name': _('Bon de travail'),
            'type': 'ir.actions.act_window',
            'res_model': 'bon',
            'res_id': bon_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def _get_number_of_days(self, date_from, date_to):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        time_delta = to_dt - from_dt
        return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)



    @api.one
    def cloturer(self):
        state = self.state.search([], order='sequence desc', limit=1)
        
        if state:
            self.state = state.id
            self.state_end = True
            self.update_equipment()

            # Clôturer la demande d'intrvention et le bon de travail
            self.intervention_id.cloturer()
            self.bon_id.action_done()


    @api.multi
    def unlink(self):
        for record in self:
            if record.state.sequence == record.state.search([], order='sequence desc', limit=1).sequence:
                raise Warning(_(u"Vous ne pouvez pas supprimer un enregistrement dans l'état %s" % record.state.name))
        return super(Corrective, record).unlink()

    @api.onchange('ref')
    def _onchange_ref(self):
        logging.warning(str(self.ref))
        self._set_equipment_id()

    @api.one
    def _get_equipment_id(self):
        self._set_equipment_id()

    ref_mnt_corr = fields.Char("Référence maintenance corrective", default='/',readonly=True)
    equipment_id = fields.Many2one('machine', 'Machine', required=True)
    panne = fields.Many2one('cause_panne', 'Panne?')
    date_from = fields.Date('Date Debut', )
    date_to = fields.Date('Date Cloture',)
    arret = fields.Boolean(string=u"machine à l'arrêt")
    number_of_days = fields.Float(string=u"Nombre de jour")
    note = fields.Text('Notes')
    responsable = fields.Many2many('technicien', string='Technicien')
    details_cause_panne = fields.One2many('cause_panne', 'type_id')
    color = fields.Integer('Color Index', default=0)
    state = fields.Many2one('corrective.state',
                             default=_get_default_state_id,
                             select=True,
                             track_visibility='onchange',
                             copy=False)
    kanban_state = fields.Selection(
        [('normal', 'En cours '), ('blocked', u'Bloqué '), ('done', 'Prêt pour la prochaine étape ')], 'État du Kanban',
        track_visibility='onchange',
        help="L'état kanban d'une maintenance corrective indique des situations particulières qui l'affectent :\n"
             " * Normal est la situation par défaut\n"
             " * Bloqué indique que quelque chose empêche la progression de cette maintenance\n"
             " * Prêt pour l'étape suivante indique que la maintenance corrective est prête à être tirée à l'étape suivante ",
        required=False, copy=False)
    intervention_id = fields.Many2one('intervention', 'Intervention')
    bon_id = fields.Many2one('bon', 'Bon de travail')
    state_end = fields.Boolean()

    @api.onchange('date_from','date_to') 
    def _check_change(self):
        res = 0
        if self.date_from :
            if self.date_to :
                date_from = datetime.datetime.strptime(self.date_from, "%Y-%m-%d")
                date_to = datetime.datetime.strptime(self.date_to, "%Y-%m-%d")
                delta = date_to - date_from
                res = delta.days
                self.number_of_days = res
                a = self.env['machine'].search([('id', '=', self.equipment_id.id)])
                print "argarg", a
                self.env['machine'].write(a)
                #machine_obj = self.env['machine']
                #self.env.add_todo(machine_obj._fields['days_of_overtime'], machine_obj.search([('id', '=', self.equipment_id.id)]))
                #machine_obj.recompute()
        
    @api.one
    @api.multi
    def update_equipment(self):
        if self.equipment_id.date_gar > fields.Date.today():
            self.equipment_id.days_of_overtime += self.number_of_days
            self.intervention_id.cloturer()
            self.intervention_id.corrective_ref = self.ref_mnt_corr
        return True

    @api.model
    def create(self, values):
        if ('ref_mnt_corr' not in values) or (values.get('ref_mnt_corr') == '/'):
            values['ref_mnt_corr'] = self.env['ir.sequence'].get('cmms.cm')
        
        rec = super(Corrective, self).create(values)
        rec.equipment_id.compute_days_of_overtime()
        rec.equipment_id.compute_cm_count()
        return rec
    
    @api.multi   
    def write(self, vals):
        print "write values : ", vals
        rec = super(Corrective, self).write(vals)
        self.equipment_id.compute_days_of_overtime()
        rec.equipment_id.compute_cm_count()
        return rec    
    

    def copy(self, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = self.env['ir.sequence'].get('cmms.cm')
        return super(Corrective, self).copy(default=default)
