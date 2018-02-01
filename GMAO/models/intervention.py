# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class InterventionState(models.Model):
    _name = 'intervention.state'
    _description = "Etat de l'intervention"
    _order = 'sequence'

    def _get_default_intervention_ids(self):
        project_id = self.env['intervention']._get_default_intervention_id()
        if project_id:
            return [project_id]
        return None

    name = fields.Char('Etat', required=True, translate=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=1)
    case_default = fields.Boolean('Default for New Projects',
        help="Si vous cochez ce champ, cette étape sera proposée par défaut sur chaque nouveau projet."
             "Il n'attribuera pas cette étape aux projets existants.")
    project_ids = fields.Many2many('intervention',
                                   'intervention_state_rel',
                                   'state_id',
                                   'intervention_id',
                                   'Interventions',
                                   default=_get_default_intervention_ids)
    fold = fields.Boolean('Plié dans la vue Kanban',
                               help='Cette étape est repliée dans la vue kanban lorsque '
                               "il n'y a pas d'enregistrements à cet etat pour afficher .")



class Intervention(models.Model):
    _name = "intervention"
    _description = "Interventions"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def stage_groups(self, present_ids, domain, **kwargs):
        states_obj = self.env['intervention.state'].search([])
        unfold_states = [inter.state.id for inter in self.search([('state', '!=', False)])]
        states = states_obj.name_get()
        folded = {state.id: True for state in states_obj if state.id not in unfold_states}
        return states, folded

    _group_by_full = {'state': stage_groups, }

    def _get_default_state_id(self):
        """ Gives default state """
        project_id = self._get_default_intervention_id()
        return self.state_find([('fold', '=', False)])

    def state_find(self, domain=[], order='sequence asc'):
        # perform search, return the first found
        state = self.env['intervention.state'].search(domain, order=order, limit=1)
        if state:
            return state.id
        return False

    def _get_default_intervention_id(self):
        return self._resolve_intervention_id_from_context() or False

    def _resolve_intervention_id_from_context(self):
        context = self._context.copy()
        if type(context.get('default_intervention_id')) in (int, long):
            return context['default_intervention_id']
        if isinstance(context.get('default_intervention_id'), basestring):
            intervention_name = context['default_intervention_id']
            intervention_ids = self.env['project.project'].name_search(name=intervention_name)
            if len(intervention_ids) == 1:
                return intervention_ids[0][0]
        return None

    @api.multi
    def unlink(self):
        for record in self:
            if record.state.sequence == record.state.search([], order='sequence desc', limit=1).sequence:
                raise Warning(_(u"Vous ne pouvez pas supprimer un enregistrement dans l'état %s" % record.state.name))
        return super(Intervention, record).unlink()

    @api.one
    def cloturer(self):
        state = self.state.search([], order='sequence desc', limit=1)
        if state:
            self.state = state.id
            self.state_end = True

    @api.model
    def create(self, values):
        if values.get('name', '/') == '/':
            values['name'] = self.env['ir.sequence'].get('cmms.intervention')
        rec = super(Intervention, self).create(values)
        rec.equipment_id.compute_intervention_count()
        return rec
    

    @api.multi
    def create_corrective(self):
        self.type = "maintenance"
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'corrective',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {'default_intervention_id': self.id,
                        'default_equipment_id': self.equipment_id.id,
                        'default_responsable': self.intervenant.id}

        }

    @api.multi
    def group_by_state(self):
        return {
            'view_mode': 'list',
            'res_model': 'intervention',
            'type': 'ir.actions.act_window',
            'domain': [('state', '=', self.state.id)]

        }


    @api.one
    @api.depends('date', 'date_end')
    def _compute_duration(self):
        if self.date_end and self.date:
            self.duration = (fields.Date.from_string(self.date_end) - fields.Date.from_string(self.date)).days

    name = fields.Char("Référence de l'intervention",readonly=True)
    #design_projet = fields.Many2one('projet', String='ID et désignation du Projet  ')
    equipment_id = fields.Many2one('machine', String='ID désignation groupe')
    #design_system = fields.Char(String='ID désignation système ')
    #design_sous_system = fields.Char(String='ID désignation sous-système ')
    state = fields.Many2one('intervention.state', u'Statut',
                             track_visibility='onchange',
                             select=True,
                             # required=True,
                             copy=False,
                            default=_get_default_state_id,
                            readonly=True)
    kanban_state = fields.Selection(
        [('normal', 'En cours '), ('blocked', u'Bloqué '), ('done', 'Prêt pour la prochaine étape ')], 'État du Kanban',
        track_visibility='onchange',
        help="L'état kanban d'une intervention indique des situations particulières qui l'affectent :\n"
             " * Normal est la situation par défaut\n"
             " * Bloqué indique que quelque chose empêche la progression de cette tâche\n"
             " * Prêt pour l'étape suivante indique que la tâche est prête à être tirée à l'étape suivante ",
        required=False, copy=False)

    type = fields.Selection([('diagnostic', 'Diagnostique'),
                             ('maintenance', 'Maintenance'),
                             ('done', 'Terminée')],
                             default='diagnostic',
                             index=True,
                            #readonly=True,
                             track_visibility='onchange',
                             copy=False)
    demandeur = fields.Many2one('client', String='Nom du demandeur')
    #equipement = fields.Char(String='Equipement ')
    date = fields.Date(String='Date de la Demande')
    classification = fields.Text(String="Classification de l'intervention (non-conformité d’équipement"
                                        " ou d’installation, remplacement dans le cadre de la garantie) ")
    motif = fields.Text(String="Motif de l'intervention")
    ##nature = fields.Text(String=" Nature des travaux à réaliser")
    delai = fields.Selection([(2, "Très urgent "), (1, "Urgent "), (0, 'Normal ')],
                             String='Délais pour intervention', default=0)

    date_end = fields.Date('Date de la Panne')
    duration = fields.Integer(compute="_compute_duration", string=u'Durée', store=True)

    responsable = fields.Many2one('res.users', 'Responsable', readonly=True, default=lambda self: self._uid)
    intervenant = fields.Many2one('technicien', 'intervenant')

    ##intervention_ids = fields.One2many('ligne.intervention', 'intervention_id', String='Materiels concernés')

    color = fields.Integer('Color Index', default=0)

    state_end = fields.Boolean()

    def copy(self, default=None):
        if default is None:
            default = {}
            default = default.copy()
            default['name'] = self.env['ir.sequence'].get('cmms.intervention')
        return super(Intervention, self).copy(default=default)


class LigneIntervention(models.Model):
    _name = "ligne.intervention"
    _description = "Materiels concernés"

    marque = fields.Char("Marque", size=64, required=True)
    sous_ensemble = fields.Char("Sous ensembles", size=64)
    ref = fields.Char('Référence')
    atelier = fields.Char('Atelier/Service ')
    temps = fields.Float("Temps alloué ")

    intervention_id = fields.Many2one('intervention', 'Reference to parent')
