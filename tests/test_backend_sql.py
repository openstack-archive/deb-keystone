# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

from keystone import catalog
from keystone.common import sql
from keystone import config
from keystone import exception
from keystone import identity
from keystone import policy
from keystone import test
from keystone import token
from keystone import trust


import default_fixtures
import test_backend

CONF = config.CONF
DEFAULT_DOMAIN_ID = CONF.identity.default_domain_id


class SqlTests(test.TestCase):
    def setUp(self):
        super(SqlTests, self).setUp()
        self.config([test.etcdir('keystone.conf.sample'),
                     test.testsdir('test_overrides.conf'),
                     test.testsdir('backend_sql.conf')])

        # initialize managers and override drivers
        self.catalog_man = catalog.Manager()
        self.identity_man = identity.Manager()
        self.token_man = token.Manager()
        self.trust_man = trust.Manager()
        self.policy_man = policy.Manager()

        # create shortcut references to each driver
        self.catalog_api = self.catalog_man.driver
        self.identity_api = self.identity_man.driver
        self.token_api = self.token_man.driver
        self.policy_api = self.policy_man.driver
        self.trust_api = self.trust_man.driver

        # populate the engine with tables & fixtures
        self.load_fixtures(default_fixtures)
        #defaulted by the data load
        self.user_foo['enabled'] = True

    def tearDown(self):
        sql.set_global_engine(None)
        super(SqlTests, self).tearDown()


class SqlIdentity(SqlTests, test_backend.IdentityTests):
    def test_delete_user_with_project_association(self):
        user = {'id': uuid.uuid4().hex,
                'name': uuid.uuid4().hex,
                'domain_id': DEFAULT_DOMAIN_ID,
                'password': uuid.uuid4().hex}
        self.identity_man.create_user({}, user['id'], user)
        self.identity_api.add_user_to_project(self.tenant_bar['id'],
                                              user['id'])
        self.identity_api.delete_user(user['id'])
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.get_projects_for_user,
                          user['id'])

    def test_create_null_user_name(self):
        user = {'id': uuid.uuid4().hex,
                'name': None,
                'domain_id': DEFAULT_DOMAIN_ID,
                'password': uuid.uuid4().hex}
        self.assertRaises(exception.ValidationError,
                          self.identity_man.create_user, {},
                          user['id'],
                          user)
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.get_user,
                          user['id'])
        self.assertRaises(exception.UserNotFound,
                          self.identity_api.get_user_by_name,
                          user['name'],
                          DEFAULT_DOMAIN_ID)

    def test_create_null_project_name(self):
        tenant = {'id': uuid.uuid4().hex,
                  'name': None,
                  'domain_id': DEFAULT_DOMAIN_ID}
        self.assertRaises(exception.ValidationError,
                          self.identity_man.create_project, {},
                          tenant['id'],
                          tenant)
        self.assertRaises(exception.ProjectNotFound,
                          self.identity_api.get_project,
                          tenant['id'])
        self.assertRaises(exception.ProjectNotFound,
                          self.identity_api.get_project_by_name,
                          tenant['name'],
                          DEFAULT_DOMAIN_ID)

    def test_create_null_role_name(self):
        role = {'id': uuid.uuid4().hex,
                'name': None}
        self.assertRaises(exception.Conflict,
                          self.identity_api.create_role,
                          role['id'],
                          role)
        self.assertRaises(exception.RoleNotFound,
                          self.identity_api.get_role,
                          role['id'])

    def test_delete_project_with_user_association(self):
        user = {'id': 'fake',
                'name': 'fakeuser',
                'domain_id': DEFAULT_DOMAIN_ID,
                'password': 'passwd'}
        self.identity_man.create_user({}, 'fake', user)
        self.identity_api.add_user_to_project(self.tenant_bar['id'],
                                              user['id'])
        self.identity_api.delete_project(self.tenant_bar['id'])
        tenants = self.identity_api.get_projects_for_user(user['id'])
        self.assertEquals(tenants, [])

    def test_delete_user_with_metadata(self):
        user = {'id': 'fake',
                'name': 'fakeuser',
                'domain_id': DEFAULT_DOMAIN_ID,
                'password': 'passwd'}
        self.identity_man.create_user({}, 'fake', user)
        self.identity_api.create_metadata(user['id'],
                                          self.tenant_bar['id'],
                                          {'extra': 'extra'})
        self.identity_api.delete_user(user['id'])
        self.assertRaises(exception.MetadataNotFound,
                          self.identity_api.get_metadata,
                          user['id'],
                          self.tenant_bar['id'])

    def test_delete_project_with_metadata(self):
        user = {'id': 'fake',
                'name': 'fakeuser',
                'domain_id': DEFAULT_DOMAIN_ID,
                'password': 'passwd'}
        self.identity_man.create_user({}, 'fake', user)
        self.identity_api.create_metadata(user['id'],
                                          self.tenant_bar['id'],
                                          {'extra': 'extra'})
        self.identity_api.delete_project(self.tenant_bar['id'])
        self.assertRaises(exception.MetadataNotFound,
                          self.identity_api.get_metadata,
                          user['id'],
                          self.tenant_bar['id'])

    def test_update_project_returns_extra(self):
        """This tests for backwards-compatibility with an essex/folsom bug.

        Non-indexed attributes were returned in an 'extra' attribute, instead
        of on the entity itself; for consistency and backwards compatibility,
        those attributes should be included twice.

        This behavior is specific to the SQL driver.

class SqlCatalog(test.TestCase, test_backend.CatalogTests):
    def setUp(self):
        super(SqlCatalog, self).setUp()
        self.config([test.etcdir('keystone.conf.sample'),
                     test.testsdir('test_overrides.conf'),
                     test.testsdir('backend_sql.conf')])
        sql_util.setup_test_database()
        self.catalog_api = catalog_sql.Catalog()
        self.catalog_man = catalog.Manager()
        self.load_fixtures(default_fixtures)

    def test_malformed_catalog_throws_error(self):
        self.catalog_api.create_service('a', {"id": "a", "desc": "a1",
                                        "name": "b"})
        badurl = "http://192.168.1.104:$(compute_port)s/v2/$(tenant)s"
        self.catalog_api.create_endpoint('b', {"id": "b", "region": "b1",
                                         "service_id": "a", "adminurl": badurl,
                                         "internalurl": badurl,
                                         "publicurl": badurl})
        with self.assertRaises(exception.MalformedEndpoint):
            self.catalog_api.get_catalog('fake-user', 'fake-tenant')

    def test_get_catalog_without_endpoint(self):
        new_service = {
            'id': uuid.uuid4().hex,
            'type': uuid.uuid4().hex,
            'name': uuid.uuid4().hex,
            'description': uuid.uuid4().hex,
        }
        self.catalog_api.create_service(
            new_service['id'],
            new_service.copy())
        service_id = new_service['id']

        new_endpoint = {
            'id': uuid.uuid4().hex,
            'region': uuid.uuid4().hex,
            'service_id': service_id,
        }

        self.catalog_api.create_endpoint(
            new_endpoint['id'],
            new_endpoint.copy())

        catalog = self.catalog_api.get_catalog('user', 'tenant')

        service_type = new_service['type']
        region = new_endpoint['region']

        self.assertEqual(catalog[region][service_type]['name'],
                         new_service['name'])
        self.assertEqual(catalog[region][service_type]['id'],
                         new_endpoint['id'])
        self.assertEqual(catalog[region][service_type]['publicURL'],
                         "")
        self.assertEqual(catalog[region][service_type]['adminURL'],
                         None)
        self.assertEqual(catalog[region][service_type]['internalURL'],
                         None)
