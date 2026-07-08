from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('generate/', views.generate_view, name='generate'),
    path('preview/', views.preview_view, name='preview'),
    path('shuffle/', views.shuffle_view, name='shuffle'),
    path('export/', views.export_view, name='export'),
    path('export/docx/', views.export_docx_view, name='export_docx'),
    path('export/pdf/', views.export_pdf_view, name='export_pdf'),
    path('reset/', views.reset_view, name='reset'),
]
