from django.shortcuts import render, get_object_or_404, redirect
import logging
from django.core.paginator import Paginator
from django.contrib import messages
from .models import User
from .forms import UserForm

# Create your views here.
logger = logging.getLogger(__name__)

def LoginView(request):
    return render(request, 'login.html')


def UserListView(request):
    try:
        users = User.objects.all()
        pagination = Paginator(users, 10)  
        page_number = request.GET.get('page')
        page_obj = pagination.get_page(page_number)
        context={
            'users': page_obj,
        }
        logger.info("Successfully retrieved user.")
        return render(request, 'user.html', context)
    except Exception as e:
        logger.error(f"Error retrieving user : {e}")
        messages.error(request, "Failed to retrieve users.")
        return render(request, '404.html', status=404)

def UserCreateView(request):
    try:
        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                form.save()
                logger.info("User created successfully.")
                messages.success(request, "User created successfully!")
                return redirect('user')
            else:
                logger.warning("Invalid data submitted for user creation.")
                messages.error(request, "Failed to create user. Please check the form.")
        else:
            form = UserForm()
            logger.debug("Rendering user creation form.")
        return render(request, 'user_create.html', {'form': form})
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        messages.error(request, "Failed to create user.")
        return render(request, '404.html', status=404)


def UserUpdateView(request,pk):
    try:
        user = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            form = UserForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                logger.info(f"User (ID: {pk}) updated successfully.")
                messages.success(request, "User updated successfully!")
                return redirect('user')
            else:
                logger.warning(f"Invalid data submitted for updating user (ID: {pk}).")
                messages.error(request, "Failed to update user. Please check the form.")
        else:
            form = UserForm(instance=user)
            logger.debug(f"Rendering update form for user (ID: {pk}).")
        return render(request, 'user_update.html', {'form': form})
    except Exception as e:
        logger.error(f"Error updating user (ID: {pk}): {e}")
        messages.error(request, "Failed to update user.")
        return render(request, '404.html', status=404)

def UserDeleteView(request,pk):
    try:
        user = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            user.delete()
            logger.info(f"User (ID: {pk}) deleted successfully.")
            messages.success(request, "User deleted successfully!")
            return redirect('user')
        logger.debug(f"Rendering delete confirmation for user (ID: {pk}).")
        return render(request, 'user_delete.html', {'user': user})
    except Exception as e:
        logger.error(f"Error deleting user (ID: {pk}): {e}")
        messages.error(request, "Failed to delete user.")
        return render(request, '404.html', status=404)

def LogoutView(request):
    return render(request,"user is logout")

