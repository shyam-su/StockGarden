from django.shortcuts import render

# Create your views here.
def LoginView(request):
    return render(request, 'login.html')


def UserListView(request):
    return render(request, 'user_list.html')

def UserCreateView(request):
    pass

def UserUpdateView(request):
    pass

def UserDeleteView(request):
    pass

