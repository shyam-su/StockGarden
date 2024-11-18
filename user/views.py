from django.shortcuts import render

# Create your views here.
def LoginView(request):
    return render(request, 'login.html')


def UserListView(request):
    return render(request, 'user.html')

def UserCreateView(request):
    return render(request, 'user_create.html')

def UserUpdateView(request):
    return render(request, 'user_update.html')

def UserDeleteView(request):
    return render(request, 'user_delete.html')

def LogoutView(request):
    return render(request,"user is logout")

