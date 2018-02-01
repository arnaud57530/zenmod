# -*- coding:utf-8 -*-

from openerp import models, fields, api


class AlertScheduler(models.Model):
    _name = 'equipment.scheduler'

    @api.model
    def process_scheduler_queue(self):
        template_end = self.env.ref('GMAO.end_equipment_email_template')
        template_notify = self.env.ref('GMAO.notify_end_equipment_email_template')
        context = self.env.context.copy()
        context['default_subtype_id'] = self.env.ref('mail.mt_comment').id
        date_str = fields.Date.today()
        today = fields.Date.from_string(date_str)
        machines = self.env['machine'].search([('state', '=', 2), ('sent', '=', False)])
        for machine in machines:
            if machine.date_gar:
                days = (fields.Date.from_string(machine.date_gar)-today).days
                if 0 < days <= machine.days_alert:
                    context['default_notified_partner_ids'] = [(4, self.env['res.users'].browse(machine.env.uid).partner_id.id)]
                    context['days'] = days
                    template_notify.sudo().with_context(context).send_mail(
                        machine.id, force_send=True)
                    machine.write({'sent': True})

