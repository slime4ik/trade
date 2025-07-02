from ad.forms import SearchForm

# Можно в ad:ad_list только оставить
def search_form(request):
    return {'search_form': SearchForm()}