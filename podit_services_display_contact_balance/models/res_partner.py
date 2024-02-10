
from odoo import models, fields, api
from lxml import etree




class ResPartner(models.Model):
    

    _name = 'res.partner'
    _inherit = 'res.partner'
    
    
    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True, string="Currency")
        
    for n in  range(1,50):
        i=str(n)
        field_receivable = f"total_receivable_{i}"
        field_payable = f"total_payable_{i}"
                
        locals()[field_receivable] = fields.Monetary(compute=lambda self,n=n: self._credit_debit_balance_get(n),string='Total Receivable', help="Total amount this customer owes you.", currency_field='currency_id')
        locals()[field_payable] = fields.Monetary(compute=lambda self,n=n: self._credit_debit_balance_get(n),string='Total Payable',help="Total amount you have to pay to this vendor." ,currency_field='currency_id')
                
    

    
    def _get_company_currency(self):
        for partner in self:
            if partner.company_id:
                partner.currency_id = partner.sudo().company_id.currency_id
            else:
                partner.currency_id = self.env.company.currency_id
                
    @api.depends_context('company')
    def _credit_debit_balance_get(self, id):
        i=str(id)
        field_receivable1 = f"total_receivable_{i}"
        field_payable1 = f"total_payable_{i}"
        tables, where_clause, where_params = self.env['account.move.line']._where_calc([
            ('parent_state', '=', 'posted'),
            ('company_id', '=', self.env.company.id),
            ('branch_id','=', id)
        ]).get_sql()

        where_params = [tuple(self.ids)] + where_params
        if where_clause:
            where_clause = 'AND ' + where_clause
        self._cr.execute("""SELECT account_move_line.partner_id, a.account_type, SUM(account_move_line.amount_residual)
                      FROM """ + tables + """
                      LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                      WHERE a.account_type IN ('asset_receivable','liability_payable')
                      AND account_move_line.partner_id IN %s
                      AND account_move_line.reconciled IS NOT TRUE
                      """ + where_clause + """
                      GROUP BY account_move_line.partner_id, a.account_type, account_move_line.branch_id
                      """, where_params)
        treated = self.browse()
        for pid, type, val in self._cr.fetchall():
            partner = self.browse(pid)
            if type == 'asset_receivable':  
                partner[field_receivable1] = val
                if partner not in treated:
                    partner[field_payable1]= False
                    treated |= partner
            elif type == 'liability_payable':
                partner[field_payable1] = -val
                if partner not in treated:
                    partner[field_receivable1] = False
                    treated |= partner
        remaining = (self - treated)
        remaining[field_payable1] = False
        remaining[field_receivable1] = False 
             
    
    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):  
        arch, view = super()._get_view(view_id, view_type, **options) 
        doc = etree.XML(view['arch'])   
        if view_type == 'tree':    
            for node in doc.xpath("//field[contains(@string,'_Total_Receivable')]"):
                doc.remove(node)   
            for node in doc.xpath("//field[contains(@string,'_Total_Payable')]"):
                doc.remove(node)   
            new_ref = doc.xpath("//field[@name='display_name']")      
            if new_ref:
                self.env['res.branch'].flush_model()
                for branch in self.env.user.branch_ids:
                    id = branch.id
                    i=str(id)
                    field_receivable = f"total_receivable_{i}"
                    field_payable = f"total_payable_{i}"
                    if not (doc.xpath("//field[@string='"+branch.name+"_Total_Receivable']")):
                            new_ref[0].addnext(etree.Element('field', {'string': branch.name+'_Total_Receivable', 'name':field_receivable, 'sum':'Total'}))
                            new_ref[0].addnext(etree.Element('field', {'string': branch.name+'_Total_Payable', 'name':field_payable, 'sum':'Total'}))
            view['arch'] = etree.tostring(doc)
            arch, view = super()._get_view(view_id, view_type, **options)   
        return arch, view        