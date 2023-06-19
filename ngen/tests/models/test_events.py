from django.test import TestCase
from django.core.exceptions import ValidationError

from ngen.models import Event, Network, User, NetworkEntity, Taxonomy, Feed, Tlp, State, Priority, Edge, Report, Contact


# class EventTest(TestCase):
#     fixtures = ["priority.json", "feed.json", "tlp.json", "user.json", "taxonomy.json", "state.json", "edge.json", "report.json", "network_entity.json", "network.json", "contact.json"]

#     def setUp(self):
#         self.taxonomy = Taxonomy.objects.get(pk=1)
#         self.feed = Feed.objects.get(pk=1)
#         self.tlp = Tlp.objects.get(pk=1)
#         print(self.tlp)
#         print(self.feed)
#         print(self.taxonomy)

#     # def test_create_event(self):
#     #     Event.objects.create(taxonomy=self.taxonomy, feed=self.feed)

# tlp
# date
# taxonomy
# feed
# reporter
# evidence_file_path
# notes
# case
# uuid
# tasks
# node_order_by
# comments
