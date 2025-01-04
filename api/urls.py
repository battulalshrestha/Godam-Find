from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet
from .views import TopWarehouseViewSet
from .views import TagViewSet
from .views import GoogleLoginView
from .views import GoogleLoginTestView
from .views import CreateReviewAPIView
from .views import UserReviewsAPIView
from .views import AddToFavoritesAPIView
from .views import RemoveFromFavoritesAPIView
from .views import FavoriteWarehouseAPIView, AddWarehouseView,UserRequestWarehouseAPIView
router = DefaultRouter()
router.register(r'warehouse', WarehouseViewSet)
router.register(r'top-warehouse', TopWarehouseViewSet)
router.register(r'tag', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('google-login-test/', GoogleLoginTestView.as_view(), name='google-login-test'),
    path('create-review/', CreateReviewAPIView.as_view(), name='add-review'),
    path('user-reviews/<str:user_id>/', UserReviewsAPIView.as_view(), name='user-reviews'),
    path('add-to-favorites/', AddToFavoritesAPIView.as_view(), name='add-to-favorites'),
    path('remove-from-favorites/', RemoveFromFavoritesAPIView.as_view(), name='remove-from-favorites'),
    path('favorite-warehouses/<int:user_id>/', FavoriteWarehouseAPIView.as_view(), name='favorite-warehouses'),
    path('add-warehouse/', AddWarehouseView.as_view(), name='add-warehouse'),
    path('user-requested-warehouses/<int:user_id>/',UserRequestWarehouseAPIView.as_view(), name='user-requested-warehouses'),



]