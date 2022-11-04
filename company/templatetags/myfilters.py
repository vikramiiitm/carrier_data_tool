from django import template

register = template.Library()

def addclass(value, token):
    value.field.widget.attrs["class"] = token
    return value

def addplaceholder(value, token):
    value.field.widget.attrs["placeholder"] = token
    return value

@register.simple_tag
def my_url(value, field_name, urlencode=None):
    """
    It is used for navigation of next page with filter.

    value: page number
    field_name: string page
    urlencode: part of url from page=something to end
    """
    print('>>>>>>>>>>>>>>>>')
    print(value, field_name, urlencode)
    url = '?{}={}'.format(field_name, value)
    if urlencode:
        querystring = urlencode.split('&')  #it will be list of string ex ['page=2', 'name=something', 'legal_name=']
        # list of filtered query string (except page query)
        filtered_querystring = filter(lambda p: p.split('=')[0]!=field_name, querystring)   # ['name=something', 'legal_name=']
        # print(f'filtered_querystring: {filtered_querystring}')
        #jopin the filtered querystring with '&'
        encoded_query_string =  '&'.join(filtered_querystring)
        # print(f'encoded_query_string: {encoded_query_string}')
        #now join page number(=url line 20)
        url = '{}&{}'.format(url, encoded_query_string)
        print(f'url: {url}')
        return url
    return url

register.filter(addclass)
register.filter(addplaceholder)