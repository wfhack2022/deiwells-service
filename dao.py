import logging
import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config as cfg
from model import Organization, Address, People


class DataAccessUtil:

    def __init__(self):
        engine = create_engine('postgresql://%s:%s@%s:%s/%s' %
                               (cfg.db_user, cfg.db_password, cfg.db_host, cfg.db_port, cfg.database), echo=True)
        self.Session = sessionmaker(bind=engine)

    def get_organizations(self):
        session = self.Session()

        try:
            orgs = session.query(Organization).all()
            orgs_json = [
                            org.to_json()['raw'] for org in orgs
                        ]
            session.commit()
            return orgs_json
        except Exception as e:
            logging.error('*** Exception in get_organizations: %s' % e)
            session.rollback()
            raise
        finally:
            session.close()

    def get_organization_by_id(self, org_id):
        session = self.Session()

        try:
            org = session.query(Organization).get(org_id)

            if org is None:
                msg = 'Unable to find organization with id = %s' % org_id
                logging.error(msg)
                raise Exception(msg)

            org_json = org.to_json()

            org_json['people'] = [
                item.to_json() for item in org.people
            ]
            return org_json
        except Exception as e:
            logging.error('*** Exception in get_organization_by_id: %s' % e)
            session.rollback()
            raise
        finally:
            session.close()

    def get_organization_by_name(self, name):
        session = self.Session()
        org_exists = session.query(Organization).filter(Organization.name == name).one_or_none()

        if org_exists is not None:
            return org_exists.to_json()

        return org_exists

    def create_organization(self, data):
        logging.info('*** input in create_organization: %s' % data)
        org = {'name': data['name'], 'about': data['about'], 'industry': data['industry']}
        address = data['address']
        people = data['people']
        position = data['position']

        session = self.Session()

        try:
            people_list = []

            logging.info('*** org in get_organizations: %s' % org)

            logging.info('*** address in get_organizations: %s' % address)

            new_org = Organization(name=org['name'], about=org['about'],
                                   industry=org['industry'], raw=data)

            org_address = Address(address_line1=address[0],
                                  address_line2=address[1],
                                  city=address[2] if len(address) > 2 else '',
                                  state=address[3] if len(address) > 3 else '',
                                  pincode=address[4] if len(address) > 4 else '',
                                  country=address[5] if len(address) > 5 else '',
                                  organization=new_org)

            for i in range(len(people)):
                people_entry = People(name=people[i], position=position[i],
                                      organization=new_org, department='admin')
                people_list.append(people_entry)

            session.add(new_org)
            session.add(org_address)
            session.add_all(people_list)
            session.commit()

            the_organization = session.query(Organization).get(new_org.org_id)

            return the_organization.to_json()

        except Exception as e:
            logging.error('*** Exception in create_organization: %s' % e)
            traceback.print_exc()

            session.rollback()
            raise
        finally:
            session.close()
