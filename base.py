import mongoengine
import graphene
import re
import inspect
import json
import logging

from .conversion_dicts import field_conversion_dict, argument_conversion_dict

from datetime import datetime

logger = logging.getLogger()

existent_types = {}

class BaseDocumentGraphene:
    """
        Base graphene document converter.
    """
    document = None
    object = None
    resolver = None
    resolver_kwargs_function = None

    def __init__(self, mongoengine_doc, resolver_kwargs_function = lambda self, info, **kwargs: kwargs):
        self.document = mongoengine_doc
        self.resolver_kwargs_function = resolver_kwargs_function

        self.object = self._get_graphene_ref()

        self.resolver = self._get_graphene_resolver()

    def get_graphene_props(self, conversion_type="field"):
        """
            Returns the graphene ObjectType properties based on the mongoengine document fields.
        """
        logger.debug('{:25} - Get Graphene Props'.format(self.__class__.__name__))

        props = {
            '_id': graphene.String()
        }

        for prop_key in dir(self.document):
            try:
                prop = getattr(self.document, prop_key)
                prop_type = type(prop)


                if 'mongoengine.fields' in str(prop_type):
                    prop_type_str = re.match('<class \'(.*)\'>', str(prop_type))[1]
                    
                    conversion_dict = field_conversion_dict if conversion_type == 'field' else argument_conversion_dict

                    prop_converted = conversion_dict.get(prop_type_str, graphene.String)

                    prop_args = inspect.getfullargspec(prop_converted).args
                    if prop_type is mongoengine.fields.ListField:
                        if type(prop.field) is mongoengine.fields.ReferenceField:
                            # In case of reference field, the input list will be string to receive the objectId
                            props[prop_key] = graphene.List(graphene.String)
                        else:
                            props[prop_key] = self._parse_embedded_prop(prop_converted, prop.field.document_type, conversion_type)
                    elif prop_type is mongoengine.fields.EmbeddedDocumentListField:
                        props[prop_key] = self._parse_embedded_prop(prop_converted, prop.field.document_type, conversion_type)
                    elif len(prop_args) == 1:
                        props[prop_key] = prop_converted()
                    elif prop_args[1] == 'type' or prop_args[1] == 'of_type':
                        props[prop_key] = self._parse_embedded_prop(prop_converted, prop.document_type, conversion_type)
            except Exception as e:
                logger.error(e)
                pass
        return props

    def _get_graphene_ref(self):
        """
            Should return the desired graphene type.
        """
        return type('BaseDocumentGraphene', (graphene.ObjectType, ), {})

    def _get_graphene_resolver(self):
        """
            Should return the desired graphene type resolver.
        """
        def resolver(self, info, *args, **kwargs):
            return None

        return resolver

    def _parse_embedded_prop(self, prop, doc_type, conversion_type):
        if conversion_type == 'field':
            return prop(DocumentGrapheneObject(doc_type).object)
        else:
            return prop(DocumentGrapheneInputObject(doc_type).object)

    def serialize_document(self, doc):
        doc.select_related()
        doc_dict = doc._data
        return self.serialize_document_json(self.document, doc_dict)
    
    @classmethod
    def serialize_document_json(cls, document_type, doc_dict):
        for key, value in doc_dict.items():
            if value is None:
                continue

            if key == '_id': 
                doc_dict['_id'] = str(doc_dict['_id'])
                continue

            f_ = getattr(document_type, key)

            if type(f_) is mongoengine.fields.ListField and type(f_.field) is mongoengine.fields.ReferenceField:
                doc_dict[key] = [ cls.serialize_document_json(f_.field.document_type, i_._data) for i_ in value ]
            elif type(f_) is mongoengine.fields.EmbeddedDocumentField:
                doc_dict[key] = cls.serialize_document_json(f_.document_type, value._data)

        return doc_dict

class DocumentGrapheneObject(BaseDocumentGraphene):
    """
        Converts a mongoengine Document to a graphene ObjectType.
    """

    def _get_graphene_object_name(self):
        """
            Returns the graphene object name [mongoengine document name] + GrapheneObject
        """
        return self.document.__name__ + 'GrapheneObject'

    def _get_graphene_ref(self):
        """
            Returns the graphene object.
        """
        name  = self._get_graphene_object_name()

        if name in existent_types: return existent_types[name]

        props = self.get_graphene_props()    

        type_ = type(name, (graphene.ObjectType, ), props)

        existent_types[name] = type_

        return type_

class DocumentGrapheneInputObject(BaseDocumentGraphene):
    """
        Converts a mongoengine Document to a graphene InputObjectType.
    """

    def _get_graphene_object_name(self):
        """
            Returns the graphene object name [mongoengine document name] + GrapheneInputObject
        """
        return self.document.__name__ + 'GrapheneInputObject'

    def _get_graphene_ref(self):
        """
            Returns the graphene object.
        """
        name  = self._get_graphene_object_name()

        if name in existent_types: return existent_types[name]

        props = self.get_graphene_props('argument')    

        type_ = type(name, (graphene.InputObjectType, ), props)

        existent_types[name] = type_

        return type_