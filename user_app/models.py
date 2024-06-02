from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
import base64

key = base64.urlsafe_b64decode(settings.SECRET_KEY_FERNET)
cipher_suite = Fernet(key)


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=50)
    futcoins = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    objects = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class LoteFutCoins(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} - {self.cantidad} FutCoins por {self.precio} USD"


class CompraFutCoins(models.Model):
    usuario = models.ForeignKey(Account, related_name='compras_futcoins', on_delete=models.CASCADE)
    lote = models.ForeignKey(LoteFutCoins, on_delete=models.CASCADE)
    numero_tarjeta = models.CharField(max_length=16)
    fecha_expiracion = models.CharField(max_length=5)  # MM/YY
    cvv = models.CharField(max_length=256)  # Almacenará el CVV cifrado
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} compró {self.lote.cantidad} FutCoins por {self.lote.precio} USD"

    def save(self, *args, **kwargs):
        # Cifrar el CVV antes de guardarlo
        self.cvv = cipher_suite.encrypt(self.cvv.encode()).decode()
        super().save(*args, **kwargs)

    def get_cvv(self):
        # Método para descifrar el CVV
        return cipher_suite.decrypt(self.cvv.encode()).decode()
