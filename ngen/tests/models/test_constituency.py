from django.core.exceptions import ValidationError
from django.test import TestCase

from ngen.models import (
    Network,
    NetworkEntity,
    Event,
    Taxonomy,
    Feed,
    Tlp,
    Priority,
    User,
)


class ConstituencyTest(TestCase):

    fixtures = [
        "tests/priority.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.taxonomy = Taxonomy.objects.create(
            type="incident", name="Phising", slug="phising"
        )
        cls.feed = Feed.objects.create(slug="shodan", name="Shodan")
        cls.tlp = Tlp.objects.create(
            slug="clear",
            when="Given some circumstance",
            why="Some reason",
            information="Some information",
            description="Some description",
            name="Clear",
            code=0,
        )
        cls.priority = Priority.objects.get(name="Medium", severity=3)
        cls.user = User.objects.create(
            username="test", password="test", priority=cls.priority
        )
        cls.example_entity = NetworkEntity.objects.create(name="Example Entity")
        cls.default_ipv4 = Network.objects.create(cidr="0.0.0.0/0")
        cls.default_ipv6 = Network.objects.create(cidr="::/0")
        cls.default_domain = Network.objects.create(domain="*")
        cls.ipv4_1 = Network.objects.create(
            cidr="163.10.0.0/16", network_entity=cls.example_entity
        )
        cls.ipv4_1_1 = Network.objects.create(
            cidr="163.10.1.0/24", network_entity=cls.example_entity
        )
        cls.ipv4_1_2 = Network.objects.create(
            cidr="163.10.2.0/24", network_entity=cls.example_entity
        )
        cls.ipv4_1_3 = Network.objects.create(
            cidr="163.10.250.0/24", network_entity=cls.example_entity
        )
        cls.ipv4_2_1 = Network.objects.create(
            cidr="163.10.2.1/32", network_entity=cls.example_entity
        )
        cls.ipv4_2_2 = Network.objects.create(
            cidr="163.10.2.2/32", network_entity=cls.example_entity
        )
        cls.ipv4_2_3 = Network.objects.create(
            cidr="163.10.2.3/32", network_entity=cls.example_entity
        )
        Network.objects.create(domain="ar", network_entity=cls.example_entity)
        Network.objects.create(domain="edu.ar", network_entity=cls.example_entity)
        Network.objects.create(domain="unlp.edu.ar", network_entity=cls.example_entity)
        Network.objects.create(
            domain="info.unlp.edu.ar", network_entity=cls.example_entity
        )
        Network.objects.create(
            domain="cert.unlp.edu.ar", network_entity=cls.example_entity
        )
        Network.objects.create(
            domain="servicios.cert.unlp.edu.ar", network_entity=cls.example_entity
        )
        Network.objects.create(cidr="2001:db8::/32", network_entity=cls.example_entity)
        Network.objects.create(
            cidr="2001:db8:3c4d::/48", network_entity=cls.example_entity
        )
        Network.objects.create(
            cidr="2001:db8:3c4d:15::/64", network_entity=cls.example_entity
        )
        Network.objects.create(
            cidr="2001:db8:3c4d:0015:0000:0000:1a2f:1a2b/128",
            network_entity=cls.example_entity,
        )

    def test_cidr4_tree(self):
        self.assertEqual(
            Network.objects.get(cidr="163.10.0.0/16").get_parent(), self.default_ipv4
        )
        self.assertIn(
            Network.objects.get(cidr="163.10.0.0/16"),
            Network.objects.default_ipv4().first().get_children().all(),
        )
        self.assertIn(
            Network.objects.get(cidr="163.10.1.0/24"),
            Network.objects.get(cidr="163.10.0.0/16").get_children().all(),
        )
        self.assertIn(
            Network.objects.get(cidr="163.10.2.0/24"),
            Network.objects.get(cidr="163.10.0.0/16").get_children().all(),
        )
        self.assertIn(
            Network.objects.get(cidr="163.10.2.1/32"),
            Network.objects.get(cidr="163.10.2.0/24").get_children().all(),
        )
        self.assertIn(
            Network.objects.get(cidr="163.10.2.2/32"),
            Network.objects.get(cidr="163.10.2.0/24").get_children().all(),
        )
        self.assertIn(
            Network.objects.get(cidr="163.10.2.3/32"),
            Network.objects.get(cidr="163.10.2.0/24").get_children().all(),
        )
        self.assertEqual(self.default_ipv4.get_parent(), None)

    def test_cidr6_tree(self):
        self.assertIn(
            Network.objects.get(cidr="2001:db8:3c4d:0015:0000:0000:1a2f:1a2b/128"),
            Network.objects.get(cidr="2001:db8:3c4d:15::/64").get_children().all(),
        )
        self.assertIn(
            Network.objects.get(cidr="2001:db8:3c4d:15::/64"),
            Network.objects.get(cidr="2001:db8:3c4d::/48").get_children().all(),
        )
        self.assertIn(
            Network.objects.get(cidr="2001:db8:3c4d::/48"),
            Network.objects.get(cidr="2001:db8::/32").get_children().all(),
        )
        self.assertEqual(
            Network.objects.get(cidr="2001:db8::/32").get_parent(), self.default_ipv6
        )
        self.assertEqual(self.default_ipv6.get_parent(), None)

    def test_domain_tree(self):
        self.assertIn(
            Network.objects.get(domain="servicios.cert.unlp.edu.ar"),
            Network.objects.get(domain="cert.unlp.edu.ar").get_children().all(),
        )
        self.assertIn(
            Network.objects.get(domain="info.unlp.edu.ar"),
            Network.objects.get(domain="unlp.edu.ar").get_children().all(),
        )
        self.assertIn(
            Network.objects.get(domain="unlp.edu.ar"),
            Network.objects.get(domain="edu.ar").get_children().all(),
        )
        self.assertIn(
            Network.objects.get(domain="edu.ar"),
            Network.objects.get(domain="ar").get_children().all(),
        )
        self.assertEqual(
            Network.objects.get(domain="ar").get_parent(), self.default_domain
        )
        self.assertEqual(self.default_domain.get_parent(), None)

    def test_defaults(self):
        """
        Test that the default networks are returned by the default methods and
        only can be 3 default networks: ipv4, ipv6 and domain.
        """
        self.assertIn(Network.objects.get(cidr="0.0.0.0/0"), Network.objects.defaults())
        self.assertIn(Network.objects.get(cidr="::/0"), Network.objects.defaults())
        self.assertIn(Network.objects.get(domain="*"), Network.objects.defaults())
        self.assertEqual(
            Network.objects.get(cidr="0.0.0.0/0"),
            Network.objects.default_ipv4().first(),
        )
        self.assertEqual(
            Network.objects.get(cidr="::/0"), Network.objects.default_ipv6().first()
        )
        self.assertEqual(
            Network.objects.get(domain="*"), Network.objects.default_domain().first()
        )
        self.assertEqual(self.default_ipv4, Network.objects.default_ipv4().first())
        self.assertEqual(self.default_ipv6, Network.objects.default_ipv6().first())
        self.assertEqual(self.default_domain, Network.objects.default_domain().first())
        self.assertEqual(Network.objects.get(cidr="0.0.0.0/0"), self.default_ipv4)
        self.assertEqual(Network.objects.get(cidr="::/0"), self.default_ipv6)
        self.assertEqual(Network.objects.get(domain="*"), self.default_domain)
        self.assertEqual(Network.objects.defaults().count(), 3)

    def test_network_default_not_duplicated(self):
        """
        Test that the default networks are not duplicated.
        """
        self.assertRaises(ValidationError, Network.objects.create, cidr="0.0.0.0/0")
        self.assertRaises(ValidationError, Network.objects.create, cidr="::/0")
        self.assertRaises(ValidationError, Network.objects.create, domain="*")

    def test_network_not_duplicated(self):
        self.assertRaises(
            ValidationError,
            Network.objects.create,
            cidr="163.10.0.0/16",
            network_entity=NetworkEntity.objects.first(),
        )
        self.assertRaises(ValidationError, Network.objects.create, cidr="163.10.0.0/16")

    def test_network_cidr_domain_mix(self):
        self.assertRaises(
            ValidationError,
            Network.objects.create,
            cidr="1.1.0.0/16",
            domain="test.edu.ar",
            network_entity=NetworkEntity.objects.first(),
        )

    def test_network_ipv4_update(self):
        test1 = Network.objects.create(cidr="10.0.0.0/24")
        test1_parent = test1.get_parent()
        test1.cidr = "10.0.0.1"
        test1.save()
        self.assertEqual(test1_parent, self.default_ipv4)
        self.assertEqual(test1_parent, test1.get_parent())
        self.assertNotEqual(test1, test1.get_parent())

    def test_network_ipv6_update(self):
        test1 = Network.objects.create(cidr="2222::/64")
        test1_parent = test1.get_parent()
        test1.cidr = "2222::1"
        test1.save()
        self.assertEqual(test1_parent, self.default_ipv6)
        self.assertEqual(test1_parent, test1.get_parent())
        self.assertNotEqual(test1, test1.get_parent())

    def test_network_domain_update(self):
        test1 = Network.objects.create(domain="test.com")
        test1_parent = test1.get_parent()
        test1.domain = "www.test.com"
        test1.save()
        self.assertEqual(test1_parent, self.default_domain)
        self.assertEqual(test1_parent, test1.get_parent())
        self.assertNotEqual(test1, test1.get_parent())

    def test_delete_entity(self):
        related_networks = Network.objects.filter(network_entity=self.example_entity)
        self.assertNotEqual(related_networks.count(), 0)
        self.example_entity.delete()
        self.assertNotEqual(
            Network.objects.filter(network_entity=self.example_entity).count(),
            related_networks.count(),
        )
        self.assertEqual(NetworkEntity.objects.filter(name="Example Entity").count(), 0)
        self.assertRaises(
            NetworkEntity.DoesNotExist,
            NetworkEntity.objects.get,
            id=self.example_entity.id,
        )

    def test_delete_ipv4_network_with_events_and_children(self):
        test1 = Network.objects.create(cidr="163.10.0.0/20")

        event1 = Event.objects.create(
            cidr="163.10.4.111/32",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes 1",
            priority=self.priority,
        )

        event2 = Event.objects.create(
            cidr="163.10.4.112/32",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes 2",
            priority=self.priority,
        )

        event3 = Event.objects.create(
            cidr="163.10.1.1/32",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes 3",
            priority=self.priority,
        )

        event4 = Event.objects.create(
            cidr="163.10.128.1/32",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes 4",
            priority=self.priority,
        )

        event5 = Event.objects.create(
            cidr="163.10.2.111/32",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes 4",
            priority=self.priority,
        )

        self.assertIn(test1, Network.objects.all())
        self.assertIn(event1, test1.events.all())
        self.assertIn(event2, test1.events.all())
        self.assertIn(event3, self.ipv4_1_1.events.all())
        self.assertIn(event4, self.ipv4_1.events.all())
        self.assertIn(event5, self.ipv4_1_2.events.all())

        test1.delete()

        self.assertNotIn(test1, Network.objects.all())
        self.assertIn(event3, self.ipv4_1_1.events.all())
        self.assertIn(event4, self.ipv4_1.events.all())
        self.assertIn(event1, self.ipv4_1.events.all())
        self.assertIn(event2, self.ipv4_1.events.all())
        self.assertIn(event5, self.ipv4_1_2.events.all())

    def test_insert_ipv4_network(self):
        test1 = Network.objects.create(cidr="163.10.0.0/20")
        self.ipv4_1_1.refresh_from_db()
        self.ipv4_1_2.refresh_from_db()
        self.assertEqual(test1.get_parent(), self.ipv4_1)
        self.assertIn(test1, self.ipv4_1.get_children().all())
        self.assertQuerysetEqual(
            test1.get_children().all(), [self.ipv4_1_1, self.ipv4_1_2], ordered=False
        )
        self.assertQuerysetEqual(
            Network.objects.children_of(self.ipv4_1),
            [
                self.ipv4_1_1,
                self.ipv4_1_2,
                self.ipv4_1_3,
                self.ipv4_2_1,
                self.ipv4_2_2,
                self.ipv4_2_3,
                test1,
            ],
            ordered=False,
        )
        self.assertEqual(test1, self.ipv4_1_1.parent)
        self.assertEqual(test1, self.ipv4_1_2.parent)

    def _create_networks(self):
        """
        redes       (eventos)
        1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.33.0.1/32, 1.33.0.2/32, 1.128.0.1/32, 1.129.0.1/32)
            1.1.0.0/16  (1.1.0.1/32, 1.1.0.2/32, 1.1.192.1/32, 1.1.129.1/32)
                1.1.1.0/24  (1.1.1.1/32, 1.1.1.2/32, 1.1.1.129/32)
                1.1.2.0/24  (1.1.2.1/32, 1.1.2.2/32, 1.1.2.129/32)
                1.1.3.0/24  (1.1.3.1/32, 1.1.3.2/32, 1.1.3.129/32)
                1.1.128.0/24  (1.1.128.1/32, 1.1.128.2/32, 1.1.128.129/32)
            1.2.0.0/16  (1.2.0.1/32, 1.2.0.2/32, 1.2.192.1/32, 1.2.129.1/32)
                1.2.1.0/24  (1.2.1.1/32, 1.2.1.2/32, 1.2.1.129/32)
                1.2.2.0/24  (1.2.2.1/32, 1.2.2.2/32, 1.2.2.129/32)
                1.2.3.0/24  (1.2.3.1/32, 1.2.3.2/32, 1.2.3.129/32)
                1.2.128.0/24  (1.2.128.1/32, 1.2.128.2/32, 1.2.128.129/32)
            1.3.0.0/16  (1.3.0.1/32, 1.3.0.2/32, 1.3.192.1/32, 1.3.129.1/32)
                1.3.1.0/24  (1.3.1.1/32, 1.3.1.2/32, 1.3.1.129/32)
                1.3.2.0/24  (1.3.2.1/32, 1.3.2.2/32, 1.3.2.129/32)
                1.3.3.0/24  (1.3.3.1/32, 1.3.3.2/32, 1.3.3.129/32)
                1.3.128.0/24  (1.3.128.1/32, 1.3.128.2/32, 1.3.128.129/32)
            1.32.0.0/16  (1.32.0.1/32, 1.32.0.2/32, 1.32.192.1/32, 1.32.129.1/32)
        """
        # Init networks and events
        self.networks = {
            "1.0.0.0/8": None,
            "1.1.0.0/16": None,
            "1.1.1.0/24": None,
            "1.1.2.0/24": None,
            "1.1.3.0/24": None,
            "1.1.128.0/24": None,
            "1.2.0.0/16": None,
            "1.2.1.0/24": None,
            "1.2.2.0/24": None,
            "1.2.3.0/24": None,
            "1.2.128.0/24": None,
            "1.3.0.0/16": None,
            "1.3.1.0/24": None,
            "1.3.2.0/24": None,
            "1.3.3.0/24": None,
            "1.3.128.0/24": None,
            "1.32.0.0/16": None,
        }
        self.events = {
            "1.0.0.1/32": None,
            "1.0.0.2/32": None,
            "1.33.0.1/32": None,
            "1.33.0.2/32": None,
            "1.128.0.1/32": None,
            "1.129.0.1/32": None,
            "1.1.0.1/32": None,
            "1.1.0.2/32": None,
            "1.1.192.1/32": None,
            "1.1.129.1/32": None,
            "1.1.1.1/32": None,
            "1.1.1.2/32": None,
            "1.1.1.129/32": None,
            "1.1.2.1/32": None,
            "1.1.2.2/32": None,
            "1.1.2.129/32": None,
            "1.1.3.1/32": None,
            "1.1.3.2/32": None,
            "1.1.3.129/32": None,
            "1.1.128.1/32": None,
            "1.1.128.2/32": None,
            "1.1.128.129/32": None,
            "1.2.0.1/32": None,
            "1.2.0.2/32": None,
            "1.2.192.1/32": None,
            "1.2.129.1/32": None,
            "1.2.1.1/32": None,
            "1.2.1.2/32": None,
            "1.2.1.129/32": None,
            "1.2.2.1/32": None,
            "1.2.2.2/32": None,
            "1.2.2.129/32": None,
            "1.2.3.1/32": None,
            "1.2.3.2/32": None,
            "1.2.3.129/32": None,
            "1.2.128.1/32": None,
            "1.2.128.2/32": None,
            "1.2.128.129/32": None,
            "1.3.0.1/32": None,
            "1.3.0.2/32": None,
            "1.3.192.1/32": None,
            "1.3.129.1/32": None,
            "1.3.1.1/32": None,
            "1.3.1.2/32": None,
            "1.3.1.129/32": None,
            "1.3.2.1/32": None,
            "1.3.2.2/32": None,
            "1.3.2.129/32": None,
            "1.3.3.1/32": None,
            "1.3.3.2/32": None,
            "1.3.3.129/32": None,
            "1.3.128.1/32": None,
            "1.3.128.2/32": None,
            "1.3.128.129/32": None,
            "1.32.0.1/32": None,
            "1.32.0.2/32": None,
            "1.32.192.1/32": None,
            "1.32.129.1/32": None,
        }
        # delete if exists
        Network.objects.filter(cidr__in=self.networks.keys()).delete()
        Event.objects.filter(cidr__in=self.events.keys()).delete()
        # create new
        for key in self.networks.keys():
            self.networks[key] = Network.objects.create(cidr=key)
        for key in self.events.keys():
            self.events[key] = Event.objects.create(
                cidr=key,
                taxonomy=self.taxonomy,
                feed=self.feed,
                tlp=self.tlp,
                reporter=self.user,
                notes="Some notes " + key,
                priority=self.priority,
            )
        # networks
        # 1.0.0.0/8
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].get_children().all()),
            {
                self.networks["1.1.0.0/16"],
                self.networks["1.2.0.0/16"],
                self.networks["1.3.0.0/16"],
                self.networks["1.32.0.0/16"],
            },
        )
        # 1.1.0.0/16
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].get_children().all()),
            {
                self.networks["1.3.1.0/24"],
                self.networks["1.3.2.0/24"],
                self.networks["1.3.3.0/24"],
                self.networks["1.3.128.0/24"],
            },
        )
        # 1.2.0.0/16
        self.assertSetEqual(
            set(self.networks["1.2.0.0/16"].get_children().all()),
            {
                self.networks["1.2.1.0/24"],
                self.networks["1.2.2.0/24"],
                self.networks["1.2.3.0/24"],
                self.networks["1.2.128.0/24"],
            },
        )
        # 1.3.0.0/16
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].get_children().all()),
            {
                self.networks["1.3.1.0/24"],
                self.networks["1.3.2.0/24"],
                self.networks["1.3.3.0/24"],
                self.networks["1.3.128.0/24"],
            },
        )

        # events
        # 1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.33.0.1/32, 1.33.0.2/32, 1.128.0.1/32, 1.129.0.1/32)
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].events.all()),
            {
                self.events["1.0.0.1/32"],
                self.events["1.0.0.2/32"],
                self.events["1.33.0.1/32"],
                self.events["1.33.0.2/32"],
                self.events["1.128.0.1/32"],
                self.events["1.129.0.1/32"],
            },
        )
        # 1.1.0.0/16  (1.1.0.1/32, 1.1.0.2/32, 1.1.192.1/32, 1.1.129.1/32)
        self.assertSetEqual(
            set(self.networks["1.1.0.0/16"].events.all()),
            {
                self.events["1.1.0.1/32"],
                self.events["1.1.0.2/32"],
                self.events["1.1.192.1/32"],
                self.events["1.1.129.1/32"],
            },
        )
        # 1.1.1.0/24  (1.1.1.1/32, 1.1.1.2/32, 1.1.1.129/32)
        self.assertSetEqual(
            set(self.networks["1.1.1.0/24"].events.all()),
            {
                self.events["1.1.1.1/32"],
                self.events["1.1.1.2/32"],
                self.events["1.1.1.129/32"],
            },
        )
        # 1.1.2.0/24  (1.1.2.1/32, 1.1.2.2/32, 1.1.2.129/32)
        self.assertSetEqual(
            set(self.networks["1.1.2.0/24"].events.all()),
            {
                self.events["1.1.2.1/32"],
                self.events["1.1.2.2/32"],
                self.events["1.1.2.129/32"],
            },
        )
        # 1.1.3.0/24  (1.1.3.1/32, 1.1.3.2/32, 1.1.3.129/32)
        self.assertSetEqual(
            set(self.networks["1.1.3.0/24"].events.all()),
            {
                self.events["1.1.3.1/32"],
                self.events["1.1.3.2/32"],
                self.events["1.1.3.129/32"],
            },
        )
        # 1.1.128.0/24  (1.1.128.1/32, 1.1.128.2/32, 1.1.128.129/32)
        self.assertSetEqual(
            set(self.networks["1.1.128.0/24"].events.all()),
            {
                self.events["1.1.128.1/32"],
                self.events["1.1.128.2/32"],
                self.events["1.1.128.129/32"],
            },
        )
        # 1.2.0.0/16  (1.2.0.1/32, 1.2.0.2/32, 1.2.192.1/32, 1.2.129.1/32)
        self.assertSetEqual(
            set(self.networks["1.2.0.0/16"].events.all()),
            {
                self.events["1.2.0.1/32"],
                self.events["1.2.0.2/32"],
                self.events["1.2.192.1/32"],
                self.events["1.2.129.1/32"],
            },
        )
        # 1.2.1.0/24  (1.2.1.1/32, 1.2.1.2/32, 1.2.1.129/32)
        self.assertSetEqual(
            set(self.networks["1.2.1.0/24"].events.all()),
            {
                self.events["1.2.1.1/32"],
                self.events["1.2.1.2/32"],
                self.events["1.2.1.129/32"],
            },
        )
        # 1.2.2.0/24  (1.2.2.1/32, 1.2.2.2/32, 1.2.2.129/32)
        self.assertSetEqual(
            set(self.networks["1.2.2.0/24"].events.all()),
            {
                self.events["1.2.2.1/32"],
                self.events["1.2.2.2/32"],
                self.events["1.2.2.129/32"],
            },
        )
        # 1.2.3.0/24  (1.2.3.1/32, 1.2.3.2/32, 1.2.3.129/32)
        self.assertSetEqual(
            set(self.networks["1.2.3.0/24"].events.all()),
            {
                self.events["1.2.3.1/32"],
                self.events["1.2.3.2/32"],
                self.events["1.2.3.129/32"],
            },
        )
        # 1.2.128.0/24  (1.2.128.1/32, 1.2.128.2/32, 1.2.128.129/32)
        self.assertSetEqual(
            set(self.networks["1.2.128.0/24"].events.all()),
            {
                self.events["1.2.128.1/32"],
                self.events["1.2.128.2/32"],
                self.events["1.2.128.129/32"],
            },
        )
        # 1.3.0.0/16  (1.3.0.1/32, 1.3.0.2/32, 1.3.192.1/32, 1.3.129.1/32)
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].events.all()),
            {
                self.events["1.3.0.1/32"],
                self.events["1.3.0.2/32"],
                self.events["1.3.192.1/32"],
                self.events["1.3.129.1/32"],
            },
        )
        # 1.3.1.0/24  (1.3.1.1/32, 1.3.1.2/32, 1.3.1.129/32)
        self.assertSetEqual(
            set(self.networks["1.3.1.0/24"].events.all()),
            {
                self.events["1.3.1.1/32"],
                self.events["1.3.1.2/32"],
                self.events["1.3.1.129/32"],
            },
        )
        # 1.3.2.0/24  (1.3.2.1/32, 1.3.2.2/32, 1.3.2.129/32)
        self.assertSetEqual(
            set(self.networks["1.3.2.0/24"].events.all()),
            {
                self.events["1.3.2.1/32"],
                self.events["1.3.2.2/32"],
                self.events["1.3.2.129/32"],
            },
        )
        # 1.3.3.0/24  (1.3.3.1/32, 1.3.3.2/32, 1.3.3.129/32)
        self.assertSetEqual(
            set(self.networks["1.3.3.0/24"].events.all()),
            {
                self.events["1.3.3.1/32"],
                self.events["1.3.3.2/32"],
                self.events["1.3.3.129/32"],
            },
        )
        # 1.3.128.0/24  (1.3.128.1/32, 1.3.128.2/32, 1.3.128.129/32)
        self.assertSetEqual(
            set(self.networks["1.3.128.0/24"].events.all()),
            {
                self.events["1.3.128.1/32"],
                self.events["1.3.128.2/32"],
                self.events["1.3.128.129/32"],
            },
        )
        # 1.32.0.0/16  (1.32.0.1/32, 1.32.0.2/32, 1.32.192.1/32, 1.32.129.1/32)
        self.assertSetEqual(
            set(self.networks["1.32.0.0/16"].events.all()),
            {
                self.events["1.32.0.1/32"],
                self.events["1.32.0.2/32"],
                self.events["1.32.192.1/32"],
                self.events["1.32.129.1/32"],
            },
        )

    def test_modify_network_increase_mask(self):
        """
        modificar la red - aumentar mascara a red no existente
        1.3.0.0/16 -> 1.3.0.0/17
        expectativa:
        redes       (eventos)
        1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.33.0.1/32, 1.33.0.2/32, 1.128.0.1/32, 1.129.0.1/32, 1.3.192.1/32, 1.3.129.1/32) <<-
            1.1.0.0/16  (1.1.0.1/32, 1.1.0.2/32, 1.1.192.1/32)
                1.1.1.0/24  (1.1.1.1/32, 1.1.1.2/32, 1.1.1.129/32)
                1.1.2.0/24  (1.1.2.1/32, 1.1.2.2/32, 1.1.2.129/32)
                1.1.3.0/24  (1.1.3.1/32, 1.1.3.2/32, 1.1.3.129/32)
                1.1.128.0/24  (1.1.128.1/32, 1.1.128.2/32, 1.1.128.129/32)
            1.2.0.0/16  (1.2.0.1/32, 1.2.0.2/32, 1.2.192.1/32)
                1.2.1.0/24  (1.2.1.1/32, 1.2.1.2/32, 1.2.1.129/32)
                1.2.2.0/24  (1.2.2.1/32, 1.2.2.2/32, 1.2.2.129/32)
                1.2.3.0/24  (1.2.3.1/32, 1.2.3.2/32, 1.2.3.129/32)
                1.2.128.0/24  (1.2.128.1/32, 1.2.128.2/32, 1.2.128.129/32)
            1.3.0.0/17  (1.3.0.1/32, 1.3.0.2/32) <<-
                1.3.1.0/24  (1.3.1.1/32, 1.3.1.2/32, 1.3.1.129/32)
                1.3.2.0/24  (1.3.2.1/32, 1.3.2.2/32, 1.3.2.129/32)
                1.3.3.0/24  (1.3.3.1/32, 1.3.3.2/32, 1.3.3.129/32)
            1.3.128.0/24  (1.3.128.1/32, 1.3.128.2/32, 1.3.128.129/32) <<-
            1.32.0.0/16  (1.32.0.1/32, 1.32.0.2/32, 1.32.192.1/32, 1.32.129.1/32)
        """
        self._create_networks()

        self.networks["1.3.0.0/16"].cidr = "1.3.0.0/17"
        self.networks["1.3.0.0/16"].save()

        for n in self.networks.values():
            n.refresh_from_db()
        for e in self.events.values():
            e.refresh_from_db()

        # networks
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].get_children().all()),
            {
                self.networks["1.3.1.0/24"],
                self.networks["1.3.2.0/24"],
                self.networks["1.3.3.0/24"],
            },
        )
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].get_children().all()),
            {
                self.networks["1.1.0.0/16"],
                self.networks["1.2.0.0/16"],
                self.networks["1.3.0.0/16"],
                self.networks["1.3.128.0/24"],
                self.networks["1.32.0.0/16"],
            },
        )
        self.assertIn(
            self.networks["1.3.128.0/24"],
            self.networks["1.0.0.0/8"].get_children().all(),
        )

        # events
        # 1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.33.0.1/32, 1.33.0.2/32, 1.128.0.1/32, 1.129.0.1/32, 1.3.192.1/32, 1.3.129.1/32) <<-
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].events.all()),
            {
                self.events["1.0.0.1/32"],
                self.events["1.0.0.2/32"],
                self.events["1.33.0.1/32"],
                self.events["1.33.0.2/32"],
                self.events["1.128.0.1/32"],
                self.events["1.129.0.1/32"],
                self.events["1.3.192.1/32"],
                self.events["1.3.129.1/32"],
            },
        )
        # 1.3.0.0/17  (1.3.0.1/32, 1.3.0.2/32, 1.3.192.1/32) <<-
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].events.all()),
            {
                self.events["1.3.0.1/32"],
                self.events["1.3.0.2/32"],
            },
        )
        # 1.3.128.0/24  (1.3.128.1/32, 1.3.128.2/32, 1.3.128.129/32) <<-
        self.assertSetEqual(
            set(self.networks["1.3.128.0/24"].events.all()),
            {
                self.events["1.3.128.1/32"],
                self.events["1.3.128.2/32"],
                self.events["1.3.128.129/32"],
            },
        )

    def test_modify_network_decrease_mask(self):
        """
        modificar la red - disminuir mascara a red no existente
        1.3.0.0/16 -> 1.2.0.0/15
        redes       (eventos)
        1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.33.0.1/32, 1.33.0.2/32, 1.128.0.1/32, 1.129.0.1/32)
            1.1.0.0/16  (1.1.0.1/32, 1.1.0.2/32, 1.1.192.1/32, 1.1.129.1/32)
                1.1.1.0/24  (1.1.1.1/32, 1.1.1.2/32, 1.1.1.129/32)
                1.1.2.0/24  (1.1.2.1/32, 1.1.2.2/32, 1.1.2.129/32)
                1.1.3.0/24  (1.1.3.1/32, 1.1.3.2/32, 1.1.3.129/32)
                1.1.128.0/24  (1.1.128.1/32, 1.1.128.2/32, 1.1.128.129/32)
            1.2.0.0/15  (1.3.0.1/32, 1.3.0.2/32, 1.3.192.1/32, 1.3.129.1/32) <<-
                1.2.0.0/16  (1.2.0.1/32, 1.2.0.2/32, 1.2.192.1/32, 1.2.129.1/32) <<-
                    1.2.1.0/24  (1.2.1.1/32, 1.2.1.2/32, 1.2.1.129/32) <<-
                    1.2.2.0/24  (1.2.2.1/32, 1.2.2.2/32, 1.2.2.129/32) <<-
                    1.2.3.0/24  (1.2.3.1/32, 1.2.3.2/32, 1.2.3.129/32) <<-
                    1.2.128.0/24  (1.2.128.1/32, 1.2.128.2/32, 1.2.128.129/32) <<-
                1.3.1.0/24  (1.3.1.1/32, 1.3.1.2/32, 1.3.1.129/32) <<-
                1.3.2.0/24  (1.3.2.1/32, 1.3.2.2/32, 1.3.2.129/32) <<-
                1.3.3.0/24  (1.3.3.1/32, 1.3.3.2/32, 1.3.3.129/32) <<-
                1.3.128.0/24  (1.3.128.1/32, 1.3.128.2/32, 1.3.128.129/32) <<-
            1.32.0.0/16  (1.32.0.1/32, 1.32.0.2/32, 1.32.192.1/32, 1.32.129.1/32)
        """
        self._create_networks()
        self.networks["1.3.0.0/16"].cidr = "1.2.0.0/15"
        self.networks["1.3.0.0/16"].save()

        for n in self.networks.values():
            n.refresh_from_db()
        for e in self.events.values():
            e.refresh_from_db()

        # networks
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].get_children().all()),
            {
                self.networks["1.1.0.0/16"],
                self.networks["1.3.0.0/16"],
                self.networks["1.32.0.0/16"],
            },
        )
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].get_children().all()),
            {
                self.networks["1.2.0.0/16"],
                self.networks["1.3.1.0/24"],
                self.networks["1.3.2.0/24"],
                self.networks["1.3.3.0/24"],
                self.networks["1.3.128.0/24"],
            },
        )
        self.assertSetEqual(
            set(self.networks["1.2.0.0/16"].get_children().all()),
            {
                self.networks["1.2.1.0/24"],
                self.networks["1.2.2.0/24"],
                self.networks["1.2.3.0/24"],
                self.networks["1.2.128.0/24"],
            },
        )

        # events
        # 1.2.0.0/15  (1.3.0.1/32, 1.3.0.2/32, 1.3.192.1/32, 1.3.129.1/32) <<-
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].events.all()),
            {
                self.events["1.3.0.1/32"],
                self.events["1.3.0.2/32"],
                self.events["1.3.192.1/32"],
                self.events["1.3.129.1/32"],
            },
        )
        # 1.2.0.0/16  (1.2.0.1/32, 1.2.0.2/32, 1.2.192.1/32, 1.2.129.1/32) <<-
        self.assertSetEqual(
            set(self.networks["1.2.0.0/16"].events.all()),
            {
                self.events["1.2.0.1/32"],
                self.events["1.2.0.2/32"],
                self.events["1.2.192.1/32"],
                self.events["1.2.129.1/32"],
            },
        )
        # 1.3.1.0/24  (1.3.1.1/32, 1.3.1.2/32, 1.3.1.129/32) <<-
        self.assertSetEqual(
            set(self.networks["1.3.1.0/24"].events.all()),
            {
                self.events["1.3.1.1/32"],
                self.events["1.3.1.2/32"],
                self.events["1.3.1.129/32"],
            },
        )

        # 1.3.2.0/24  (1.3.2.1/32, 1.3.2.2/32, 1.3.2.129/32) <<-
        self.assertSetEqual(
            set(self.networks["1.3.2.0/24"].events.all()),
            {
                self.events["1.3.2.1/32"],
                self.events["1.3.2.2/32"],
                self.events["1.3.2.129/32"],
            },
        )

        # 1.3.3.0/24  (1.3.3.1/32, 1.3.3.2/32, 1.3.3.129/32) <<-
        self.assertSetEqual(
            set(self.networks["1.3.3.0/24"].events.all()),
            {
                self.events["1.3.3.1/32"],
                self.events["1.3.3.2/32"],
                self.events["1.3.3.129/32"],
            },
        )

        # 1.3.128.0/24  (1.3.128.1/32, 1.3.128.2/32, 1.3.128.129/32) <<-
        self.assertSetEqual(
            set(self.networks["1.3.128.0/24"].events.all()),
            {
                self.events["1.3.128.1/32"],
                self.events["1.3.128.2/32"],
                self.events["1.3.128.129/32"],
            },
        )

    def test_modify_network_change_tree(self):
        """
        modificar la red - cambiar de arbol
        1.3.0.0/16 -> 1.1.128.0/17
        redes       (eventos)
        1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.33.0.1/32, 1.33.0.2/32, 1.128.0.1/32, 1.129.0.1/32, 1.3.0.1/32, 1.3.0.2/32, 1.3.192.1/32, 1.3.129.1/32) <<-
            1.1.0.0/16  (1.1.0.1/32, 1.1.0.2/32)
                1.1.1.0/24  (1.1.1.1/32, 1.1.1.2/32, 1.1.1.129/32)
                1.1.2.0/24  (1.1.2.1/32, 1.1.2.2/32, 1.1.2.129/32)
                1.1.3.0/24  (1.1.3.1/32, 1.1.3.2/32, 1.1.3.129/32)
                1.1.128.0/17 (1.1.192.1/32, 1.1.129.1/32) <<-
                    1.1.128.0/24  (1.1.128.1/32, 1.1.128.2/32, 1.1.128.129/32) <<-
            1.2.0.0/16  (1.2.0.1/32, 1.2.0.2/32, 1.2.192.1/32, 1.2.129.1/32)
                1.2.1.0/24  (1.2.1.1/32, 1.2.1.2/32, 1.2.1.129/32)
                1.2.2.0/24  (1.2.2.1/32, 1.2.2.2/32, 1.2.2.129/32)
                1.2.3.0/24  (1.2.3.1/32, 1.2.3.2/32, 1.2.3.129/32)
                1.2.128.0/24  (1.2.128.1/32, 1.2.128.2/32, 1.2.128.129/32)
            1.3.1.0/24  (1.3.1.1/32, 1.3.1.2/32, 1.3.1.129/32)
            1.3.2.0/24  (1.3.2.1/32, 1.3.2.2/32, 1.3.2.129/32)
            1.3.3.0/24  (1.3.3.1/32, 1.3.3.2/32, 1.3.3.129/32)
            1.3.128.0/24  (1.3.128.1/32, 1.3.128.2/32, 1.3.128.129/32)
            1.32.0.0/16  (1.32.0.1/32, 1.32.0.2/32, 1.32.192.1/32, 1.32.129.1/32)
        """
        self._create_networks()

        self.networks["1.3.0.0/16"].cidr = "1.1.128.0/17"
        self.networks["1.3.0.0/16"].save()

        for n in self.networks.values():
            n.refresh_from_db()
        for e in self.events.values():
            e.refresh_from_db()

        # networks
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].get_children().all()),
            {
                self.networks["1.1.0.0/16"],
                self.networks["1.2.0.0/16"],
                self.networks["1.3.1.0/24"],
                self.networks["1.3.2.0/24"],
                self.networks["1.3.3.0/24"],
                self.networks["1.3.128.0/24"],
                self.networks["1.32.0.0/16"],
            },
        )
        self.assertSetEqual(
            set(self.networks["1.1.0.0/16"].get_children().all()),
            {
                self.networks["1.1.1.0/24"],
                self.networks["1.1.2.0/24"],
                self.networks["1.1.3.0/24"],
                self.networks["1.3.0.0/16"],
            },
        )
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].get_children().all()),
            {
                self.networks["1.1.128.0/24"],
            },
        )

        # events
        # 1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.33.0.1/32, 1.33.0.2/32, 1.128.0.1/32, 1.129.0.1/32, 1.3.0.1/32, 1.3.0.2/32, 1.3.192.1/32, 1.3.129.1/32) <<-
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].events.all()),
            {
                self.events["1.0.0.1/32"],
                self.events["1.0.0.2/32"],
                self.events["1.33.0.1/32"],
                self.events["1.33.0.2/32"],
                self.events["1.128.0.1/32"],
                self.events["1.129.0.1/32"],
                self.events["1.3.0.1/32"],
                self.events["1.3.0.2/32"],
                self.events["1.3.192.1/32"],
                self.events["1.3.129.1/32"],
            },
        )
        # 1.1.128.0/17 (1.1.192.1/32, 1.1.129.1/32) <<-
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].events.all()),
            {
                self.events["1.1.192.1/32"],
                self.events["1.1.129.1/32"],
            },
        )
        # 1.1.128.0/24  (1.1.128.1/32, 1.1.128.2/32, 1.1.128.129/32) <<-
        self.assertSetEqual(
            set(self.networks["1.1.128.0/24"].events.all()),
            {
                self.events["1.1.128.1/32"],
                self.events["1.1.128.2/32"],
                self.events["1.1.128.129/32"],
            },
        )

    def test_modify_network_make_leaf(self):
        """
        modificar la red - hacer hoja
        1.3.0.0/16 -> 1.3.0.44/32
        redes       (eventos)
        1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.33.0.1/32, 1.33.0.2/32, 1.128.0.1/32, 1.129.0.1/32, 1.3.0.1/32, 1.3.0.2/32, 1.3.192.1/32, 1.3.129.1/32) <<-
            1.1.0.0/16  (1.1.0.1/32, 1.1.0.2/32, 1.1.192.1/32, 1.1.129.1/32)
                1.1.1.0/24  (1.1.1.1/32, 1.1.1.2/32, 1.1.1.129/32)
                1.1.2.0/24  (1.1.2.1/32, 1.1.2.2/32, 1.1.2.129/32)
                1.1.3.0/24  (1.1.3.1/32, 1.1.3.2/32, 1.1.3.129/32)
                1.1.128.0/24  (1.1.128.1/32, 1.1.128.2/32, 1.1.128.129/32)
            1.2.0.0/16  (1.2.0.1/32, 1.2.0.2/32, 1.2.192.1/32, 1.2.129.1/32)
                1.2.1.0/24  (1.2.1.1/32, 1.2.1.2/32, 1.2.1.129/32)
                1.2.2.0/24  (1.2.2.1/32, 1.2.2.2/32, 1.2.2.129/32)
                1.2.3.0/24  (1.2.3.1/32, 1.2.3.2/32, 1.2.3.129/32)
                1.2.128.0/24  (1.2.128.1/32, 1.2.128.2/32, 1.2.128.129/32)
            1.3.0.44/16  () <<-
            1.3.1.0/24  (1.3.1.1/32, 1.3.1.2/32, 1.3.1.129/32)
            1.3.2.0/24  (1.3.2.1/32, 1.3.2.2/32, 1.3.2.129/32)
            1.3.3.0/24  (1.3.3.1/32, 1.3.3.2/32, 1.3.3.129/32)
            1.3.128.0/24  (1.3.128.1/32, 1.3.128.2/32, 1.3.128.129/32)
            1.32.0.0/16  (1.32.0.1/32, 1.32.0.2/32, 1.32.192.1/32, 1.32.129.1/32)
        """
        self._create_networks()

        self.networks["1.3.0.0/16"].cidr = "1.3.0.44/32"
        self.networks["1.3.0.0/16"].save()

        for n in self.networks.values():
            n.refresh_from_db()
        for e in self.events.values():
            e.refresh_from_db()

        # networks
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].get_children().all()),
            {
                self.networks["1.1.0.0/16"],
                self.networks["1.2.0.0/16"],
                self.networks["1.3.0.0/16"],
                self.networks["1.32.0.0/16"],
                self.networks["1.3.1.0/24"],
                self.networks["1.3.2.0/24"],
                self.networks["1.3.3.0/24"],
                self.networks["1.3.128.0/24"],
            },
        )
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].get_children().all()),
            set(),
        )

        # events
        # 1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.33.0.1/32, 1.33.0.2/32, 1.128.0.1/32, 1.129.0.1/32, 1.3.0.1/32, 1.3.0.2/32, 1.3.192.1/32, 1.3.129.1/32) <<-
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].events.all()),
            {
                self.events["1.0.0.1/32"],
                self.events["1.0.0.2/32"],
                self.events["1.33.0.1/32"],
                self.events["1.33.0.2/32"],
                self.events["1.128.0.1/32"],
                self.events["1.129.0.1/32"],
                self.events["1.3.0.1/32"],
                self.events["1.3.0.2/32"],
                self.events["1.3.192.1/32"],
                self.events["1.3.129.1/32"],
            },
        )
        # 1.3.0.44/16  () <<-
        self.assertSetEqual(
            set(self.networks["1.3.0.0/16"].events.all()),
            set(),
        )

    def test_modify_win_parent_events(self):
        """
        modificar la red - hacer ganar eventos del padre sin cambiar arbol de redes
        1.32.0.0/16 -> 1.32.0.0/15
        redes       (eventos)
        1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.128.0.1/32, 1.129.0.1/32) <<-
            1.1.0.0/16  (1.1.0.1/32, 1.1.0.2/32, 1.1.192.1/32, 1.1.129.1/32)
                1.1.1.0/24  (1.1.1.1/32, 1.1.1.2/32, 1.1.1.129/32)
                1.1.2.0/24  (1.1.2.1/32, 1.1.2.2/32, 1.1.2.129/32)
                1.1.3.0/24  (1.1.3.1/32, 1.1.3.2/32, 1.1.3.129/32)
                1.1.128.0/24  (1.1.128.1/32, 1.1.128.2/32, 1.1.128.129/32)
            1.2.0.0/16  (1.2.0.1/32, 1.2.0.2/32, 1.2.192.1/32, 1.2.129.1/32)
                1.2.1.0/24  (1.2.1.1/32, 1.2.1.2/32, 1.2.1.129/32)
                1.2.2.0/24  (1.2.2.1/32, 1.2.2.2/32, 1.2.2.129/32)
                1.2.3.0/24  (1.2.3.1/32, 1.2.3.2/32, 1.2.3.129/32)
                1.2.128.0/24  (1.2.128.1/32, 1.2.128.2/32, 1.2.128.129/32)
            1.3.0.0/16  (1.3.0.1/32, 1.3.0.2/32, 1.3.192.1/32, 1.3.129.1/32)
                1.3.1.0/24  (1.3.1.1/32, 1.3.1.2/32, 1.3.1.129/32)
                1.3.2.0/24  (1.3.2.1/32, 1.3.2.2/32, 1.3.2.129/32)
                1.3.3.0/24  (1.3.3.1/32, 1.3.3.2/32, 1.3.3.129/32)
                1.3.128.0/24  (1.3.128.1/32, 1.3.128.2/32, 1.3.128.129/32)
            1.32.0.0/15  (1.32.0.1/32, 1.32.0.2/32, 1.32.192.1/32, 1.32.129.1/32, 1.33.0.1/32, 1.33.0.2/32) <<-
        """
        self._create_networks()

        self.networks["1.32.0.0/16"].cidr = "1.32.0.0/15"
        self.networks["1.32.0.0/16"].save()

        for n in self.networks.values():
            n.refresh_from_db()
        for e in self.events.values():
            e.refresh_from_db()

        # networks
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].get_children().all()),
            {
                self.networks["1.1.0.0/16"],
                self.networks["1.2.0.0/16"],
                self.networks["1.3.0.0/16"],
                self.networks["1.32.0.0/16"],
            },
        )
        self.assertSetEqual(
            set(self.networks["1.32.0.0/16"].get_children().all()),
            set(),
        )

        # events
        # 1.0.0.0/8   (1.0.0.1/32, 1.0.0.2/32, 1.128.0.1/32, 1.129.0.1/32) <<-
        self.assertSetEqual(
            set(self.networks["1.0.0.0/8"].events.all()),
            {
                self.events["1.0.0.1/32"],
                self.events["1.0.0.2/32"],
                self.events["1.128.0.1/32"],
                self.events["1.129.0.1/32"],
            },
        )
        # 1.32.0.0/15  (1.32.0.1/32, 1.32.0.2/32, 1.32.192.1/32, 1.32.129.1/32, 1.33.0.1/32, 1.33.0.2/32) <<-
        self.assertSetEqual(
            set(self.networks["1.32.0.0/16"].events.all()),
            {
                self.events["1.32.0.1/32"],
                self.events["1.32.0.2/32"],
                self.events["1.32.192.1/32"],
                self.events["1.32.129.1/32"],
                self.events["1.33.0.1/32"],
                self.events["1.33.0.2/32"],
            },
        )

    def test_loop_ascendant_level0(self):
        self.ipv4_1.parent = self.ipv4_1
        self.assertRaises(ValidationError, self.ipv4_1.save)

    def test_loop_ascendant_level1(self):
        self.ipv4_1.parent = self.ipv4_1_3
        self.assertRaises(ValidationError, self.ipv4_1.save)

    def test_loop_descendant_level0(self):
        self.ipv4_1.children.add(self.ipv4_1)
        self.assertRaises(ValidationError, self.ipv4_1.save)

    def test_loop_descendant_level1(self):
        self.ipv4_1_2.children.add(self.ipv4_1)
        self.assertRaises(ValidationError, self.ipv4_1_2.save)
