from malnutrition.sms.views.joining import Join

class MalawiJoin(Join):
    def success(self):
        info = self.data.provider.get_dictionary()
        info.update(self.data.facility.get_dictionary())
        return "Name = %(provider_name_inverted)s, GMC = %(name)s %(codename)s,"\
            " Phone number = %(mobile)s."\
            " If this is not correct, please re-register." % info

    def error_in_use(self, in_use, facility):
        info = in_use.get_dictionary()
        info.update(facility.get_dictionary())
        return "An existing user %(provider_name_inverted)s at GMC #%(codename)s"\
            " is already registered to this phone number. "\
            " Confirm registration by replying N (for no) or Y (for yes)." % info
                    
    def error_facility_exists(self):
        return "The GMC ID given does not exist."