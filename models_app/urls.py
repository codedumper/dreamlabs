from django.urls import path
from . import views
from . import schedule_views

app_name = 'models_app'

urlpatterns = [
    # Modèles
    path('', views.model_list, name='list'),
    path('<int:model_id>/', views.model_detail, name='detail'),
    path('create/', views.model_create, name='create'),
    path('<int:model_id>/update/', views.model_update, name='update'),
    path('<int:model_id>/deactivate/', views.model_deactivate, name='deactivate'),
    path('<int:model_id>/reactivate/', views.model_reactivate, name='reactivate'),
    path('<int:model_id>/user/reset-password/', views.model_user_reset_password, name='model_user_reset_password'),
    path('<int:model_id>/gains/create/', views.gain_create, name='gain_create'),
    path('worked-hours/', views.worked_hours_bulk_create, name='worked_hours_bulk_create'),
    
    # Horaires (Schedules)
    path('schedules/', schedule_views.schedule_list, name='schedule_list'),
    path('schedules/create/', schedule_views.schedule_create, name='schedule_create'),
    path('schedules/<int:schedule_id>/update/', schedule_views.schedule_update, name='schedule_update'),
    path('schedules/<int:schedule_id>/delete/', schedule_views.schedule_delete, name='schedule_delete'),
    
    # Assignations d'horaires
    path('schedule-assignments/', schedule_views.schedule_assignment_list, name='schedule_assignment_list'),
    path('schedule-assignments/create/', schedule_views.schedule_assignment_create, name='schedule_assignment_create'),
    
    # Sessions de travail
    path('work-sessions/', schedule_views.work_session_list, name='work_session_list'),
    path('work-sessions/<int:session_id>/confirm-presence/', schedule_views.work_session_confirm_presence, name='work_session_confirm_presence'),
    path('work-sessions/<int:session_id>/mark-absent/', schedule_views.work_session_mark_absent, name='work_session_mark_absent'),
    path('work-sessions/<int:session_id>/reactivate-from-absent/', schedule_views.work_session_reactivate_from_absent, name='work_session_reactivate_from_absent'),
    path('work-sessions/<int:session_id>/start-break/', schedule_views.work_session_start_break, name='work_session_start_break'),
    path('work-sessions/<int:session_id>/end-break/', schedule_views.work_session_end_break, name='work_session_end_break'),
    path('work-sessions/<int:session_id>/start-meal/', schedule_views.work_session_start_meal, name='work_session_start_meal'),
    path('work-sessions/<int:session_id>/end-meal/', schedule_views.work_session_end_meal, name='work_session_end_meal'),
    path('work-sessions/<int:session_id>/start-coaching/', schedule_views.work_session_start_coaching, name='work_session_start_coaching'),
    path('work-sessions/<int:session_id>/end-coaching/', schedule_views.work_session_end_coaching, name='work_session_end_coaching'),
    path('work-sessions/<int:session_id>/complete/', schedule_views.work_session_complete, name='work_session_complete'),
    path('work-sessions/<int:session_id>/reopen/', schedule_views.work_session_reopen, name='work_session_reopen'),
]
