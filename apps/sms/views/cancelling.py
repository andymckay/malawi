from malnutrition.forms import Form
from malnutrition.forms import BooleanField, DateField, StringField, GenderField, FloatField
from malnutrition.sms.resolve import models

from malnutrition.sms.views.reporting import New, Report
from malnutrition.sms.command import authenticated, CommandError, Command

class NewCancelForm(Form):
    child = StringField(valid="(\d+)")
    gmc = StringField(valid="(\d+)")

class MalawiNewCancel(Command):
    @authenticated
    def post_init(self):
        self.form = NewCancelForm
    
    def error_not_exists(self):
        return "Cannot find a child to cancel"
    
    def process(self):
        self.data.provider = provider = models.Provider.by_mobile(self.message.peer)
        try:
            case = models.Case.objects.get(ref_id=self.form.clean.child.data, provider=provider)
        except models.Case.DoesNotExist:
            raise CommandError, self.error_not_exists()
        
        # i don't think this is right, do we lose history about the case?
        # but this should drop the case from the provider
        #case.provider = None
        case.save()
        self.data.case = case