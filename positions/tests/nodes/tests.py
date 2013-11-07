from __future__ import unicode_literals
from django.test import TestCase
from positions.tests.nodes.models import Node
from functools import partial

class NodesTestCase(TestCase):

    def setUp(self):
        """
        Creates a simple tree::

            parent1
                child2
                child1
                child3
            parent2
                child4
                child5
                child6
        """
        self.parent1 = Node.objects.create(name='Parent 1')
        self.parent2 = Node.objects.create(name='Parent 2')
        self.child1 = self.parent1.children.create(name='Child 1')
        self.child2 = self.parent1.children.create(name='Child 2')
        self.child3 = self.parent1.children.create(name='Child 3')
        self.child2.position = 0
        self.child2.save()
        self.child1 = Node.objects.get(pk=self.child1.pk)
        self.child2 = Node.objects.get(pk=self.child2.pk)
        self.child3 = Node.objects.get(pk=self.child3.pk)

        self.child4 = self.parent2.children.create(name='Child 4')
        self.child5 = self.parent2.children.create(name='Child 5')
        self.child6 = self.parent2.children.create(name='Child 6')

    def test_structure(self):
        """
        Tests the tree structure
        """
        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 1', 0), ('Parent 2', 1), ('Child 2', 0), ('Child 1', 1), ('Child 3', 2), ('Child 4', 0), ('Child 5', 1), ('Child 6', 2)])

    def test_collection_field_change_sibling_position(self):
        """
        Set child6 as the first sibling in its branch.
        """
        self.child6.position = 0
        self.child6.save()

        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 1', 0), ('Parent 2', 1), ('Child 2', 0), ('Child 1', 1), ('Child 3', 2), ('Child 6', 0), ('Child 4', 1), ('Child 5', 2)])

    def test_collection_field_change_first_child(self):
        """
        Move child2 to make it the first child of parent2
        """
        self.child2.position = 0
        self.child2.parent = Node.objects.get(pk=self.parent2.pk)
        self.child2.save()

        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 1', 0), ('Parent 2', 1), ('Child 1', 0), ('Child 3', 1), ('Child 2', 0), ('Child 4', 1), ('Child 5', 2), ('Child 6', 3)])

    def test_collection_field_change_last_child(self):
        """
        Move child2 to make it the last child of parent2
        """

        self.child2.position = -1
        self.child2.parent = Node.objects.get(pk=self.parent2.pk)
        self.child2.save()

        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 1', 0), ('Parent 2', 1), ('Child 1', 0), ('Child 3', 1), ('Child 4', 0), ('Child 5', 1), ('Child 6', 2), ('Child 2', 3)])

    def test_collection_field_change_sibling_1(self):
        """
        Move child2 to make it the next sibling of child4
        """

        self.child2.position = 1
        self.child2.parent = Node.objects.get(pk=self.parent2.pk)
        self.child2.save()

        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 1', 0), ('Parent 2', 1), ('Child 1', 0), ('Child 3', 1), ('Child 4', 0), ('Child 2', 1), ('Child 5', 2), ('Child 6', 3)])

    def test_collection_field_change_sibling_2(self):
        """
        Move child2 to make it the next sibling of child5
        """

        self.child2.position = 2
        self.child2.parent = Node.objects.get(pk=self.parent2.pk)
        self.child2.save()

        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 1', 0), ('Parent 2', 1), ('Child 1', 0), ('Child 3', 1), ('Child 4', 0), ('Child 5', 1), ('Child 2', 2), ('Child 6', 3)])

    def test_collection_field_change_sibling_3(self):
        """
        Move child2 to make it the next sibling of child6 (last child)
        """

        self.child2.position = 3
        self.child2.parent = Node.objects.get(pk=self.parent2.pk)
        self.child2.save()

        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 1', 0), ('Parent 2', 1), ('Child 1', 0), ('Child 3', 1), ('Child 4', 0), ('Child 5', 1), ('Child 6', 2), ('Child 2', 3)])

    def test_deletion_1(self):
        """
        Delete child2
        """
        self.child2.delete()
        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 1', 0), ('Parent 2', 1), ('Child 1', 0), ('Child 3', 1), ('Child 4', 0), ('Child 5', 1), ('Child 6', 2)])

    def test_deletion_2(self):
        """
        Delete child3
        """
        self.child3.delete()
        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 1', 0), ('Parent 2', 1), ('Child 2', 0), ('Child 1', 1), ('Child 4', 0), ('Child 5', 1), ('Child 6', 2)])

    def test_deletion_3(self):
        """
        Delete child1
        """
        self.child1.delete()
        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 1', 0), ('Parent 2', 1), ('Child 2', 0), ('Child 3', 1), ('Child 4', 0), ('Child 5', 1), ('Child 6', 2)])

    def test_deletion_4(self):
        """
        Delete parent1
        """
        self.parent1.delete()
        tree = list(Node.objects.order_by('parent__position', 'position').values_list('name', 'position'))
        self.assertEqual(tree, [('Parent 2', 0), ('Child 4', 0), ('Child 5', 1), ('Child 6', 2)])

class NodesTestCase2(TestCase):
    def assertQuerysetEqual(self, qs, values, transform=tuple, ordered=True):
        '''assertQuerysetEqual with transform default changed from `repr` to `tuple`''' 
        return super(NodesTestCase2, self).assertQuerysetEqual(qs, values, transform, ordered)
    
    def test_nodes(self):
        # create some parent nodes
        Node.objects.create(name='Parent 1')
        qs = Node.objects.order_by('position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 1', 0)])
        Node.objects.create(name='Parent 2')
        qs = Node.objects.order_by('position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 1', 0), ('Parent 2', 1)])
        parent3 = Node.objects.create(name='Parent 3', position=0)
        qs = Node.objects.order_by('position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 3', 0), ('Parent 1', 1), ('Parent 2', 2)])
        parent3.position = 999
        parent3.save()
        qs = Node.objects.order_by('position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 1', 0), ('Parent 2', 1), ('Parent 3', 2)])
        parent3.position = -2
        parent3.save()
        qs = Node.objects.order_by('position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 1', 0), ('Parent 3', 1), ('Parent 2', 2)])
        parent3.delete()
        qs = Node.objects.order_by('position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 1', 0), ('Parent 2', 1)])
        # create some children
        parent1 = Node.objects.order_by('position')[0]
        parent1.children.create(name='Child 1')
        qs = Node.objects.order_by('parent__position', 'position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 1', 0), ('Parent 2', 1), ('Child 1', 0)])
        child2 = parent1.children.create(name='Child 2')
        qs = Node.objects.order_by('parent__position', 'position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 1', 0), ('Parent 2', 1), ('Child 1', 0), ('Child 2', 1)])
        child2.position = 0
        child2.save()
        qs = Node.objects.order_by('parent__position', 'position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 1', 0), ('Parent 2', 1), ('Child 2', 0), ('Child 1', 1)])
        parent2 = Node.objects.filter(parent__isnull=True).order_by('position')[1]
        self.assertEqual(parent2.name, 'Parent 2')
        
        parent1.children.create(name='Child 3')
        parent2.children.create(name='Child 4')
        parent2.children.create(name='Child 5')
        parent2.children.create(name='Child 6')
        qs = Node.objects.order_by('parent__position', 'position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 1', 0), ('Parent 2', 1), ('Child 2', 0), ('Child 1', 1), ('Child 3', 2), ('Child 4', 0), ('Child 5', 1), ('Child 6', 2)])
        #Move nodes around
        child2 = Node.objects.get(pk=child2.pk)
        child2.position = 0
        child2.parent = Node.objects.get(pk=parent2.pk)
        setattr(child2, "_debug", True)
        child2.save()
        qs = Node.objects.order_by('parent__position', 'position').values_list('name', 'position')
        self.assertQuerysetEqual(qs, [('Parent 1', 0), ('Parent 2', 1), ('Child 1', 0), ('Child 3', 1), ('Child 2', 0), ('Child 4', 1), ('Child 5', 2), ('Child 6', 3)])
        
