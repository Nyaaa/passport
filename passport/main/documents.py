from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Order, Distributor


@registry.register_document
class OrderDocument(Document):
    distributor = fields.NestedField(properties={'name': fields.TextField()})
    recipient = fields.NestedField(properties={'name': fields.TextField()})
    city = fields.NestedField(properties={'name': fields.TextField()})

    class Index:
        name = 'orders'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Order
        fields = [
            'date',
            'document',
            # 'sets',
            'comment',
        ]
