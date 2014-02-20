from __future__ import unicode_literals

from django.test.testcases import TestCase
from django.utils.unittest.case import skip
from positions.tests.lists.models import List, Item

@skip
class WithRespectToParentTestCase(TestCase):
    def setUp(self):
        self.list = List.objects.create(name='To Do')

    def assertItemsEqualsList(self, values):
        qs = self.list.items.values_list('name', 'position').order_by('position')
        return self.assertQuerysetEqual(qs, values, transform=tuple)

    def create_items(self, *names):
        for name in names:
            self.list.items.create(name=name)

    def test_creation(self):
        # create a couple items using the default position
        self.list.items.create(name='Write Tests')
        self.assertItemsEqualsList([('Write Tests', 0)])
        self.list.items.create(name='Excersize')
        self.assertItemsEqualsList([('Write Tests', 0), ('Excersize', 1)])
        self.list.items.create(name='Learn to spell Exercise', position=0)
        self.assertItemsEqualsList([('Learn to spell Exercise', 0), ('Write Tests', 1), ('Excersize', 2)])
        # save an item without changing it's position
        excersize = self.list.items.order_by('-position')[0]
        excersize.name = 'Exercise'
        excersize.save()
        self.assertItemsEqualsList([('Learn to spell Exercise', 0), ('Write Tests', 1), ('Exercise', 2)])

    def test_deletion(self):
        self.create_items('Learn to spell Exercise', 'Write Tests', 'Exercise')
        # delete an item
        learn_to_spell = self.list.items.order_by('position')[0]
        learn_to_spell.delete()
        self.assertItemsEqualsList([('Write Tests', 0), ('Exercise', 1)])
        # create a couple more items
        self.create_items('Drink less Coke', 'Go to Bed')
        self.assertItemsEqualsList([('Write Tests', 0), ('Exercise', 1), ('Drink less Coke', 2), ('Go to Bed', 3)])

    def test_moving(self):
        self.create_items('Write Tests', 'Exercise', 'Drink less Coke', 'Go to Bed')
        # move item to end using None
        write_tests = self.list.items.order_by('position')[0]
        write_tests.position = None
        write_tests.save()
        self.assertItemsEqualsList([('Exercise', 0), ('Drink less Coke', 1), ('Go to Bed', 2), ('Write Tests', 3)])
        # move item using negative index
        write_tests.position = -3
        write_tests.save()
        self.assertItemsEqualsList([('Exercise', 0), ('Write Tests', 1), ('Drink less Coke', 2), ('Go to Bed', 3)])
        # move item to position
        write_tests.position = 2
        write_tests.save()
        self.assertItemsEqualsList([('Exercise', 0), ('Drink less Coke', 1), ('Write Tests', 2), ('Go to Bed', 3)])
        # move item to beginning
        sleep = self.list.items.order_by('-position')[0]
        sleep.position = 0
        sleep.save()
        self.assertItemsEqualsList([('Go to Bed', 0), ('Exercise', 1), ('Drink less Coke', 2), ('Write Tests', 3)])

    def test_check_auto_now(self):
        # check auto_now updates
        self.create_items('Go to Bed', 'Exercise', 'Drink less Coke', 'Write Tests')
        sleep_updated, excersize_updated, eat_better_updated, write_tests_updated = [i.updated for i in self.list.items.order_by('position')]
        eat_better = self.list.items.order_by('-position')[1]
        eat_better.position = 1
        eat_better.save()
        todo_list = list(self.list.items.order_by('position'))
        self.assertEqual(sleep_updated, todo_list[0].updated)
        self.assertLess(eat_better_updated, todo_list[1].updated) # this item
        self.assertLess(excersize_updated, todo_list[2].updated)  # and this one was updated, other's not
        self.assertEqual(write_tests_updated, todo_list[3].updated)

    def test_create_item_using_negative_index_or_zero_index(self):
        # create an item using negative index
        # http://github.com/jpwatts/django-positions/issues/#issue/5
        self.create_items('Go to Bed', 'Drink less Coke', 'Exercise', 'Write Tests')
        fix_issue_5 = Item(list=self.list, name="Fix Issue #5")
        self.assertEqual(fix_issue_5.position, -1)
        fix_issue_5.position = -2
        self.assertEqual(fix_issue_5.position, -2)
        fix_issue_5.save()
        self.assertEqual(fix_issue_5.position, 3)
        self.assertItemsEqualsList([('Go to Bed', 0), ('Drink less Coke', 1), ('Exercise', 2), ('Fix Issue #5', 3), ('Write Tests', 4)])
        # Try again, now that the model has been saved.
        fix_issue_5.position = -2
        fix_issue_5.save()
        self.assertEqual(fix_issue_5.position, 3)
        self.assertItemsEqualsList([('Go to Bed', 0), ('Drink less Coke', 1), ('Exercise', 2), ('Fix Issue #5', 3), ('Write Tests', 4)])
        # create an item using with a position of zero
        #http://github.com/jpwatts/django-positions/issues#issue/7
        item0 = self.list.items.create(name="Fix Issue #7", position=0)
        self.assertEqual(item0.position, 0)
        self.assertItemsEqualsList([('Fix Issue #7', 0), ('Go to Bed', 1), ('Drink less Coke', 2), ('Exercise', 3), ('Fix Issue #5', 4), ('Write Tests', 5)])
