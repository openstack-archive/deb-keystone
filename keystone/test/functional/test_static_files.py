import unittest2 as unittest
from keystone.test.functional import common


class TestStaticFiles(common.ApiTestCase):
    def test_pdf_contract(self):
        if not common.isSsl():
            #TODO(ziad): Caller hangs in SSL (but works with cURL)
            r = self.service_request(path='/identitydevguide.pdf')
            self.assertResponseSuccessful(r)

    def test_wadl_contract(self):
        r = self.service_request(path='/identity.wadl')
        self.assertResponseSuccessful(r)

    def test_wadl_common(self):
        r = self.service_request(path='/common.ent')
        self.assertResponseSuccessful(r)

    def test_xsd_contract(self):
        r = self.service_request(path='/xsd/api.xsd')
        self.assertResponseSuccessful(r)

    def test_xsd_atom_contract(self):
        r = self.service_request(path='/xsd/atom/atom.xsd')
        self.assertResponseSuccessful(r)

    def test_xslt(self):
        r = self.service_request(path='/xslt/schema.xslt')
        self.assertResponseSuccessful(r)

    def test_js(self):
        r = self.service_request(path='/js/shjs/sh_java.js')
        self.assertResponseSuccessful(r)

    def test_xml_sample(self):
        r = self.service_request(path='/samples/auth.xml')
        self.assertResponseSuccessful(r)

    def test_json_sample(self):
        r = self.service_request(path='/samples/auth.json')
        self.assertResponseSuccessful(r)

    def test_stylesheet(self):
        r = self.service_request(path='/style/shjs/sh_acid.css')
        self.assertResponseSuccessful(r)


class TestAdminStaticFiles(common.FunctionalTestCase):
    def test_pdf_contract(self):
        if not common.isSsl():
            #TODO(ziad): Caller hangs in SSL (but works with cURL)
            r = self.admin_request(path='/identityadminguide.pdf')
            self.assertResponseSuccessful(r)

    def test_wadl_contract(self):
        r = self.admin_request(path='/identity-admin.wadl')
        self.assertResponseSuccessful(r)

    def test_xsd_contract(self):
        r = self.admin_request(path='/xsd/api.xsd')
        self.assertResponseSuccessful(r)

    def test_xsd_atom_contract(self):
        r = self.admin_request(path='/xsd/atom/atom.xsd')
        self.assertResponseSuccessful(r)

    def test_xslt(self):
        r = self.admin_request(path='/xslt/schema.xslt')
        self.assertResponseSuccessful(r)

    def test_js(self):
        r = self.admin_request(path='/js/shjs/sh_java.js')
        self.assertResponseSuccessful(r)

    def test_xml_sample(self):
        r = self.admin_request(path='/samples/auth.xml')
        self.assertResponseSuccessful(r)

    def test_json_sample(self):
        r = self.admin_request(path='/samples/auth.json')
        self.assertResponseSuccessful(r)

    def test_stylesheet(self):
        r = self.admin_request(path='/style/shjs/sh_acid.css')
        self.assertResponseSuccessful(r)


if __name__ == '__main__':
    unittest.main()
