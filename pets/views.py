from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import Pet, Item, Inventory, Item
from .forms import PetForm, UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("Form is valid")  # Debug
            user = form.save()
            print(f"User created: {user}")  # Debug
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                print(f"User authenticated: {user}")  # Debug
                login(request, user)    # Log the user in after signup
                messages.success(request, 'Your account has been created! You can now log in.')
                return redirect('login') # Redirect to login page
            else:
                print("Authentication failed")  # Debug
        else:
            print("Form is invalid") # Debug
    else:
        form = UserCreationForm()
    return render(request, 'pets/register.html', {'form': form})

def pet_list(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'pets/pet_list.html', {'pets': pets})

@login_required
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            return redirect('pet_list')
        
    else:
        form = PetForm()
    return render(request, 'pets/add_pet.html', {'form': form})

@login_required
def buy_items(request, item_id, quantity):
    item = Item.objects.get(id=item_id) # item id
    profile = request.user  # profile of user buying item

    if profile.currency >= item.price:  # check if user has enough money
        profile.currency -= item.price  # deduct currency from user
        profile.save()
        profile.add_item_to_inventory(item, quantity)   # add item to user profile
        return redirect('pets/user_inventory', username=request.user.username)
    else:
        return render(request, 'pets/error.html', {'message': 'Not enough currency to buy this item!'})

@login_required
def feed_pet(request, pet_id, item_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    success = pet.feed(request.user, item_id)

    if success:
        message = f"You fed {pet.name} using {item_id}!"
    else:
        message = "You don't have the required food item."

    # Redirect to the pet detail page
    return redirect("pets/pet_detail", pet_id=pet.id)

@login_required
def view_inventory(request):
    inventory = Inventory.objects.filter(user=request.user)
    
    filter_option = request.GET.get('filter', '')  # Default to no filter

    if filter_option == 'happiness':
        inventory = inventory.filter(item__happiness_increase__gt=0)  # Filter by happiness
    elif filter_option == 'food':
        inventory = inventory.filter(item__is_food=True)  # Filter by food items
    elif filter_option == 'toy':
        inventory = inventory.filter(item__is_toy=True)  # Filter by toy items
    elif filter_option == 'health':
        inventory = inventory.filter(item__health_increase__gt=0)  # Filter by health items
    elif filter_option == 'energy':
        inventory = inventory.filter(item__energy_increase__gt=0)  # Filter by energy items
    # Filter Options
    
    return render(request, "pets/user_inventory.html", {
        "inventory": inventory,
        "filter_option": filter_option,
        })

@login_required
def use_item(request, inventory_id, pet_id):
    """
    View to handle using an item from inventory on a pet.
    """
    inventory_item = get_object_or_404(Inventory, id=inventory_id, user=request.user)
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)

    try:
        inventory_item.use_item(pet)
        messages.success(request, f"You used {inventory_item.item.name} on {pet.name}!")
    except ValidationError as e:
        messages.error(request, str(e)),

    return redirect('pets/pet_detail', pet_id=pet.id)    # Redirect back to pet details page