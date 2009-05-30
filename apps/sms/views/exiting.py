from malnutrition.sms.views.exiting import Exit

class MalawiExit(Exit):
    def success(self):
        info = self.data.case.get_dictionary()
        info.update(self.data.case.provider.clinic.get_dictionary())
        info["reason"] = self.data.reason
        return "Thank you for informing us that Child #%(ref_id)s cancelled for at %(name)s GMC #%(codename)s has exited program. Reason given: %(reason)s." % info