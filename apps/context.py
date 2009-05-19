def processor(self):
    context = {
        "site": { "title": "Malawi",
                  "tabs": [
                  { "link": "/national/", "title": "National"},
                  { "link": "/district/", "title": "District"}, 
                  { "link": "/gmc/", "title": "GMC"},
                  { "link": "/child/", "title": "Child"},
                  { "link": "/has/", "title": "HSA"},
                  ]
                 },
    }
    return context