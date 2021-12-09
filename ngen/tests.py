from django.test import TestCase

from ngen.models import Network


class ConstituencyTest(TestCase):

    @classmethod
    def setUp(cls):
        Network.objects.create(address='163.10.0.0/16')
        Network.objects.create(address='163.10.1.0/24')
        Network.objects.create(address='163.10.2.0/24')
        Network.objects.create(address='163.10.2.1/32')
        Network.objects.create(address='163.10.2.2/32')
        Network.objects.create(address='163.10.2.3/32')
        Network.objects.create(address='ar')
        Network.objects.create(address='edu.ar')
        Network.objects.create(address='unlp.edu.ar')
        Network.objects.create(address='info.unlp.edu.ar')
        Network.objects.create(address='cert.unlp.edu.ar')
        Network.objects.create(address='servicios.cert.unlp.edu.ar')
        Network.objects.create(address='2001:db8::/32')
        Network.objects.create(address='2001:db8:3c4d::/48')
        Network.objects.create(address='2001:db8:3c4d:15::/64')
        Network.objects.create(address='2001:db8:3c4d:0015:0000:0000:1a2f:1a2b/128')

    def test_cidr4_tree(self):
        self.assertEqual(Network.objects.get(cidr='163.10.0.0/16').get_parent(), Network.lookup_default_network())
        self.assertIn(Network.objects.get(cidr='163.10.0.0/16'), Network.get_root_nodes().first().get_children().all())
        self.assertIn(Network.objects.get(cidr='163.10.1.0/24'),
                      Network.objects.get(cidr='163.10.0.0/16').get_children().all())
        self.assertIn(Network.objects.get(cidr='163.10.2.0/24'),
                      Network.objects.get(cidr='163.10.0.0/16').get_children().all())
        self.assertIn(Network.objects.get(cidr='163.10.2.1/32'),
                      Network.objects.get(cidr='163.10.2.0/24').get_children().all())
        self.assertIn(Network.objects.get(cidr='163.10.2.2/32'),
                      Network.objects.get(cidr='163.10.2.0/24').get_children().all())
        self.assertIn(Network.objects.get(cidr='163.10.2.3/32'),
                      Network.objects.get(cidr='163.10.2.0/24').get_children().all())

    def test_cidr6_tree(self):
        self.assertIn(Network.objects.get(cidr='2001:db8:3c4d:0015:0000:0000:1a2f:1a2b/128'),
                      Network.objects.get(cidr='2001:db8:3c4d:15::/64').get_children().all())
        self.assertIn(Network.objects.get(cidr='2001:db8:3c4d:15::/64'),
                      Network.objects.get(cidr='2001:db8:3c4d::/48').get_children().all())
        self.assertIn(Network.objects.get(cidr='2001:db8:3c4d::/48'),
                      Network.objects.get(cidr='2001:db8::/32').get_children().all())
        self.assertEqual(Network.objects.get(cidr='2001:db8::/32').get_parent(), Network.lookup_default_network())

    def test_domain_tree(self):
        self.assertIn(Network.objects.get(domain='servicios.cert.unlp.edu.ar'),
                      Network.objects.get(domain='cert.unlp.edu.ar').get_children().all())
        self.assertIn(Network.objects.get(domain='info.unlp.edu.ar'),
                      Network.objects.get(domain='unlp.edu.ar').get_children().all())
        self.assertIn(Network.objects.get(domain='unlp.edu.ar'),
                      Network.objects.get(domain='edu.ar').get_children().all())
        self.assertIn(Network.objects.get(domain='edu.ar'),
                      Network.objects.get(domain='ar').get_children().all())
        self.assertEqual(Network.objects.get(domain='ar').get_parent(), Network.lookup_default_network())
