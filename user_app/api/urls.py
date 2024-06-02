from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path

from user_app.api.views import register, logout_view, login_view, JugadoresUsuarioList, LotesFutCoinsList, \
    ComprarFutCoins

urlpatterns = [
    # path('login/', obtain_auth_token, name='login'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),

    path('logout/', logout_view, name='logout'),

    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('mis-jugadores/', JugadoresUsuarioList.as_view(), name='mis-jugadores'),

    path('lotes-futcoins/', LotesFutCoinsList.as_view(), name='lotes-futcoins'),
    path('comprar-futcoins/', ComprarFutCoins.as_view(), name='comprar-futcoins')
]
