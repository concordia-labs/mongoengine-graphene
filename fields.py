import graphene 
import json

from .base import logger
from . import BaseDocumentGraphene, DocumentGrapheneObject

class DocumentGrapheneField(BaseDocumentGraphene):
    """
        Converts a mongoengine Document to a graphene Field.
    """
    
    def _get_graphene_ref(self):
        """
            Returns the graphene object Field.
        """
        graphene_obj = DocumentGrapheneObject(self.document)

        props = graphene_obj.get_graphene_props(conversion_type="argument")

        return graphene.Field(graphene_obj.object, **props)

    def _get_graphene_resolver(self):
        """
            Returns a graphene resolver for the object property
        """
        kwargs_function = self.resolver_kwargs_function
        doc = self.document

        async def resolver(self, info, **kwargs):
            return doc.objects(**kwargs_function(self, info, **kwargs)).first()

        return resolver

class DocumentGrapheneList(BaseDocumentGraphene):
    """
        Converts a mongoengine Document to a graphene List.
    """

    custom_resolver = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'custom_resolver' in kwargs:
            self.custom_resolver = kwargs['custom_resolver']
    
    def _get_graphene_ref(self):
        """
            Returns the graphene object List.
        """

        graphene_obj = DocumentGrapheneObject(self.document)

        props = graphene_obj.get_graphene_props(conversion_type='argument')
        props.update({
            'limit': graphene.Int(),
            'offset': graphene.Int(),
        })

        return graphene.List(graphene_obj.object, **props)

    def _get_graphene_resolver(self):
        """
            Returns a graphene resolver for the object property
        """
        
        kwargs_function = self.resolver_kwargs_function
        doc_serializer  = self.serialize_document
        doc = self.document

        def default_resolver(self_, info, limit = 10, offset = 0,**kwargs):
            filter_ = self._parse_kwargs_function_result(kwargs_function(self_, info, **kwargs))
            
            queryset = doc.objects.filter(*filter_[0], **filter_[1])[offset:offset + limit]
            
            return [ doc_serializer(d) for d in queryset]

        if self.custom_resolver:
            default_resolver = self.custom_resolver

        def resolver(self, info, *args, **kwargs):
            try:
                return default_resolver(self, info, *args, **kwargs)
            except Exception as e:
                logger.error(' - '.join(['Resolver Error', str(e)]))

        return resolver
