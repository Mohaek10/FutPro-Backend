from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user_app.api.views import register, logout_view, login_view, JugadoresUsuarioList, LotesFutCoinsList, \
    ComprarFutCoins, VerTodasLasComprasAdmin, UserProfileView, ChangePasswordView, check_admin_status

router = DefaultRouter()
router.register('lotes-futcoins', LotesFutCoinsList, basename='lotes-futcoins')
urlpatterns = [
    # path('login/', obtain_auth_token, name='login'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('check-admin-status/', check_admin_status, name='check-admin-status'),

    path('logout/', logout_view, name='logout'),

    path('user/me/', UserProfileView.as_view(), name='user-me'),
    path('user/me/change-password/', ChangePasswordView.as_view(), name='user-me-change-password'),

    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('mis-jugadores/', JugadoresUsuarioList.as_view(), name='mis-jugadores'),

    path('comprar-futcoins/', ComprarFutCoins.as_view(), name='comprar-futcoins'),
    path('', include(router.urls)),

    path('todas-las-compras/', VerTodasLasComprasAdmin.as_view(), name='todas-las-compras'),

]
