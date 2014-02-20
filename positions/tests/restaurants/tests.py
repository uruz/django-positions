from django.db import models
from django.test import TestCase
from django.utils.unittest.case import skip
from positions.tests.restaurants.models import Menu, Food, Drink


@skip
class ModelInheritanceTestCase(TestCase):

    def test_model_inheritance(self):
        romanos = Menu.objects.create(name="Romano's Pizza")
        pizza = Food.objects.create(menu=romanos, name="Pepperoni")
        self.assertEqual(pizza.position, 0)
        wine = Drink.objects.create(menu=romanos, name="Merlot")
        self.assertEqual(wine.position, 0)
        spaghetti = Food.objects.create(menu=romanos, name="Spaghetti & Meatballs")
        self.assertEqual(spaghetti.position, 1)
        soda = Drink.objects.create(menu=romanos, name="Coca-Cola")
        self.assertEqual(soda.position, 1)
