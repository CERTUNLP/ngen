from django.test import TestCase
from django.core.exceptions import ValidationError

from ngen.models import Network, NetworkEntity


class ConstituencyTest(TestCase):

    @classmethod
    def setUp(cls):
        example_entity = NetworkEntity.objects.create(name='Example Entity')
        Network.objects.create(cidr=None, domain=None, network_entity=example_entity)
        Network.objects.create(cidr='163.10.0.0/16', network_entity=example_entity)
        Network.objects.create(cidr='163.10.1.0/24', network_entity=example_entity)
        Network.objects.create(cidr='163.10.2.0/24', network_entity=example_entity)
        Network.objects.create(cidr='163.10.2.1/32', network_entity=example_entity)
        Network.objects.create(cidr='163.10.2.2/32', network_entity=example_entity)
        Network.objects.create(cidr='163.10.2.3/32', network_entity=example_entity)
        Network.objects.create(domain='ar', network_entity=example_entity)
        Network.objects.create(domain='edu.ar', network_entity=example_entity)
        Network.objects.create(domain='unlp.edu.ar', network_entity=example_entity)
        Network.objects.create(domain='info.unlp.edu.ar', network_entity=example_entity)
        Network.objects.create(domain='cert.unlp.edu.ar', network_entity=example_entity)
        Network.objects.create(domain='servicios.cert.unlp.edu.ar', network_entity=example_entity)
        Network.objects.create(cidr='2001:db8::/32', network_entity=example_entity)
        Network.objects.create(cidr='2001:db8:3c4d::/48', network_entity=example_entity)
        Network.objects.create(cidr='2001:db8:3c4d:15::/64', network_entity=example_entity)
        Network.objects.create(cidr='2001:db8:3c4d:0015:0000:0000:1a2f:1a2b/128', network_entity=example_entity)
        Network.objects.create(cidr='0::/0', network_entity=example_entity)

    def test_cidr4_tree(self):
        self.assertEqual(Network.objects.get(cidr='163.10.0.0/16').get_parent(), Network.objects.default_network())
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
        self.assertEqual(Network.objects.get(cidr='2001:db8::/32').get_parent(), Network.objects.default_network())

    def test_domain_tree(self):
        self.assertIn(Network.objects.get(domain='servicios.cert.unlp.edu.ar'),
                      Network.objects.get(domain='cert.unlp.edu.ar').get_children().all())
        self.assertIn(Network.objects.get(domain='info.unlp.edu.ar'),
                      Network.objects.get(domain='unlp.edu.ar').get_children().all())
        self.assertIn(Network.objects.get(domain='unlp.edu.ar'),
                      Network.objects.get(domain='edu.ar').get_children().all())
        self.assertIn(Network.objects.get(domain='edu.ar'),
                      Network.objects.get(domain='ar').get_children().all())
        self.assertEqual(Network.objects.get(domain='ar').get_parent(), Network.objects.default_network())

    def test_network_not_duplicated(self):
        self.assertRaises(ValidationError, Network.objects.create, cidr='163.10.0.0/16', network_entity=NetworkEntity.objects.first())

    def test_network_ipv4_ipv6_mix(self):
        self.assertRaises(ValidationError, Network.objects.create, cidr='163.10.0.0/16', network_entity=NetworkEntity.objects.first())
