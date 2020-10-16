"""SynthesisNavigator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import url
from SynthesisNavigator import views,DM,formget
from django.views.static import serve
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Home/',views.Home),
    path('database/',views.DataBase),
    path('hms/',views.HybridMetabolicSimulation),
    path('pf/',views.PathwayFinding),
    #path('insertdb/', DM.insert_all_data),
    path('HMS/',views.HMS),
    path('PF/',views.PF),
    path('PFR/',views.PFR),
    path('DBS/',views.DBS),
    #path('formGet/',formget.formGet),
    re_path(r'file_down/(?P<path>.*)$', views.file_down),

    url( r'^static/(?P<path>.*)$',serve,{'document_root':settings.STATIC_ROOT},name='static'),
]
