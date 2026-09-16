from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import AbstractBaseUser

from apps.login.services import login_user, get_user_roles

USER_CACHE = {}

class ERPNextBackend:
    def authenticate(self, request, username=None, password=None):
        resp = login_user(username, password)
        if resp.status_code == 200 and "message" in resp.json():
            sid = resp.cookies.get("sid")
            roles = get_user_roles(username, sid)
            user_id = abs(hash(username)) % (10**8)
            user = ERPUser(user_id, username, sid, roles)
            USER_CACHE[user_id] = {
                "username": username,
                "sid": sid,
                "roles": roles,
            }
            return user
        return None

    def get_user(self, user_id):
        # No usamos DB, devolvemos None
        user_data = USER_CACHE.get(user_id)
        if user_data:
            return ERPUser(user_id, user_data["username"], user_data["sid"], user_data["roles"])
        return None
    
class ERPUser:
    def __init__(self, user_id, username, sid=None, roles=None):
        self.pk = user_id
        self.id = username
        self.username = username
        self.erp_sid = sid
        self.roles = roles or []

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_staff(self):
        # Considera staff si tiene rol "admin"
        return "admin" in self.roles
    
    @property
    def is_superuser(self):
        # Considera superuser si tiene rol "superuser"
        return "System Manager" in self.roles

    def has_perm(self, perm, obj=None):
        # Ejemplo simple: si es admin o superuser, todos los permisos
        if self.is_superuser or self.is_staff:
            return True
        # Si no, puedes mapear permisos específicos según roles
        return False

    def has_module_perms(self, app_label):
        # Permitir acceso a módulos si es admin o superuser
        return self.is_superuser or self.is_staff        

    class _meta:
        class pk:
            @staticmethod
            def value_to_string(obj):
                return str(obj.id)

    def save(self, *args, **kwargs):
        # Evita el crash de update_last_login
        return