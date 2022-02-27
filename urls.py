from django.urls import path
from . import views

urlpatterns = [
		path("",views.index,name="index"),
		path("<int:page>",views.index,name="index"),
		path("post/",views.post,name="post"),
		path("share/<int:share_id>",views.share,name="share"),
]
