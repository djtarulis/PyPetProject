from django.test import TestCase
from django.contrib.auth.models import User
from .models import Pet

class PetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.pet = Pet.objects.create(owner=self.user, name="Fluffy", species="Dog", happiness=90, health=80)

    def test_happiness_clamped_to_100(self):
        self.pet.happiness += 20  # Attempt to increase happiness to 110
        self.pet.save()
        self.assertEqual(self.pet.happiness, 100)  # Ensure it's clamped to 100

    def test_happiness_clamped_to_0(self):
        self.pet.happiness -= 150  # Attempt to decrease happiness to -60
        self.pet.save()
        self.assertEqual(self.pet.happiness, 0)  # Ensure it's clamped to 0

    def test_health_clamped_to_100(self):
        self.pet.health = 105  # Attempt to set health to 105
        self.pet.save()
        self.assertEqual(self.pet.health, 100)  # Ensure it's clamped to 100

    def test_health_clamped_to_0(self):
        self.pet.health = -10  # Attempt to set health to -10
        self.pet.save()
        self.assertEqual(self.pet.health, 0)  # Ensure it's clamped to 0
