from django.test import TestCase
from .models import Pet, CustomUser, Item, Pet, Inventory

class PetModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
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
    
class CustomUserTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
        self.item1 = Item.objects.create(name='Ball', description='A toy ball', price=10)
        self.item2 = Item.objects.create(name='Apple', description='A healthy snack', price=5)
        self.pet = Pet.objects.create(owner=self.user, name='Buddy', health=100, happiness=100, energy=90)

    def test_user_creation(self):
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')

    def test_inventory_management(self):
        inventory_item = Inventory.objects.create(user=self.user, item=self.item1, quantity=2)
        self.assertEqual(inventory_item.user.username, 'testuser')
        self.assertEqual(inventory_item.item.name, 'Ball')
        self.assertEqual(inventory_item.quantity, 2)

    def test_pet_creation(self):
        self.assertEqual(Pet.objects.count(), 1)
        self.assertEqual(self.pet.name, 'Buddy')
        self.assertEqual(self.pet.owner, self.user)

class InventoryEdgeCasesTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
        self.item = Item.objects.create(name='Bone', description='A crunchy bone', price=20)

# TODO: FINISH SETTING UP INVENTORY TESTS
    def test_negative_quantity(self):
        with self.assertRaises(ValueError):
            Inventory.objects.create(user=self.user, item=self.item, quantity=-5)
    
    def test_zero_quantity(self):
        inventory_item = Inventory.objects.create(user=self.user, item=self.item, quantity=0)
        self.assertEqual(inventory_item.quantity, 0)

    # Not sure if this is how I want to handle inventory yet...
    # def test_duplicate_inventory_entries(self):
    #     Inventory.objects.create(user=self.user, item=self.item, quantity=5)
    #     with self.assertRaises(Exception):
    #         Inventory.objects.create(user=self.user, item=self.item, quantity=3)
        
    def test_large_quantity(self):
        inventory_item = Inventory.objects.create(user=self.user, item=self.item, quantity=1000000)
        self.assertEqual(inventory_item.quantity, 1000000)