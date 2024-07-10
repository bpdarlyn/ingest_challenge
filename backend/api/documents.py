from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields

from backend.helpers import elastic_search as elastic_search_helpers
from backend.api.models import Organization


INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES['documents.organization'])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=2,
    number_of_replicas=1
)


@INDEX.doc_type
class OrganizationDocument(Document):
    id = fields.IntegerField(attr='id')
    name = fields.TextField(
        analyzer=elastic_search_helpers.Analyzers.standard_analyzer,
        fields={
            'exact': fields.TextField(analyzer=elastic_search_helpers.Analyzers.exact_analyzer),
            'almost_exactly_analyzer': fields.TextField(analyzer=elastic_search_helpers.Analyzers.almost_exactly_analyzer),
        }
    )

    website = fields.TextField(
        analyzer=elastic_search_helpers.Analyzers.url_analyzer,
    )

    description = fields.TextField(
        analyzer=elastic_search_helpers.Analyzers.standard_analyzer,
        fields={
            'exact': fields.TextField(analyzer=elastic_search_helpers.Analyzers.exact_analyzer),
            'almost_exactly_analyzer': fields.TextField(
                analyzer=elastic_search_helpers.Analyzers.almost_exactly_analyzer),
        }
    )

    country = fields.TextField(
        attr='country_indexing',
        analyzer=elastic_search_helpers.Analyzers.standard_analyzer,
        fields={
            'almost_exactly_analyzer': fields.TextField(
                analyzer=elastic_search_helpers.Analyzers.almost_exactly_analyzer),
        }
    )

    industry = fields.TextField(
        attr='industry_indexing',
        analyzer=elastic_search_helpers.Analyzers.standard_analyzer,
        fields={
            'almost_exactly_analyzer': fields.TextField(
                analyzer=elastic_search_helpers.Analyzers.almost_exactly_analyzer),
        }
    )

    organization_id = fields.TextField(
        attr='publisher_indexing',
        analyzer='keyword',
    )

    year_founded = fields.IntegerField()
    number_of_employees = fields.IntegerField()

    class Django(object):
        """Inner nested class Django."""

        model = Organization
