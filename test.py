from flask import jsonify
from dao import DataAccessUtil

dao = DataAccessUtil()

org_payload = {
 'name' : 'Santhosh\'s Test Org5',
 'about' : 'Test about',
 'industry': 'Software',
}

address_payload = ['addrl1', 'addrl2', 'city', 'st', '123456', 'India']
people_payload = ['Santhosh', 'Palak', 'Ragu', 'Srini', 'Kumar']
position_payload = ['Engg', 'Engg', 'Engg', 'Engg', 'Engg']

res = (dao.create_organization(org_payload, address_payload, people_payload, position_payload))
print(res)