from datetime import date, datetime, timedelta

def parser(text):
    """ This is the text format requested, which unfortunately strptime doesn't understand """
    return date(year=int(text[4:8]),day=int(text[0:2]),month=int(text[2:4]))
    
def last_month():
    now = datetime.now()
    previous = now - timedelta(days=now.day)
    beginning = datetime(year=previous.year, month=previous.month, day=1)
    end = datetime(year=previous.year, month=previous.month, day=previous.day)
    return beginning, end

def this_month():
    now = datetime.now()
    beginning = datetime(year=now.year, month=now.month, day=1)
    end = datetime(year=now.year, month=now.month, day=now.day)
    return beginning, end

if __name__=="__main__":
    print last_month()