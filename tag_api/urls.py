from django.urls import path, include
from .views import Tags, VMs, AssignUnassignTags, Users

urlpatterns = [
   
    # Tags URL
    path('tags', Tags.as_view()),
    path('tags/<str:id>', Tags.as_view()),
    path('assign_unassign_tags', AssignUnassignTags.as_view()),

    # VMs URL
    path('vms', VMs.as_view()),
    path('vms/<int:id>', VMs.as_view()),

    # User Profile URL
    path('user', Users.as_view()),
]