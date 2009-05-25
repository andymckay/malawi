from malnutrition.sms.views.confirming import Confirm

class MalawiConfirm(Confirm):
    def success(self):
        info = self.data.provider.get_dictionary()
        info.update(self.data.facility.get_dictionary())
        return "%(mobile)s registered to %(provider_name_inverted)s at GMC #%(codename)s." % info