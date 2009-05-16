from datetime import date

def parser(text):
    """ This is the text format requested, which unfortunately strptime doesn't understand """
    return date(year=int(text[4:8]),day=int(text[0:2]),month=int(text[2:4]))