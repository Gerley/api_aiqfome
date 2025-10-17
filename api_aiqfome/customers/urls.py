from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, FavoriteProductViewSet

router = DefaultRouter()
router.register(r'favorite-products', FavoriteProductViewSet, basename="favorite-products")
router.register(r'', CustomerViewSet, basename="user")

urlpatterns = router.urls
