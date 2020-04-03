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
    extra_kwargs = []
    resolver_kwargs_function = None
    mutation_kwargs_function = None

    def __init__(self, mongoengine_doc, extra_kwargs = [], resolver_kwargs_function = lambda self, info, **kwargs: kwargs, mutation_kwargs_function = lambda self, info, **kwargs: kwargs, *args, **kwargs):
        self.document = mongoengine_doc

        self.extra_kwargs = extra_kwargs

        self.resolver_kwargs_function = resolver_kwargs_function
        self.mutation_kwargs_function = mutation_kwargs_function

        self.object = self._get_graphene_ref()

        self.resolver = self._get_graphene_resolver()

    def get_graphene_props(self, conversion_type="field"):
        """
            Returns the graphene ObjectType properties based on the mongoengine document fields.
        """
        # logger.spam('{:25} - Get Graphene Props'.format(self.__class__.__name__))

        props = {
            'id': graphene.String()
        }

        for arg in self.extra_kwargs:
            key = arg[0]
            type_ = arg[1] if len(arg) > 1 else graphene.String()
            resolver = arg[2] if len(arg) > 2 else None

            props.update([(key, type_(),)])

            if conversion_type =='field' and resolver:
                props.update([('resolve_' + key, resolver,)])

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
                            if conversion_type == 'field':
                                props[prop_key] = graphene.List(DocumentGrapheneObject(prop.field.document_type).object)
                            else:
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

    def _parse_kwargs_function_result(self, result):
        filter_args = tuple()
        filter_kwargs = {}

        if type(result) is tuple or type(result) is list:
            filter_args = result
        elif type(result) is mongoengine.queryset.visitor.QCombination:
            filter_args = [result]
        elif type(result) is dict:
            filter_kwargs = result

        return filter_args, filter_kwargs

    def serialize_document(self, doc):
        doc.select_related()
        doc_dict = doc._data
        return self.serialize_document_json(self.document, doc_dict)
    
    @classmethod
    def serialize_document_json(cls, document_type, doc_dict):
        for key, value in doc_dict.items():
            if value is None or key == 'id' or key == '_id':
                if key == '_id':
                    doc_dict['id'] = doc_dict.pop('_id')
                continue

            f_ = getattr(document_type, key)

            if type(f_) is mongoengine.ListField\
                or type(f_) is mongoengine.EmbeddedDocumentListField:
                if type(f_.field) is mongoengine.ReferenceField\
                    or type(f_.field) is mongoengine.EmbeddedDocumentField:
                    doc_dict[key] = [ cls.serialize_document_json(f_.field.document_type, i_._data) for i_ in value ]
            elif type(f_) is mongoengine.ReferenceField\
                or type(f_) is mongoengine.EmbeddedDocumentField:
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
