from django.urls import path 
from . import views
urlpatterns = [
      path('', views.login, name='login'),
      path('dashboard/', views.dashboard, name='dashboard'),
      path('add/', views.ajouter, name='ajouter'),
    path('modify/<str:username>/', views.modify, name='modify'),
    path('delete/<str:username>/', views.supprimer, name='supprimer'),
    path('modify/<str:username>/', views.modify, name='modify'),
    path('modifyAdmin/<str:username>/', views.modifyAdmin, name='modifyAdmin'),
    path('deleted-users/', views.deleted_users_list, name='deleted_users_list'),
    path('logout/', views.logout_view, name='logout'),
    path('restore/<str:username>/', views.restore_user, name='restore_user'),
    path('restore/<str:username>/', views.restore_user, name='restore_user'),
   # path('', views.index, name='index'),
    path('show', views.index, name='index'),
    
    # path('ajouter_voiture', views.ajouter_voiture, name='ajouter_voiture'),
    path('ajouter_voiture_submit', views.ajouter_voiture_submit, name='ajouter_voiture_submit'),
    path('ajouter_client_submit', views.ajouter_client_submit, name='ajouter_client_submit'),
    
    path('supprimer_voiture/<voiture_id>', views.supprimer_voiture, name='supprimer_voiture'),
    path('delete_client/<client_id>/', views.delete_client, name='delete_client'),

    # path('update_voiture/<voiture_id>', views.update_voiture, name='update_voiture'),
    path('update_voiture_submit/<voiture_id>', views.update_voiture_submit, name='update_voiture_submit'),
    path('update_client_submit/<str:client_id>/', views.update_client_submit, name='update_client_submit'),

    path('reserve_car/<voiture_id>/', views.reserve_car, name='reserve_car'),
    path('submit_reservation/<voiture_id>/', views.submit_reservation, name='submit_reservation'),


    path('client', views.client, name='client'),
    path('voiture', views.voiture, name='voiture'),
    path('reservation', views.show_reservation, name='reservation'),
    path('supprimer_reservation/<str:reservation_id>/', views.supprimer_reservation, name='supprimer_reservation'),
    path('generate_pdf/<str:reservation_id>/', views.generate_pdf, name='generate_pdf'),
    path('change_dispo/<str:voiture_id>/', views.change_dispo, name='change_dispo'),

    path('accept_reservation/<str:reservation_id>/', views.accept_reservation, name='accept_reservation'),
    path('refuse_reservation/<str:reservation_id>/', views.refuse_reservation, name='refuse_reservation'),

]