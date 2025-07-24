
from django.urls import path,include
from .views import *

urlpatterns = [
    path('',index,name='index'),
    path('summary/',home,name='home'),
    path('signup/',signup,name='signup'),
    path('signin/',signin,name='signin'),
    path('signout/',signout,name='signout'),
    path('userhistory/<int:id>',user_history,name='userhistory'),
    path('summarydetail/<int:pk>',summary_user,name='summarydetail'),
    path('deletesummary/<int:pk>',delete_summary,name='deletesummary'),
    path('search/',search,name="searchquery"),
    
    
]
