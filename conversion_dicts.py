import graphene

field_conversion_dict = {
    'mongoengine.fields.BinaryField': None,
    'mongoengine.fields.BooleanField': graphene.Boolean,
    'mongoengine.fields.CachedReferenceField': None,
    'mongoengine.fields.ComplexDateTimeField': None,
    'mongoengine.fields.DateField': graphene.String,
    'mongoengine.fields.DateTimeField': graphene.String,
    'mongoengine.fields.DecimalField': None,
    'mongoengine.fields.DictField': None,
    'mongoengine.fields.DynamicField': None,
    'mongoengine.fields.EmailField': graphene.String,
    'mongoengine.fields.EmbeddedDocumentField': graphene.Field,
    'mongoengine.fields.EmbeddedDocumentListField': graphene.List,
    'mongoengine.fields.FieldDoesNotExist': None,
    'mongoengine.fields.FileField': None,
    'mongoengine.fields.FloatField': graphene.Float,
    'mongoengine.fields.GenericEmbeddedDocumentField': None,
    'mongoengine.fields.GenericLazyReferenceField': None,
    'mongoengine.fields.GenericReferenceField': None,
    'mongoengine.fields.GeoJsonBaseField': None,
    'mongoengine.fields.GeoPointField': None,
    'mongoengine.fields.ImageField': None,
    'mongoengine.fields.IntField': graphene.Int,
    'mongoengine.fields.LazyReferenceField': graphene.Field,
    'mongoengine.fields.LineStringField': None,
    'mongoengine.fields.ListField': graphene.List,
    'mongoengine.fields.LongField': None,
    'mongoengine.fields.MapField': None,
    'mongoengine.fields.MultiLineStringField': None,
    'mongoengine.fields.MultiPointField': None,
    'mongoengine.fields.MultiPolygonField': None,
    'mongoengine.fields.ObjectIdField': None,
    'mongoengine.fields.PointField': None,
    'mongoengine.fields.PolygonField': None,
    'mongoengine.fields.QueryFieldList': None,
    'mongoengine.fields.ReferenceField': graphene.Field,
    'mongoengine.fields.SequenceField': None,
    'mongoengine.fields.SortedListField': graphene.List,
    'mongoengine.fields.StringField': graphene.String,
    'mongoengine.fields.URLField': graphene.String,
    'mongoengine.fields.UUIDField': graphene.String,
}

argument_conversion_dict = {
    'mongoengine.fields.BinaryField': None,
    'mongoengine.fields.BooleanField': graphene.Boolean,
    'mongoengine.fields.CachedReferenceField': None,
    'mongoengine.fields.ComplexDateTimeField': None,
    'mongoengine.fields.DateField': graphene.String,
    'mongoengine.fields.DateTimeField': graphene.String,
    'mongoengine.fields.DecimalField': None,
    'mongoengine.fields.DictField': None,
    'mongoengine.fields.DynamicField': None,
    'mongoengine.fields.EmailField': graphene.String,
    'mongoengine.fields.EmbeddedDocumentField': graphene.Argument,
    'mongoengine.fields.EmbeddedDocumentListField': graphene.List,
    'mongoengine.fields.FieldDoesNotExist': None,
    'mongoengine.fields.FileField': None,
    'mongoengine.fields.FloatField': graphene.Float,
    'mongoengine.fields.GenericEmbeddedDocumentField': None,
    'mongoengine.fields.GenericLazyReferenceField': None,
    'mongoengine.fields.GenericReferenceField': None,
    'mongoengine.fields.GeoJsonBaseField': None,
    'mongoengine.fields.GeoPointField': None,
    'mongoengine.fields.ImageField': None,
    'mongoengine.fields.IntField': graphene.Int,
    'mongoengine.fields.LazyReferenceField': graphene.Argument,
    'mongoengine.fields.LineStringField': None,
    'mongoengine.fields.ListField': graphene.List,
    'mongoengine.fields.LongField': None,
    'mongoengine.fields.MapField': None,
    'mongoengine.fields.MultiLineStringField': None,
    'mongoengine.fields.MultiPointField': None,
    'mongoengine.fields.MultiPolygonField': None,
    'mongoengine.fields.ObjectIdField': None,
    'mongoengine.fields.PointField': None,
    'mongoengine.fields.PolygonField': None,
    'mongoengine.fields.QueryFieldList': None,
    'mongoengine.fields.ReferenceField': graphene.Argument,
    'mongoengine.fields.SequenceField': None,
    'mongoengine.fields.SortedListField': graphene.List,
    'mongoengine.fields.StringField': graphene.String,
    'mongoengine.fields.URLField': graphene.String,
    'mongoengine.fields.UUIDField': graphene.String,
}
