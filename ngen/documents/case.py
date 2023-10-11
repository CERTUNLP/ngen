from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl_drf.compat import KeywordField, StringField
from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_RANGE, LOOKUP_QUERY_GT, LOOKUP_QUERY_IN, \
    LOOKUP_QUERY_GTE, LOOKUP_QUERY_LT, LOOKUP_QUERY_LTE, LOOKUP_FILTER_TERMS, LOOKUP_FILTER_PREFIX, \
    LOOKUP_FILTER_WILDCARD, LOOKUP_QUERY_EXCLUDE, LOOKUP_QUERY_ISNULL, LOOKUP_FILTER_EXISTS
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    DefaultOrderingFilterBackend,
    IdsFilterBackend, OrderingFilterBackend, SearchFilterBackend, )
from django_elasticsearch_dsl_drf.pagination import QueryFriendlyPageNumberPagination
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch_dsl import analyzer

from ngen.models import Case

INDEX = Index('case')

INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)

_filters = ["lowercase", "stop", "snowball"]

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=_filters,
    char_filter=["html_strip"]
)


@INDEX.doc_type
class CaseDocument(Document):
    tlp = StringField(
        attr="tlp.name",
        analyzer=html_strip,
        fields={
            'raw': KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    state = StringField(
        attr="state.name",
        analyzer=html_strip,
        fields={
            'raw': KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    priority = StringField(
        attr="priority.name",
        analyzer=html_strip,
        fields={
            'raw': KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    assigned = fields.ObjectField(
        properties={
            'username': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }),
            'first_name': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }),
            'last_name': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }),
            'email': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                })
        })

    comments = fields.ListField(
        fields.ObjectField(
            properties={
                'content': StringField(
                    analyzer=html_strip,
                    fields={
                        'raw': KeywordField(),
                        'suggest': fields.CompletionField(),
                    })}))

    merged = fields.BooleanField()

    mergeable = fields.BooleanField()

    blocked = fields.BooleanField()

    evidence = fields.ListField(
        fields.ObjectField(
            properties={
                'filename': StringField(
                    analyzer=html_strip,
                    fields={
                        'raw': KeywordField(),
                        'suggest': fields.CompletionField(),
                    }),
            }))

    artifacts = fields.ListField(
        fields.ObjectField(
            properties={
                'type': StringField(
                    analyzer=html_strip,
                    fields={
                        'raw': KeywordField(),
                        'suggest': fields.CompletionField(),
                    }),
                'value': StringField(
                    analyzer=html_strip,
                    fields={
                        'raw': KeywordField(),
                        'suggest': fields.CompletionField(),
                    }),
            }))

    parent = fields.ObjectField(
        properties={
            'uuid': StringField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'suggest': fields.CompletionField(),
                }),
            'id': fields.IntegerField()
        })
    children = fields.ListField(
        fields.ObjectField(
            properties={
                'uuid': StringField(
                    analyzer=html_strip,
                    fields={
                        'raw': KeywordField(),
                        'suggest': fields.CompletionField(),
                    }),
                'id': fields.IntegerField()
            }))

    events = fields.ListField(
        fields.ObjectField(
            properties={
                'uuid': StringField(
                    analyzer=html_strip,
                    fields={
                        'raw': KeywordField(),
                        'suggest': fields.CompletionField(),
                    }),
                'id': fields.IntegerField(),
                'address': StringField(
                    attr='address.address.__str__',
                    analyzer=html_strip,
                    fields={
                        'raw': KeywordField(),
                    }),
                'cidr': fields.IpField(
                    attr='cidr.network_address.exploded',
                    fields={
                        'raw': KeywordField(),
                    }),
                'domain': StringField(
                    fields={
                        'raw': KeywordField(),
                    }),
                'date': fields.DateField(
                    fields={
                        'raw': KeywordField(),
                    }),
                'priority': StringField(
                    attr='priority.name',
                    fields={
                        'raw': KeywordField(),
                    }),
                'tlp': StringField(
                    attr='tlp.name',
                    fields={
                        'raw': KeywordField(),
                    }),
                'feed': StringField(
                    attr='feed.name',
                    fields={
                        'raw': KeywordField(),
                    }),
                'reporter': StringField(
                    attr='reporter.username',
                    fields={
                        'raw': KeywordField(),
                    }),
            }))

    # "priority": "http://localhost:8000/api/administration/priority/5/",
    # "tlp": "http://localhost:8000/api/administration/tlp/1/",
    # "taxonomy": "http://localhost:8000/api/taxonomy/20/",
    # "feed": "http://localhost:8000/api/administration/feed/2/",
    # "reporter": "http://localhost:8000/api/user/1/",
    class Django(object):
        model = Case
        fields = [
            'id',
            'date',
            'attend_date',
            'solve_date',
            'report_message_id',
            'uuid',
            'lifecycle',
        ]


class CaseDocumentSerializer(DocumentSerializer):
    class Meta:
        document = CaseDocument
        fields = [
            'id',
            'date',
            'attend_date',
            'solve_date',
            'report_message_id',
            'uuid',
            'tlp',
            'assigned',
            'state',
            'priority',
            'comments',
            'merged',
            'mergeable',
            'blocked',
            'evidence',
            'artifacts',
            'parent',
            'children',
            'events'
        ]


class CaseDocumentViewSet(DocumentViewSet):
    document = CaseDocument
    serializer_class = CaseDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]
    pagination_class = QueryFriendlyPageNumberPagination
    # Define search fields
    search_fields = (
        'report_message_id',
        'uuid',
        'tlp',
        'state',
        'priority',
        'assigned.username',
        'assigned.first_name',
        'assigned.last_name',
        'assigned.email',
        'comments.content',
        'evidence.filename',
        'artifacts.type',
        'artifacts.value',
        'parent.uuid',
        'children.uuid',
        'events.address'
        'events.feed'
        'events.reporter'
        'events.uuid'
    )
    filter_fields = {
        'id': {
            'field': 'id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
                LOOKUP_FILTER_TERMS,
            ],
        },
        'date': {
            'field': 'date',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
                LOOKUP_FILTER_TERMS,
            ],
        },
        'attend_date': {
            'field': 'attend_date',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
                LOOKUP_FILTER_TERMS,
            ],
        },
        'solve_date': {
            'field': 'solve_date',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
                LOOKUP_FILTER_TERMS,
            ],
        },
        'merged': 'merged',
        'mergeable': 'mergeable',
        'blocked': 'blocked',
        'lifecycle': 'lifecycle',
        'state': {
            'field': 'state',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_QUERY_ISNULL,
            ],
        },
        'priority': {
            'field': 'priority',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_QUERY_ISNULL,
            ],
        },
        'tlp': {
            'field': 'tlp',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_QUERY_ISNULL,
            ],
        },
        'uuid': {
            'field': 'uuid',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_QUERY_ISNULL,
            ],
        },
        'parent.uuid': {
            'field': 'parent.uuid',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_QUERY_ISNULL,
            ],
        },
        'children.uuid': {
            'field': 'children.uuid',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_FILTER_EXISTS,
            ],
        },
        'events.address': {
            'field': 'events.address',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_FILTER_EXISTS,
            ],
        },
        'events.feed': {
            'field': 'events.feed',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_FILTER_EXISTS,
            ],
        },
        'events.tlp': {
            'field': 'events.tlp',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_FILTER_EXISTS,
            ],
        },
        'events.priority': {
            'field': 'events.priority',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_FILTER_EXISTS,
            ],
        },
        'events.reporter': {
            'field': 'events.reporter',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_FILTER_EXISTS,
            ],
        },
    }
    ordering_fields = {
        'id': None,
        'tlp': None,
        'state': None,
        'priority': None,
    }
    ordering = 'id'

    multi_match_options = {
        'type': 'phrase',
    }
