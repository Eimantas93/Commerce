from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create_listing/", views.create_listing_view, name="create_listing"),
    path("listing/<str:id>", views.listing_view, name="listing"),
    path("<int:listing_id>", views.watch_view, name="watch"),
    path("close/<int:listing_id>", views.close_listing_view, name="close"),
    path("comment/<int:listing_id>", views.comment_view, name="comment"),
    path("my_watch_list", views.my_watch_list_view, name="my_watch_list"),
    path("categories", views.categories, name="categories"),
]
