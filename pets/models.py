from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError

"""TODO: Include avatars, level"""
class CustomUser(AbstractUser):
    """
    Extends Django's default User model with additional fields.
    """
    currency = models.IntegerField(default=1000)    # Initiall currency
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  # Optional user avatar

    def __str__(self):
        return self.username
    
    def add_item_to_inventory(self, item, quantity=1):
        """
        Add an item to the user's inventory.
        """
        inventory_item, created = Inventory.objects.get_or_create(user=self, item=item)
        inventory_item.add_item(quantity)

    def remove_item_from_inventory(self, item, quantity=1):
        """
        Remove an item from the user's inventory.
        """
        try:
            inventory_item = Inventory.objects.get(user=self, item=item)
            return inventory_item.remove_item(quantity)
        except Inventory.DoesNotExist:
            return False  # Item not found in inventory

    def get_inventory(self):
        """
        Get the user's entire inventory.
        """
        return self.inventory.all()

    def spend_currency(self, amount):
        """
        Deduct currency from the user.
        """
        if self.currency >= amount:
            self.currency -= amount
            self.save()
            return True
        return False  # Not enough currency

    def earn_currency(self, amount):
        """
        Add currency to the user.
        """
        self.currency += amount
        self.save()  
    

class Pet(models.Model):    # Pet attributes
    id = models.AutoField(primary_key=True)  # Ensures a unique ID
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pets")
    name = models.CharField(max_length=25)
    species = models.CharField(max_length=50)
    age = models.IntegerField(default=0)
    happiness = models.IntegerField(default=100)
    max_happiness = models.IntegerField(default=100)
    health = models.IntegerField(default=100)
    max_health = models.IntegerField(default=100)
    energy = models.IntegerField(default=100)
    max_energy = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    """TODO: Include avatars, level"""

    def save(self, *args, **kwargs):
        """
        Clamp happiness and health between 0 and 100
        """
        self.happiness = max(0, min(self.happiness, 100))
        self.health = max(0, min(self.health, 100))
        super().save(*args, **kwargs)  # Call the original save method

    def feed(self, user, item_id):
        """
        Feed the pet using a food item from the user's inventory
        """
        try:
            inventory_item = Inventory.objects.get(user=user, item_id=item_id)
            item=inventory_item.item

            if item.is_food and inventory_item.remove_item():   # Consumes item
                self.happiness += item.happiness_increase
                self.health += item.health_increase
                self.energy += item.energy_increase
                self.save()
                return True # Successfully fed pet
        except Inventory.DoesNotExist:
            pass
        return False    # Feeding failed

    def __str__(self):
        return f"{self.name} ({self.species})"

class Item(models.Model): # Generic item model
    """
    Item attributes
    """
    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    price = models.IntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    is_food = models.BooleanField(default=False)  # Marks if this item can be consumed as food
    is_toy = models.BooleanField(default=False)  # Marks if this item is a toy
    health_increase = models.IntegerField(default=0)  # Health points restored by this item
    happiness_increase = models.IntegerField(default=0)  # Happiness points restored by this item
    energy_increase = models.IntegerField(default=0) # "           "
    
    def __str__(self):
        return self.name
    
class Inventory(models.Model):
    """
    Tracks which item a user owns and how many.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inventory")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="inventory_item")
    quantity = models.IntegerField(default=0) # Number of item user owns.

    def __str__(self):
        """
        Prints string to display User and what items they have
        """
        # Example "john_doe - Apple (x3)"
        return f"{self.user} - {self.item.name} (x{self.quantity})"
    
    def add_item(self, amount=1):
        """
        Adds a specified amount of the item to the inventory.
        """
        self.quantity += amount
        self.save()

    def remove_item(self, amount=1):
        """
        Removes a specified amount of item from inventory. Deletes if quantity is 0
        """
        if self.quantity >= amount:
            self.quantity -= amount
            if self.quantity == 0:
                self.delete()
            else:
                self.save()
            return True
        return False # Not enough items to remove
    
    def add_item_to_user(user, item, amount=1):
        """
        Adds an item to user's inventory
        """
        # created is a boolean. True if object is created, False if not
        inventory_item, created = Inventory.objects.get_or_create(user=user, item=item)
        inventory_item.add_item(amount)

    def remove_item_from_user(user, item, amount=1):
        """
        Removes an item from the user's inventory.
        """
        try:
            inventory_item = Inventory.objects.get(user=user, item=item)
            return inventory_item.remove_item(amount)
        except Inventory.DoesNotExist:
            return False  # Item not in inventory
        
    def use_item(self, pet):
        """
        Use an item from the inventory on a pet.
        - If the item is food, increase pet health and remove item.
        - If the item is a toy, increase pet happiness.
        """

        if self.quantity <= 0:
            raise ValidationError("You don't have enough of this item.")
        
        # Apply item effects to the pet
        if self.item.is_food:
            pet.health = min(pet.health + self.item.health_increase, pet.max_health)
            pet.energy = min(pet.energy + self.item.energy_increase, pet.max_energy)
        elif self.item.is_toy:
            pet.happiness = min(pet.happiness + self.item.happiness_increase, 100)

        pet.save()

        # Remove on item from inventory
        self.quantity -= 1
        if self.quantity == 0:
            self.delete()
        else:
            self.save()

"""
TODO: Implement transactions, create a global shop
"""
class Transaction(models.Model):    # Currency transaction
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

