from __future__ import unicode_literals
from positions.tests.store.models import Product, Category, ProductCategory
from django.test import TestCase

class CollectionTestCase(TestCase):
    def setUp(self):
        clothes = Category.objects.create(name="Clothes")
        sporting_goods = Category.objects.create(name="Sporting Goods")
        bat = Product.objects.create(name="Bat")
        bat_in_sporting_goods = ProductCategory.objects.create(product=bat, category=sporting_goods)
        self.cap = Product.objects.create(name="Cap")
        self.cap_in_sporting_goods = ProductCategory.objects.create(product=self.cap, category=sporting_goods)
        cap_in_clothes = ProductCategory.objects.create(product=self.cap, category=clothes)
        glove = Product.objects.create(name="Glove")
        glove_in_sporting_goods = ProductCategory.objects.create(product=glove, category=sporting_goods)
        tshirt = Product.objects.create(name="T-shirt")
        tshirt_in_clothes = ProductCategory.objects.create(product=tshirt, category=clothes)
        jeans = Product.objects.create(name="Jeans")
        jeans_in_clothes = ProductCategory.objects.create(product=jeans, category=clothes)
        jersey = Product.objects.create(name="Jersey")
        jersey_in_sporting_goods = ProductCategory.objects.create(product=jersey, category=sporting_goods)
        jersey_in_clothes = ProductCategory.objects.create(product=jersey, category=clothes)
        ball = Product.objects.create(name="Ball")
        ball_in_sporting_goods = ProductCategory.objects.create(product=ball, category=sporting_goods)
        self.clothes = clothes
        self.sporting_goods = sporting_goods      
    
    def test_collections(self):
        qs = ProductCategory.objects.filter(category=self.clothes).values_list('product__name', 'position').order_by('position')
        self.assertQuerysetEqual(qs, [('Cap', 0), ('T-shirt', 1), ('Jeans', 2), ('Jersey', 3)], transform=tuple)
        qs = ProductCategory.objects.filter(category=self.sporting_goods).values_list('product__name', 'position').order_by('position')
        self.assertQuerysetEqual(qs, [('Bat', 0), ('Cap', 1), ('Glove', 2), ('Jersey', 3), ('Ball', 4)], transform=tuple)
        #Moving cap in sporting goods shouldn't effect its position in clothes.
        self.cap_in_sporting_goods.position = -1
        self.cap_in_sporting_goods.save()
        qs = ProductCategory.objects.filter(category=self.clothes).values_list('product__name', 'position').order_by('position')
        self.assertQuerysetEqual(qs, [('Cap', 0), ('T-shirt', 1), ('Jeans', 2), ('Jersey', 3)], transform=tuple)
        qs = ProductCategory.objects.filter(category=self.sporting_goods).values_list('product__name', 'position').order_by('position')
        self.assertQuerysetEqual(qs, [('Bat', 0), ('Glove', 1), ('Jersey', 2), ('Ball', 3), ('Cap', 4)], transform=tuple)
        # Deleting an object should reorder both collections.
        self.cap.delete()
        qs = ProductCategory.objects.filter(category=self.clothes).values_list('product__name', 'position').order_by('position')
        self.assertQuerysetEqual(qs, [('T-shirt', 0), ('Jeans', 1), ('Jersey', 2)], transform=tuple)
        qs = ProductCategory.objects.filter(category=self.sporting_goods).values_list('product__name', 'position').order_by('position')
        self.assertQuerysetEqual(qs, [('Bat', 0), ('Glove', 1), ('Jersey', 2), ('Ball', 3)], transform=tuple)
