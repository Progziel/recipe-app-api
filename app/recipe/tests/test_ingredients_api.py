"""
Tests for the Ingredients APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='user@example.com', password='testpass123'):
    """Create an return user."""
    return get_user_model().objects.create_user(email=email, password=password)


def detai_url(ingredient_id):
    """Get detail url for ingredient"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientApiTests(TestCase):
    """Test Unauthenticated API requrests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Test Ingregient 01')
        Ingredient.objects.create(user=self.user, name='Test Ingredient 02')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Test Ingredient 01')
        ingredient = Ingredient.objects.create(user=self.user, name='Test Ingredient 02')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test Updating Ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Test Ingredient 01')

        payload = {'name': 'Test Ingredietn 01 Updated'}
        url = detai_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test Deleting Ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name = 'Test Ingredient 01')

        url = detai_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())





