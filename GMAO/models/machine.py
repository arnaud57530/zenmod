# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
import openerp.addons.decimal_precision as dp
import os
import datetime
from dateutil.relativedelta import *
import time
from lxml import etree


class Machine(models.Model):
    _name = 'machine'

    @api.model
    def create(self, values):
        values['number'] = self.env['ir.sequence'].get('cmms.pm')
        pm_values = self._get_pm_values(values['date_ser'], values['type'])
        if pm_values:
            values['pm_ids'] = pm_values
        return super(Machine, self).create(values)

    @api.one
    def _count_all(self):
        print "test arg"
        intervention_obj = self.env['intervention']
        pm_obj = self.env['preventive']
        cm_obj = self.env['corrective']
        order_obj = self.env['bon']
        cm_ids = cm_obj.search([('equipment_id', '=', self.id)])
        self.pm_count = pm_obj.search_count([('equipment_id', '=', self.id)])
        self.cm_count = cm_obj.search_count([('equipment_id', '=', self.id)])
        self.order_count = order_obj.search_count([('equipment_id', '=', self.id)])
        self.intervention_count = intervention_obj.search_count([('equipment_id', '=', self.id)])
        
        
    
    @api.one    
    def compute_pm_count(self):
        pm_obj = self.env['preventive']
        self.pm_count = pm_obj.search_count([('equipment_id', '=', self.id)])
    
    @api.one    
    def compute_cm_count(self):
        cm_obj = self.env['corrective']
        self.cm_count = cm_obj.search_count([('equipment_id', '=', self.id)])
        
    @api.one    
    def compute_order_count(self):
        order_obj = self.env['bon']
        self.order_count = order_obj.search_count([('equipment_id', '=', self.id)])
    
    
    @api.one    
    def compute_intervention_count(self):
        intervention_obj = self.env['intervention']
        self.intervention_count = intervention_obj.search_count([('equipment_id', '=', self.id)])
            
        


    @api.one    
    def compute_days_of_overtime(self):
        cm_obj = self.env['corrective']
        cm_ids = cm_obj.search([('equipment_id', '=', self.id)])
        res = 0
        for record in cm_ids:
            res = res + record.number_of_days 
        self.days_of_overtime = res


        
    @api.multi
    def write(self, values):
        res = super(Machine, self).write(values)
        pms = list(self.env['preventive'].search([('equipment_id', '=', self.id), ('state_end', '=', False)], order="id asc"))
        for index in range(1, len(pms)):
            if pms[index-1].days_next_due:
                pms[index].days_last_done = pms[index-1].days_next_due
            pms[index].rate_of_use = pms[index-1].rate_of_use
        return res

    @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current machine """
        context = self._context.copy()
        if context.get('xml_id'):
            res = self.pool['ir.actions.act_window'].for_xml_id(self._cr, self._uid, 'GMAO', context['xml_id'])
            res['context'] = context
            res['context'].update({'default_equipment_id': self.id})
            res['domain'] = [('equipment_id', '=', self.id)]
            return res
        return False

    @api.one
    @api.depends('meter', 'date_ser', 'deadlinegar_2')
    def _days_next_due(self):
        if self.meter == "mois" and self.deadlinegar_2:
            # s'il n'y a pas d'intervalle on ne calcule pas la date de fin de garantie
            interval = relativedelta(months=self.deadlinegar_2)
            last_done = fields.Date.from_string(self.date_ser)
            next_due = last_done + interval
            self.date_gar = next_due.strftime(DEFAULT_SERVER_DATE_FORMAT)

    @api.one
    @api.depends('date_gar', 'days_of_overtime')
    def _compute_overtime(self):
        if self.days_of_overtime:
            interval = datetime.timedelta(days=self.days_of_overtime)
            last_done = fields.Date.from_string(self.date_gar)
            next_due = last_done + interval
            self.date_of_extension = next_due.strftime(DEFAULT_SERVER_DATE_FORMAT)

    @api.one
    @api.depends('num_serie_un', 'puissance', 'projet.name')
    def _compute_name(self):
        self.name = '/'.join([self.projet.name or '',self.site.abri or '',str(self.puissance),(self.num_serie_un or '')[7:14]])


    def _get_pm_values(self, date_ser, type_id):
        # days_last_done = fields.Date.from_string(date_ser)
        type = self.env['type'].browse(type_id)
        if type.heure and type.heures:
            return [(0, 0, {'name': '/',
                            'equipment_id': self.id,
                            'hours_interval': type.heure,
                            'days_last_done': date_ser
                            })] + [
                    (0, 0, {'name': '/',
                            'equipment_id': self.id,
                            'hours_interval': type.heure,
                            }) for index in range(2, (type.heures/type.heure)+1)
            ]
        else:
            return []

    @api.one
    @api.depends('date_gar')
    def _compute_state(self):
        date = datetime.datetime.strptime(self.date_gar, DEFAULT_SERVER_DATE_FORMAT) - datetime.datetime.now()
        if date.days > self.days_alert:
            self.state = 1
        elif 0 < date.days <= self.days_alert:
            self.state = 2
        else:
            self.state = 3


    # @api.onchange('date_ser')
    # def _update_pm_ids(self):
    #     days_last_done = fields.Date.from_string(self.date_ser)

    #     for line in self.pm_ids:
    #         line.date_last_due = days_last_done.strftime(DEFAULT_SERVER_DATE_FORMAT)
    #         days_last_done += timedelta(2000)

    name = fields.Char(string='Nom de la Machine', compute=_compute_name, track_visibility='always',store=False)
    number = fields.Char()
    photo = fields.Binary('Photo')
    active = fields.Boolean('Active',default=True)
    date_liv = fields.Date(string='Date de Livraison', required=True)
    date_ser = fields.Date(string="date de mise en service", required=True)
    deadlinegar_2 = fields.Integer('Garantie /mois',
                                   help='Cette case et pour les calculers de la grantie de la machine en mois ',
                                   required=True)
    meter = fields.Selection([('jour', 'jour'),
                              ('mois', 'Mois'),
                              ('annee', 'Années')],
                             string=u'Unité de Mesure',
                             default='mois')
    date_gar = fields.Date(compute=_days_next_due, string="date fin de garantie")
    days_of_overtime = fields.Integer(string='Jours de prolongation')
    date_of_extension = fields.Date(compute=_compute_overtime, string='Date de prolongation')
    type = fields.Many2one('type',required=True,)
    const = fields.Char(related='type.const', store=False,readonly='True',)
    num_serie_un = fields.Char(string="N° de Série  groupe")
    num_serie_deux = fields.Char(string="N° de série du moteur ")
    num_serie_trois = fields.Char(string="N° de série de l'altérnateur")
    puissance = fields.Integer(string="Puissance/Kw", required=True)
    nom_instal = fields.Many2one('technicien', string="Respensble Projet")
    etat = fields.Selection([('marche', 'Marche'), ('arreter', 'Arreter')], string="Etat de produit")
    client = fields.Many2one('client', required=True, string='Client')
    projet = fields.Many2one('projet', 'Projet', required=True)
    site = fields.Many2one(related='projet.site', store=True)
    local = fields.Selection(related='projet.local', store=True)
    information = fields.Html(string='Information')

    cm_ids = fields.One2many('corrective', 'equipment_id', 'Maintenance Corrective ')
    pm_ids = fields.One2many('preventive', 'equipment_id', 'Maintenance Preventive')

    intervention_count = fields.Integer(string='Intervention')
    pm_count = fields.Integer(string='Maintenance preventive ')
    cm_count = fields.Integer(string='Maintenance corrective')
    order_count = fields.Integer(string='Ordre de travail')
    
    state = fields.Selection(selection=[(1, "Avec garantie"),
                                        (2, 'Fin de Garantie'),
                                        (3, 'Sans Garantie')],
                             compute=_compute_state,
                             index=True,
                             # readonly=True,
                             track_visibility='onchange',
                             copy=False,
                             string='Etat de la garantie',
                             # store=True
                             )
    sent = fields.Boolean(string='Notification envoyée')
    days_alert = fields.Integer(string="Période", help='Jours restant pour envoyer une alert', default=2)

