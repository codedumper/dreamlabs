from django.urls import path
from . import views
from . import bonus_views

app_name = 'agencies'

urlpatterns = [
    path('', views.agency_list, name='list'),
    path('<int:agency_id>/', views.agency_detail, name='detail'),
    path('create/', views.agency_create, name='create'),
    path('<int:agency_id>/update/', views.agency_update, name='update'),
    # Bonus rules
    path('<int:agency_id>/bonus-rules/', bonus_views.bonus_rule_list, name='bonus_rule_list'),
    path('<int:agency_id>/bonus-rules/create/', bonus_views.bonus_rule_create, name='bonus_rule_create'),
    path('<int:agency_id>/bonus-rules/<int:rule_id>/update/', bonus_views.bonus_rule_update, name='bonus_rule_update'),
    path('<int:agency_id>/bonus-rules/<int:rule_id>/delete/', bonus_views.bonus_rule_delete, name='bonus_rule_delete'),
    path('<int:agency_id>/bonus-rules/reorder/', bonus_views.bonus_rule_reorder, name='bonus_rule_reorder'),
]
