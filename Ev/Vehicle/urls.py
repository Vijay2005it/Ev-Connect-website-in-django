from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "Vehicle"

urlpatterns = [
    path('',views.index,name='index'),
    path('about_page',views.about_page,name="about_page"),
    path('register_page/',views.register_page,name='register_page'),
    path('login_page/',views.login_page,name='login_page'),
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('owner_dashboard',views.owner_dashboard,name='owner_dashboard'),
    path('user_dashboard',views.user_dashboard,name='user_dashboard'),
    path('add_bunker',views.add_bunker,name='add_bunker'),
    path('edit_bunker/<int:id>/',views.edit_bunker,name="edit_bunker"),
    path("delete_bunker/<int:id>",views.delete_bunker,name="delete_bunker"),
    path('slot_book<int:id>',views.slot_book,name="slot_book"),
    path('mark_done/<int:booking_id>/', views.mark_done, name='mark_done'),
    path('add_mechanic',views.add_mechanic,name="add_mechanic"),
    path('delete_mechanic/<int:id>',views.delete_mechanic,name="delete_mechanic"),
    path('service_page',views.service_page,name="service_page"),
    path('contact_message',views.contact_message,name="contact_message"),
    path('delete_message/<int:id>',views.delete_message,name="delete_message")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)