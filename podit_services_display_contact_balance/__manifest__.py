{
    'name': 'Display contact balance',
    'summary': """Display contact balance in Contact dashboard""",
    'version': '16.0.1.0.1',
    'description': """Display contact balance in Contact dashboard""",
    'author': 'Pod IT Services',
    'company': 'Pod IT Services',
    'website': 'https://poditservices.com/',
    'category': 'Tools',
    'depends': ['base'],
    'license': 'AGPL-3',
    'data': [
        'views/res_partner_form.xml',
    ],
    'installable': True,
    'auto_install': False,
    'uninstall_hook':'uninstall_instrcution',
}