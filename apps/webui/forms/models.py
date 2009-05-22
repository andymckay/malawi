from malnutrition.ui.forms.base import BaseForm, BaseModelForm
from apps.sms.models.base import Facility, Zone, Provider
from django.contrib.auth.models import User 

class GMCForm(BaseModelForm):
    def __init__(self, *args, **kw):
        BaseModelForm.__init__(self, *args, **kw)
        self.fields["codename"].label = "GMC Id"

    class Meta:
        model = Facility
        exclude = ('role', )

class ZoneForm(BaseModelForm):
    def __init__(self, *args, **kw):
        BaseModelForm.__init__(self, *args, **kw)

    class Meta:
        model = Zone
        exclude = ('head', 'number')

class ProviderForm(BaseModelForm):
    def __init__(self, *args, **kw):
        BaseModelForm.__init__(self, *args, **kw)

    class Meta:
        model = Provider
        exclude = ('user', 'manager', 'following_users', 'following_clinics', 'alerts')
        
class UserForm(BaseModelForm):
    def __init__(self, *args, **kw):
        BaseModelForm.__init__(self, *args, **kw)

    class Meta:
        model = User
        exclude = ('email', 'password', 'is_staff', 'is_active', 'is_superuser', 'last_login', \
                    'date_joined', 'groups', 'user_permissions')

        