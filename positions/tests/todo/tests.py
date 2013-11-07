from __future__ import unicode_literals
from django.test import TestCase
from positions.tests.todo.models import Item

class PositionManagerTestCase(TestCase):
    def test_repositioning(self):
        self.assertEqual(Item.objects.position_field_name, 'index')
        self.assertEqual(Item.objects.all().position_field_name, 'index')
        Item.objects.create(description="Add a `reposition` method")
        Item.objects.create(description="Write some tests")
        Item.objects.create(description="Push to GitHub")
        qs = Item.objects.order_by('index').values_list('description', flat=True)
        self.assertQuerysetEqual(qs, ['Add a `reposition` method', 'Write some tests', 'Push to GitHub'], transform=lambda x:x)
        alphabetized = Item.objects.order_by('description')
        self.assertQuerysetEqual(alphabetized.values_list('description', flat=True), ['Add a `reposition` method', 'Push to GitHub', 'Write some tests'], transform=lambda x:x)
        self.assertEqual(alphabetized.position_field_name, 'index')
        repositioned = alphabetized.reposition(save=False)
        self.assertQuerysetEqual(repositioned, ['Add a `reposition` method', 'Push to GitHub', 'Write some tests'], transform=lambda x:x.description)
        
        # Make sure the position wasn't saved
        qs = Item.objects.order_by('index')
        self.assertQuerysetEqual(qs, ['Add a `reposition` method', 'Write some tests', 'Push to GitHub'], transform=lambda x:x.description)
        repositioned = alphabetized.reposition()
        self.assertQuerysetEqual(repositioned, ['Add a `reposition` method', 'Push to GitHub', 'Write some tests'], transform=lambda x:x.description)
        qs = Item.objects.order_by('index')
        self.assertQuerysetEqual(repositioned, ['Add a `reposition` method', 'Push to GitHub', 'Write some tests'], transform=lambda x:x.description)
        
    def test_moving(self):
        Item.objects.create(description="Add a `reposition` method")
        Item.objects.create(description="Push to GitHub")
        Item.objects.create(description="Write some tests")
        item = Item.objects.order_by('index')[0]
        self.assertEqual(item.description, "Add a `reposition` method")
        self.assertEqual(item.index, 0)
        item.index = -1
        item.save()
        
        # Make sure the signals are still connected
        qs = Item.objects.order_by('index')
        self.assertQuerysetEqual(qs, ['Push to GitHub', 'Write some tests', 'Add a `reposition` method'], transform=lambda x:x.description)
        self.assertEqual([i.index for i in Item.objects.order_by('index')], [0, 1, 2])
        
    def test_zeroposition(self):
        Item.objects.create(description="Push to GitHub")
        Item.objects.create(description="Write some tests")
        Item.objects.create(description="Add a `reposition` method")
        # Add an item at position zero
        # http://github.com/jpwatts/django-positions/issues/#issue/7
        item0 = Item(description="Fix Issue #7")
        item0.index = 0
        item0.save()
        qs = Item.objects.values_list('description', 'index').order_by('index')
        self.assertQuerysetEqual(qs, [('Fix Issue #7', 0), ('Push to GitHub', 1), ('Write some tests', 2), ('Add a `reposition` method', 3)], transform=tuple)
