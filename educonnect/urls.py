from django.contrib import admin
from django.urls import path, include  # ✅ Assurez-vous d'importer `include`
from core import views  # Import des vues de core


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('core.urls')),  # ✅ Ceci inclut toutes les routes définies dans `core/urls.py`
]
