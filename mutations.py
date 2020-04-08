import graphene
import mongoengine

from .base import logger, existent_types, BaseDocumentGraphene
from .fields import DocumentGrapheneField

class BaseDocumentGrapheneMutation(BaseDocumentGraphene):
    post_mutate = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'post_mutate' in kwargs:
            self.post_mutate = kwargs['post_mutate']

class DocumentCreateGrapheneMutation(BaseDocumentGrapheneMutation):

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
        kwargs_function = self.mutation_kwargs_function
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

            if result is not None and self.post_mutate is not None:
                self.post_mutate(self_, info, result, *args, **kwargs)

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

class DocumentUpdateGrapheneMutation(BaseDocumentGrapheneMutation):

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
        name = self._get_graphene_object_name()

        if name in existent_types: return existent_types[name]

        def mutate(self_, info, filter, data, *args, **kwargs):
            result = None
            doc_ = None
                
            try:
                doc_ = self.document.objects.filter(**self.resolver_kwargs_function(self_, info, **filter)).first()

                if doc_:
                    props = self.mutation_kwargs_function(self_, info, **data)

                    for key, value in props.items():
                        if value is None:
                            props[key] = None
                            continue
                        
                        f_ = getattr(self.document, key)

                        if type(f_) is mongoengine.fields.ListField and type(f_.field) is mongoengine.fields.ReferenceField:
                            props[key] = [ d_.id for d_ in f_.field.document_type.objects(id__in=value)]

                    doc_.update(**props)

                result = doc_._data            
            except Exception as e:
                logger.exception(e)

            if result is not None and self.post_mutate is not None:
                self.post_mutate(self_, info, filter, data, result, document=doc_, *args, **kwargs)

            return DocumentCreateGrapheneMutation(self.document).object(document=result, ok=(result is not None))

        props = {
            'ok': graphene.Boolean(),
            'document': DocumentGrapheneField(self.document).object,
            'Arguments': self._get_arguments_class(),
            'mutate': mutate
        }

        type_ = type(name, (graphene.Mutation,), props)

        existent_types[name] = type_

        return type_

class DocumentDeleteGrapheneMutation(BaseDocumentGrapheneMutation):

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
        name = self._get_graphene_object_name()

        if name in existent_types: return existent_types[name]

        def mutate(self_, info, *args, **kwargs):
            result = None

            try:
                self.document.objects(**self.resolver_kwargs_function(self_, info, **kwargs)).delete()        
                result = True
            except Exception as e:
                logger.exception(e)

            if result is not None and self.post_mutate is not None:
                self.post_mutate(self_, info, result, *args, **kwargs)

            return DocumentDeleteGrapheneMutation(self.document).object(ok=(result is not None))

        props = {
            'ok': graphene.Boolean(),
            'Arguments': self._get_arguments_class(),
            'mutate': mutate
        }

        type_ = type(name, (graphene.Mutation,), props)

        existent_types[name] = type_

        return type_