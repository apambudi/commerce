from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:user_id>/create", views.create, name="create"),       
    path("<int:auction_id>", views.listing, name="listing"),         
    path("<int:user_id>/watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("<int:field_id>/category", views.category, name="category"),
]
