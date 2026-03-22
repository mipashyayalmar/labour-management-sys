from django.urls import path
from . import views

urlpatterns = [
    # Language
    path('set-language/', views.set_language, name='set_language'),
    
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_entry, name='add_entry'),
    path('list/', views.list_entries, name='list_entries'),
    path('reports/', views.reports, name='reports'),
    
    # CRUD operations
    path('edit/<int:pk>/', views.edit_entry, name='edit_entry'),
    path('delete/<int:pk>/', views.delete_entry, name='delete_entry'),
    path('update-entry/', views.update_entry, name='update_entry'),
    
    # API endpoints
    path('get-total/', views.get_calculate_total, name='get_total'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('api/reports/', views.get_reports_data, name='get_reports_data'),
]