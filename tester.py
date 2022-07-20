url_upn = 'https://upn.ru/kupit/kvartiry/studii-0/oblast-sverdlovskaya-1/tsena-do-3000000'
# url_upn = 'https://upn.ru/kupit/kvartiry/studii-0/oblast-sverdlovskaya-1/tsena-do-3000000?page=2'

index = url_upn.find('?page')
if index == -1:
    url = url_upn
else:
    url = url_upn[:index]
# if url_upn[-7:-2] == '?page':
#     url = url_upn[:-7]
# elif url_upn[-8:-3] == '?page':
#     url = url_upn[:-8]
# elif url_upn[-9:-4] == '?page':
#     url = url_upn[:-9]
# elif url_upn[-10:-5] == '?page':
#     url = url_upn[:-10]
# else:
#     url = url_upn

print(url)