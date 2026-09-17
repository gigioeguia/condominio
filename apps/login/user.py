class ERPUser:
    def __init__(self, erp_sid, username, full_name, permissions=None):
        self.erp_sid = erp_sid
        self.username = username
        self.full_name = full_name
        self.permissions = permissions or []

    # 🔑 Django requiere estas tres propiedades para comprobar autenticación
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True

    def __str__(self):
        return self.username