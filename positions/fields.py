import datetime
import warnings

from django.db import models
from django.db.models.signals import post_delete, post_save


try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.datetime.now

# define basestring for python 3
try:
    basestring
except NameError:
    basestring = (str, bytes)


class Position(object):
    END = -1

    def __init__(self, position):
        self.position = position
        if position is None:
            position = self.END
        elif isinstance(position, int):
            if position < Position.END:
                raise Exception('It is not allowed to specify values less than -1')
        else:
            raise Exception('Position should be either integer or None')

    @property
    def is_end(self):
        return self.position == self.END

    @is_end.setter
    def set_is_end(self, value):
        self.position = self.END


class FMax(object):
    def __init__(self, queryset, fieldname):
        self.queryset = queryset
        self.fieldname = fieldname

    def as_sql(self, qs, connection):
        queryset = self.queryset.exclude(position = Position.END).select_for_update().values_list(self.fieldname)
        sql = str(queryset.query)
        return '(SELECT COUNT(*) FROM ({sql}) as aliased)'.format(sql=sql), ()


class PositionField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, default=-1, collection=None, parent_link=None, unique_for_field=None, unique_for_fields=None, *args, **kwargs):
        if 'unique' in kwargs:
            raise TypeError("%s can't have a unique constraint." % self.__class__.__name__)
        super(PositionField, self).__init__(verbose_name, name, default=default, *args, **kwargs)

        # Backwards-compatibility mess begins here.
        if collection is not None and unique_for_field is not None:
            raise TypeError("'collection' and 'unique_for_field' are incompatible arguments.")

        if collection is not None and unique_for_fields is not None:
            raise TypeError("'collection' and 'unique_for_fields' are incompatible arguments.")

        if unique_for_field is not None:
            warnings.warn("The 'unique_for_field' argument is deprecated.  Please use 'collection' instead.", DeprecationWarning)
            if unique_for_fields is not None:
                raise TypeError("'unique_for_field' and 'unique_for_fields' are incompatible arguments.")
            collection = unique_for_field

        if unique_for_fields is not None:
            warnings.warn("The 'unique_for_fields' argument is deprecated.  Please use 'collection' instead.", DeprecationWarning)
            collection = unique_for_fields
        # Backwards-compatibility mess ends here.

        if isinstance(collection, basestring):
            collection = (collection,)
        self.collection = collection
        self.parent_link = parent_link

    def contribute_to_class(self, cls, name):
        super(PositionField, self).contribute_to_class(cls, name)
        for constraint in cls._meta.unique_together:
            if self.name in constraint:
                raise TypeError("%s can't be part of a unique constraint." % self.__class__.__name__)
        self.auto_now_fields = []
        for field in cls._meta.fields:
            if getattr(field, 'auto_now', False):
                self.auto_now_fields.append(field)
        setattr(cls, self.name, self)
        post_delete.connect(self.update_on_delete, sender=cls)
        post_save.connect(self.update_on_save, sender=cls)

    def get_prep_value(self, value):
        '''Integer field used to do int(value). We don't need this as we has FMax class'''
        if value is None:
            return None
        return value

    def pre_save(self, model_instance, add):
        #NOTE: check if the node has been moved to another collection; if it has, delete it from the old collection.
        previous_instance = None
        collection_changed = False
        if not add and self.collection is not None:
            previous_instance = type(model_instance)._default_manager.get(pk=model_instance.pk)
            for field_name in self.collection:
                field = model_instance._meta.get_field(field_name)
                current_field_value = getattr(model_instance, field.attname)
                previous_field_value = getattr(previous_instance, field.attname)
                if previous_field_value != current_field_value:
                    collection_changed = True
                    break
        if not collection_changed:
            previous_instance = None

        if collection_changed:
            self.remove_from_collection(previous_instance)

        cache_name = self.get_cache_name()
        current, updated, _ = getattr(model_instance, cache_name)

        if collection_changed:
            current = None

        if add:
            if updated is None:
                updated = Position(Position.END)
            current = None
        elif updated is None:
            updated = -1

        # existing instance, position not modified; no cleanup required
        if current is not None and updated is None:
            return current

        collection_count = self.get_collection(model_instance).count()
        if current is None:
            max_position = collection_count
        else:
            max_position = collection_count - 1
        min_position = 0

        # new instance; appended; cleanup required on post_save
        if add:
            if updated.position >= max_position: #fragile check
                updated.is_end = True
            position = updated.position # may return -1
        else:
            if max_position >= updated.position >= min_position:
                # positive position; valid index
                position = updated.position
            elif updated.position > max_position:
                # positive position; invalid index
                position = Position.END
            elif abs(updated.position) <= (max_position + 1):
                # Impossible case, as I've prohibited that (for now)
                # negative position; valid index

                # Add 1 to max_position to make this behave like a negative list index.
                # -1 means the last position, not the last position minus 1

                position = max_position + 1 + updated.position
            else:
                # negative position; invalid index
                position = min_position

        # instance inserted; cleanup required on post_save
        setattr(model_instance, cache_name, (current, position, collection_changed))
        return position

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError("%s must be accessed via instance." % self.name)
        current, updated, _ = getattr(instance, self.get_cache_name())
        return current if updated is None else updated

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("%s must be accessed via instance." % self.name)
        if value is None:
            value = self.default
        cache_name = self.get_cache_name()
        try:
            current, updated, collection_changed = getattr(instance, cache_name)
        except AttributeError:
            current, updated, collection_changed = value, None, False
        else:
            if not isinstance(value, Position) or value is not None:
                value = Position(value)
            updated = value
        setattr(instance, cache_name, (current, updated, collection_changed))

    def get_collection(self, instance):
        filters = {}
        if self.collection is not None:
            for field_name in self.collection:
                field = instance._meta.get_field(field_name)
                field_value = getattr(instance, field.attname)
                if field.null and field_value is None:
                    filters['%s__isnull' % field.name] = True
                else:
                    filters[field.name] = field_value
        model = type(instance)
        parent_link = self.parent_link
        if parent_link is not None:
            model = model._meta.get_field(parent_link).rel.to
        return model._default_manager.filter(**filters)

    def remove_from_collection(self, instance):
        """
        Removes a positioned item from the collection.
        """
        queryset = self.get_collection(instance)
        current = getattr(instance, self.get_cache_name())[0]
        updates = {self.name: models.F(self.name) - 1}
        if self.auto_now_fields:
            right_now = now()
            for field in self.auto_now_fields:
                updates[field.name] = right_now
        queryset.filter(**{'%s__gt' % self.name: current}).update(**updates)

    def update_on_delete(self, sender, instance, **kwargs):
        queryset = self.get_collection(instance)
        current = getattr(instance, self.get_cache_name())[0]
        updates = {self.name: models.F(self.name) - 1}
        if self.auto_now_fields:
            right_now = now()
            for field in self.auto_now_fields:
                updates[field.name] = right_now
        queryset.filter(**{'%s__gt' % self.name: current}).update(**updates)

    def update_on_save(self, sender, instance, created, **kwargs):
        current, updated, collection_changed = getattr(instance, self.get_cache_name())

        if updated is None and not collection_changed and current != Position.END:
            return

        queryset = self.get_collection(instance).exclude(pk=instance.pk)

        updates = {}
        if self.auto_now_fields:
            right_now = now()
            for field in self.auto_now_fields:
                updates[field.name] = right_now

        if updated is None and created:
            updated = -1

        if created or collection_changed:
            if (current == Position.END and updated is None) or updated == Position.END:
                # position should be at the end
                self.model._default_manager.filter(pk = instance.pk).update(**{self.name: FMax(queryset, self.name)})
            else:
                # increment positions gte updated or node moved from another collection
                queryset = queryset.filter(**{'%s__gte' % self.name: updated})
                updates[self.name] = models.F(self.name) + 1
        elif updated > current:
            # decrement positions gt current and lte updated
            queryset = queryset.filter(**{'%s__gt' % self.name: current, '%s__lte' % self.name: updated})
            updates[self.name] = models.F(self.name) - 1
        else:
            # increment positions lt current and gte updated
            queryset = queryset.filter(**{'%s__lt' % self.name: current, '%s__gte' % self.name: updated})
            updates[self.name] = models.F(self.name) + 1

        queryset.update(**updates)
        updated = getattr(self.model._default_manager.get(pk = instance.pk), self.name)
        setattr(instance, self.get_cache_name(), (updated, None, collection_changed))

    def south_field_triple(self):
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.IntegerField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
