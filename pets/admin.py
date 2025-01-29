from traceback import format_tb
from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Pet, Item, Transaction, Inventory, CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Admin configuration for Users, including inventory editing.
    """
    list_display = ['id', 'username', 'email', "display_pets" , 'display_inventory', 'manage_inventory', 'is_staff', 'is_superuser']  # ✅ Shows ID & username
    list_filter = ['is_staff', 'is_superuser', 'is_active']  # Filter options in admin
    search_fields = ['username', 'email']  # Search users by username or email
    ordering = ['id']  # Sort users by ID
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'currency')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    def get_user(self, obj):
        """
        Returns the username of the related User.
        """
        return obj
    get_user.admin_order_field = 'user' # Allow sorting by user
    get_user.short_description = "Username" # Rename column in Django Admin

    def display_inventory(self, obj):
        """
        Show inventory as a table inside ProfileAdmin.
        """
        inventory = Inventory.objects.filter(user=obj)
        if not inventory.exists():
            return "No items"

        html = "<table><tr><th>Item</th><th>Quantity</th></tr>"
        for item in inventory:
            html += f"<tr><td>{item.item.name}</td><td>{item.quantity}</td></tr>"
        html += "</table>"

        return format_html(html)

    display_inventory.short_description = "Current Inventory"

    def manage_inventory(self, obj):
        """
        Provide a link to the Inventory admin filtered by the user's inventory.
        """
        url = reverse('admin:pets_inventory_changelist') + f"?user__id__exact={obj.id}"
        return format_html('<a href="{}">Manage Inventory</a>', url)
    
    manage_inventory.short_description = "Manage Inventory"

    def display_pets(self, obj):
        """
        Show the user's pet names.
        """
        pets = Pet.objects.filter(owner=obj)  # ✅ Fetch user's pets
        if not pets.exists():
            return "No pets"

        return ", ".join([pet.name for pet in pets])  # ✅ Show pet names as a comma-separated list

    display_pets.short_description = "Pets"

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for Items.
    """
    list_display = ['name', 'description', 'price', 'is_food', 'is_toy', 'health_increase', 'happiness_increase', 'energy_increase']
    search_fields = ['name']  # Enable search by name


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner', 'age', 'health', 'happiness', 'energy']
    
@admin.register(Transaction)
class GlobalTransactions(admin.ModelAdmin):
    list_display = ['id', 'item', 'timestamp']
    search_fields = ['id', 'item', 'timestamp']  # Enable search by name

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    """Admin panel for managing Inventory."""
    list_display = ['user', 'item', 'quantity']