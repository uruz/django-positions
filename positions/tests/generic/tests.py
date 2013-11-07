from __future__ import unicode_literals
from django.contrib.contenttypes.models import ContentType
from positions.tests.generic.models import GenericThing
from positions.tests.lists.models import List
from django.test import TestCase


class GenericTestCase(TestCase):
    def setUp(self):
        self.list = List.objects.create(name='To Do')
        self.ct = ContentType.objects.get_for_model(self.list)
        self.t1 = GenericThing.objects.create(name="First Generic Thing",
                                              object_id=self.list.pk,
                                              content_type=self.ct)
        self.t2 = GenericThing.objects.create(name="Second Generic Thing",
                                              object_id = self.list.pk,
                                              content_type = self.ct)
        
    def test_reposition_on_save(self):
        self.assertEqual(self.t1.position, 0)
        self.assertEqual(self.t2.position, 1)
        self.t1.position = 1
        self.t1.save()
        self.assertEqual(self.t1.position, 1)
        t2 = GenericThing.objects.get(pk=self.t2.pk)
        self.assertEqual(t2.position, 0)
    
    def test_reposition_on_delete(self):
        self.t1.position = 1
        self.t1.save()
        self.t1.delete()
        qs = GenericThing.objects.filter(object_id=self.list.pk, content_type=self.ct).values_list('name', 'position').order_by('position')
        self.assertQuerysetEqual(qs, [('Second Generic Thing', 0)], transform=tuple)
        t3 = GenericThing.objects.create(object_id=self.list.pk, content_type=self.ct, name='Mr. None')
        t3.save()
        self.assertEqual(t3.position, 1)
        t4 = GenericThing.objects.create(object_id=self.list.pk, content_type=self.ct, name='Mrs. None')
        self.assertEqual(t4.position, 2)
        t4.position = -2
        t4.save()
        self.assertEqual(t4.position, 1)
        qs = GenericThing.objects.order_by('position').values_list('name', flat=True)
        self.assertQuerysetEqual(qs, ['Second Generic Thing', 'Mrs. None', 'Mr. None'], transform=lambda x:x)
