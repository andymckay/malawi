from malnutrition.forms import Form
from malnutrition.sms.command import Command

class NullForm(Form):
    pass
    
class MalawiHelp(Command):
    def post_init(self):
        self.form = NullForm

    def success(self):
        return "To register yourself, SMS the following:  JOIN LastName FirstName Username To register a child, SMS the following:  NEW Child# GMC# gender DOB contact# To record information on an existing child, SMS the following:  Child# GMC# weight height muac oedema diarrhea"
    
    def process(self):
        pass