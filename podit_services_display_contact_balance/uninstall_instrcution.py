from odoo import SUPERUSER_ID, api
from lxml import etree

def uninstall_instrcution(cr, registry):
    env =api.Environment(cr, SUPERUSER_ID, {})
    
    view_id = env['ir.model.data'].sudo()._xmlid_lookup('base.view_partner_tree')[2]
    print("called:",view_id)
    view = env['ir.ui.view'].browse(int(view_id))
    doc = etree.XML(view.arch)
    for node in doc.xpath("//field[contains(@string,'_Total_Receivable')]"):
                doc.remove(node)   
    for node in doc.xpath("//field[contains(@string,'_Total_Payable')]"):
                doc.remove(node)   
    view.write({'arch': etree.tostring(doc)})
    