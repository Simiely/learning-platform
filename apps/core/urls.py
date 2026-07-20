from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('category/<slug:slug>/', views.category_browse_view, name='category_browse'),
    path('category/<slug:slug>/cards/', views.category_cards_view, name='category_cards'),
    path('category/<slug:slug>/quiz/', views.category_quiz_view, name='category_quiz'),
    path('api/mark-viewed/<int:item_id>/', views.mark_viewed, name='mark_viewed'),
    path('api/reset-visited/<slug:slug>/', views.reset_visited, name='reset_visited'),
    path('api/item/<int:item_id>/', views.item_detail_api, name='item_detail_api'),
    path('api/quiz/<slug:slug>/question/', views.quiz_question_api, name='quiz_question_api'),
    path('api/quiz/<slug:slug>/submit/', views.quiz_submit_batch, name='quiz_submit_batch'),
]
