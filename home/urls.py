from django.urls import path
from . import views
app_name = 'home' # este es el nombre de esta vista!
urlpatterns = [
    path('', views.home, name='home'),
]



