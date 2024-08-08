from django.core.exceptions import ValidationError
from django.test import TestCase

from ngen.models import Network, NetworkEntity


class ConstituencyTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.example_entity = NetworkEntity.objects.create(name='Example Entity')
        cls.default_ipv4 = Network.objects.create(cidr='0.0.0.0/0')
        cls.default_ipv6 = Network.objects.create(cidr='::/0')
        cls.default_domain = Network.objects.create(domain='*')
        cls.ipv4_1 = Network.objects.create(cidr='163.10.0.0/16', network_entity=cls.example_entity)
        cls.ipv4_1_1 = Network.objects.create(cidr='163.10.1.0/24', network_entity=cls.example_entity)
        cls.ipv4_1_2 = Network.objects.create(cidr='163.10.2.0/24', network_entity=cls.example_entity)
        cls.ipv4_1_3 = Network.objects.create(cidr='163.10.250.0/24', network_entity=cls.example_entity)
        cls.ipv4_2_1 = Network.objects.create(cidr='163.10.2.1/32', network_entity=cls.example_entity)
        cls.ipv4_2_2 = Network.objects.create(cidr='163.10.2.2/32', network_entity=cls.example_entity)
        cls.ipv4_2_3 = Network.objects.create(cidr='163.10.2.3/32', network_entity=cls.example_entity)
        Network.objects.create(domain='ar', network_entity=cls.example_entity)
        Network.objects.create(domain='edu.ar', network_entity=cls.example_entity)
        Network.objects.create(domain='unlp.edu.ar', network_entity=cls.example_entity)
        Network.objects.create(domain='info.unlp.edu.ar', network_entity=cls.example_entity)
        Network.objects.create(domain='cert.unlp.edu.ar', network_entity=cls.example_entity)
        Network.objects.create(domain='servicios.cert.unlp.edu.ar', network_entity=cls.example_entity)
        Network.objects.create(cidr='2001:db8::/32', network_entity=cls.example_entity)
        Network.objects.create(cidr='2001:db8:3c4d::/48', network_entity=cls.example_entity)
        Network.objects.create(cidr='2001:db8:3c4d:15::/64', network_entity=cls.example_entity)
        Network.objects.create(cidr='2001:db8:3c4d:0015:0000:0000:1a2f:1a2b/128', network_entity=cls.example_entity)

    def test_cidr4_tree(self):
        self.assertEqual(Network.objects.get(cidr='163.10.0.0/16').get_parent(), self.default_ipv4)
        self.assertIn(Network.objects.get(cidr='163.10.0.0/16'),
                      Network.objects.default_ipv4().first().get_children().all())
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
        self.assertEqual(self.default_ipv4.get_parent(), None)

    def test_cidr6_tree(self):
        self.assertIn(Network.objects.get(cidr='2001:db8:3c4d:0015:0000:0000:1a2f:1a2b/128'),
                      Network.objects.get(cidr='2001:db8:3c4d:15::/64').get_children().all())
        self.assertIn(Network.objects.get(cidr='2001:db8:3c4d:15::/64'),
                      Network.objects.get(cidr='2001:db8:3c4d::/48').get_children().all())
        self.assertIn(Network.objects.get(cidr='2001:db8:3c4d::/48'),
                      Network.objects.get(cidr='2001:db8::/32').get_children().all())
        self.assertEqual(Network.objects.get(cidr='2001:db8::/32').get_parent(), self.default_ipv6)
        self.assertEqual(self.default_ipv6.get_parent(), None)

    def test_domain_tree(self):
        self.assertIn(Network.objects.get(domain='servicios.cert.unlp.edu.ar'),
                      Network.objects.get(domain='cert.unlp.edu.ar').get_children().all())
        self.assertIn(Network.objects.get(domain='info.unlp.edu.ar'),
                      Network.objects.get(domain='unlp.edu.ar').get_children().all())
        self.assertIn(Network.objects.get(domain='unlp.edu.ar'),
                      Network.objects.get(domain='edu.ar').get_children().all())
        self.assertIn(Network.objects.get(domain='edu.ar'),
                      Network.objects.get(domain='ar').get_children().all())
        self.assertEqual(Network.objects.get(domain='ar').get_parent(), self.default_domain)
        self.assertEqual(self.default_domain.get_parent(), None)

    def test_defaults(self):
        """
        Test that the default networks are returned by the default methods and 
        only can be 3 default networks: ipv4, ipv6 and domain.
        """
        self.assertIn(Network.objects.get(cidr='0.0.0.0/0'),
                      Network.objects.defaults())
        self.assertIn(Network.objects.get(cidr='::/0'),
                      Network.objects.defaults())
        self.assertIn(Network.objects.get(domain='*'),
                      Network.objects.defaults())
        self.assertEqual(Network.objects.get(cidr='0.0.0.0/0'),
                         Network.objects.default_ipv4().first())
        self.assertEqual(Network.objects.get(cidr='::/0'),
                         Network.objects.default_ipv6().first())
        self.assertEqual(Network.objects.get(domain='*'),
                         Network.objects.default_domain().first())
        self.assertEqual(self.default_ipv4, Network.objects.default_ipv4().first())
        self.assertEqual(self.default_ipv6, Network.objects.default_ipv6().first())
        self.assertEqual(self.default_domain, Network.objects.default_domain().first())
        self.assertEqual(Network.objects.get(cidr='0.0.0.0/0'), self.default_ipv4)
        self.assertEqual(Network.objects.get(cidr='::/0'), self.default_ipv6)
        self.assertEqual(Network.objects.get(domain='*'), self.default_domain)
        self.assertEqual(Network.objects.defaults().count(), 3)

    def test_network_default_not_duplicated(self):
        """
        Test that the default networks are not duplicated.
        """
        self.assertRaises(ValidationError, Network.objects.create, cidr='0.0.0.0/0')
        self.assertRaises(ValidationError, Network.objects.create, cidr='::/0')
        self.assertRaises(ValidationError, Network.objects.create, domain='*')

    def test_network_not_duplicated(self):
        self.assertRaises(ValidationError, Network.objects.create, cidr='163.10.0.0/16',
                          network_entity=NetworkEntity.objects.first())
        self.assertRaises(ValidationError, Network.objects.create, cidr='163.10.0.0/16')

    def test_network_cidr_domain_mix(self):
        self.assertRaises(ValidationError, Network.objects.create, cidr='1.1.0.0/16', domain='test.edu.ar',
                          network_entity=NetworkEntity.objects.first())

    def test_network_ipv4_update(self):
        test1 = Network.objects.create(cidr='10.0.0.0/24')
        test1_parent = test1.get_parent()
        test1.cidr = '10.0.0.1'
        test1.save()
        self.assertEqual(test1_parent, self.default_ipv4)
        self.assertEqual(test1_parent, test1.get_parent())
        self.assertNotEqual(test1, test1.get_parent())

    def test_network_ipv6_update(self):
        test1 = Network.objects.create(cidr='2222::/64')
        test1_parent = test1.get_parent()
        test1.cidr = '2222::1'
        test1.save()
        self.assertEqual(test1_parent, self.default_ipv6)
        self.assertEqual(test1_parent, test1.get_parent())
        self.assertNotEqual(test1, test1.get_parent())

    def test_network_domain_update(self):
        test1 = Network.objects.create(domain='test.com')
        test1_parent = test1.get_parent()
        test1.domain = 'www.test.com'
        test1.save()
        self.assertEqual(test1_parent, self.default_domain)
        self.assertEqual(test1_parent, test1.get_parent())
        self.assertNotEqual(test1, test1.get_parent())

    def test_delete_entity(self):
        related_networks = Network.objects.filter(network_entity=self.example_entity)
        self.assertNotEqual(related_networks.count(), 0)
        self.example_entity.delete()
        self.assertNotEqual(Network.objects.filter(network_entity=self.example_entity).count(),
                            related_networks.count())
        self.assertEqual(NetworkEntity.objects.filter(name='Example Entity').count(), 0)
        self.assertRaises(NetworkEntity.DoesNotExist, NetworkEntity.objects.get, id=self.example_entity.id)

    def test_insert_ipv4_network(self):
        test1 = Network.objects.create(cidr='163.10.0.0/20')
        self.ipv4_1_1.refresh_from_db()
        self.ipv4_1_2.refresh_from_db()
        self.assertEqual(test1.get_parent(), self.ipv4_1)
        self.assertIn(test1, self.ipv4_1.get_children().all())
        self.assertQuerysetEqual(test1.get_children().all(), [self.ipv4_1_1, self.ipv4_1_2], ordered=False)
        self.assertQuerysetEqual(
            Network.objects.children_of(self.ipv4_1),
            [self.ipv4_1_1, self.ipv4_1_2, self.ipv4_1_3, self.ipv4_2_1, self.ipv4_2_2, self.ipv4_2_3, test1],
            ordered=False
        )
        self.assertEqual(test1, self.ipv4_1_1.parent)
        self.assertEqual(test1, self.ipv4_1_2.parent)
