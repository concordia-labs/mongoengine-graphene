import graphene
import mongoengine

from .base import logger, existent_types, BaseDocumentGraphene
from .fields import DocumentGrapheneField

class DocumentCreateGrapheneMutation(BaseDocumentGraphene):

    def _get_arguments_class(self):
        props = self.get_graphene_props('argument')
        return type('Arguments', (), props)

    def _get_graphene_object_name(self):
        """
            Returns the graphene object name [mongoengine document name] + CreateGrapheneMutation
        """
        return self.document.__name__ + 'CreateGrapheneMutation'

    def _get_graphene_ref(self):
        """
            Returns the graphene Mutation object.
        """
        kwargs_function = self.resolver_kwargs_function
        doc = self.document
        name = self._get_graphene_object_name()

        if name in existent_types: return existent_types[name]

        def mutate(self, info, *args, **kwargs):
            result = None

            try:
                doc_ = doc(**kwargs_function(self, info, **kwargs))
                doc_.save()

                result = doc_._data            
            except Exception as e:
                logger.exception(e)

            return DocumentCreateGrapheneMutation(doc).object(document=result, ok=(result is not None))

        props = {
            'ok': graphene.Boolean(),
            'document': DocumentGrapheneField(self.document).object,
            'Arguments': self._get_arguments_class(),
            'mutate': mutate
        }

        type_ = type(name, (graphene.Mutation,), props)

        existent_types[name] = type_

        return type_

class DocumentUpdateGrapheneMutation(BaseDocumentGraphene):

    def _get_arguments_class(self):
        props = self.get_graphene_props('argument')
        props.update({
            'required': True,
        })
        return type('Arguments', (), {
            'filter': type(self.document.__name__ + 'UpdateMutationFilter', (graphene.InputObjectType,), props)(),
            'data': type(self.document.__name__ + 'UpdateMutationData', (graphene.InputObjectType,), props)()
        })

    def _get_graphene_object_name(self):
        """
            Returns the graphene object name [mongoengine document name] + UpdateGrapheneMutation
        """
        return self.document.__name__ + 'UpdateGrapheneMutation'

    def _get_graphene_ref(self):
        """
            Returns the graphene Mutation object.
        """
        kwargs_function = self.resolver_kwargs_function
        doc = self.document
        name = self._get_graphene_object_name()

        if name in existent_types: return existent_types[name]

        def mutate(self, info, filter, data, *args, **kwargs):
            result = None
                
            try:
                doc_ = doc.objects(**kwargs_function(self, info, **filter)).first()

                if doc_:
                    props = kwargs_function(self, info, **data)

                    for key, value in props.items():
                        f_ = getattr(doc, key)

                        if type(f_) is mongoengine.fields.ListField and type(f_.field) is mongoengine.fields.ReferenceField:
                            props[key] = [ d_.id for d_ in f_.field.document_type.objects(id__in=value)]

                    doc_.update(**props)

                result = doc_._data            
            except Exception as e:
                logger.exception(e)

            return DocumentCreateGrapheneMutation(doc).object(document=result, ok=(result is not None))

        props = {
            'ok': graphene.Boolean(),
            'document': DocumentGrapheneField(self.document).object,
            'Arguments': self._get_arguments_class(),
            'mutate': mutate
        }

        type_ = type(name, (graphene.Mutation,), props)

        existent_types[name] = type_

        return type_

class DocumentDeleteGrapheneMutation(BaseDocumentGraphene):

    def _get_arguments_class(self):
        return type('Arguments', (), {
            'id': graphene.String()
        })

    def _get_graphene_object_name(self):
        """
            Returns the graphene object name [mongoengine document name] + DeleteGrapheneMutation
        """
        return self.document.__name__ + 'DeleteGrapheneMutation'

    def _get_graphene_ref(self):
        """
            Returns the graphene Mutation object.
        """
        kwargs_function = self.resolver_kwargs_function
        doc = self.document
        name = self._get_graphene_object_name()

        if name in existent_types: return existent_types[name]

        def mutate(self, info, *args, **kwargs):
            result = None

            try:
                doc.objects(**kwargs_function(self, info, **kwargs)).delete()        
                result = True
            except Exception as e:
                logger.exception(e)

            return DocumentDeleteGrapheneMutation(doc).object(ok=(result is not None))

        props = {
            'ok': graphene.Boolean(),
            'Arguments': self._get_arguments_class(),
            'mutate': mutate
        }

        type_ = type(name, (graphene.Mutation,), props)

        existent_types[name] = type_

        return type_