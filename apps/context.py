def processor(self):
    context = {
        "site": { "title": "Malawi",
                  "tabs": [
                  { "link": "/", "title": "National"},
                  { "link": "/district/", "title": "District"}, 
                  { "link": "/gmc/", "title": "GMC"},
                  { "link": "/child/", "title": "Child"},
                  { "link": "/hsa/", "title": "HSA"},
                  { "link": "/setup/", "title": "Setup"},
                  ]
                 },
    }
    return context