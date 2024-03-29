# %%
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8',
        'cache-control': 'max-age=0',
        # 'cookie': 'clever-last-tracker-71584=1; _gid=GA1.2.1297147818.1711480320; __gads=ID=f0084eb3a72456d2:T=1711368689:RT=1711480321:S=ALNI_MYuwMLgi-YeccvqCwDwkUoBGxOUFQ; __gpi=UID=00000a143a32badb:T=1711368689:RT=1711480321:S=ALNI_MZOcqmvusSnbEhGR9Q0daeSMpKhlg; __eoi=ID=e50d1a27905961d2:T=1711368689:RT=1711480321:S=AA-AfjakPcgTQRwnvCVTKqBEUB6I; _ga=GA1.2.539000503.1711368686; _ga_DJLCSW50SC=GS1.1.1711480320.2.1.1711480334.46.0.0; _ga_D6NF5QC4QT=GS1.1.1711480320.2.1.1711480334.46.0.0; FCNEC=%5B%5B%22AKsRol-Wfv0NM60nVWrYpx4nVoknvZ0bcsJoUfokibpuqDt4ktftb1uGwL1yiA6Dhva-RNtEQpVy-xxhkt9yX2sfIS9RBUwarkK_0LzMgTBIRMJljDEkkU82YjVBLI7fYBbO_7TcIzOspSYmzPR6SVqAHOXKwC0mRg%3D%3D%22%5D%5D',
        'referer': 'https://www.residentevildatabase.com/personagens/',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

def get_content(url):
    resp = requests.get(url, headers=headers)
    return resp

def get_basic_info(soup):

    div_page = soup.find("div", class_="td-page-content")

    paragrafo = div_page.find_all('p')[1]

    ems = paragrafo.find_all('em')


    data = {}

    for i in ems:
        chave, valor, *_ = i.text.split(':')
        chave = chave.strip(' ')
        data[chave] = valor.strip(' ')
        
    return data

def get_aparicoes(soup):
    lis = (soup.find("div", class_="td-page-content")
            .find('h4')
            .find_next()
            .find_all('li'))

    if lis:  # Verifica se a lista não está vazia
        aparicoes = [i.text for i in lis]
        return aparicoes
    else:
        return []  # Retorna uma lista vazia se lis estiver vazia


def get_personagens_info(url):
    resp = get_content(url)
    if resp.status_code != 200:
        print("Não foi possivel obter os dados")
        return {}
    else:
        soup = BeautifulSoup(resp.text) 
        data = get_basic_info(soup)
        data['Aparicoes'] = get_aparicoes(soup)
        return data


# %%
def get_links():
    url = 'https://www.residentevildatabase.com/personagens'
    resp = requests.get(url, headers=headers)

    soup_personagens = BeautifulSoup(resp.text)
    ancoras = (soup_personagens.find('div', class_='td-page-content')
                    .find_all('a'))

    links =[i['href']for i in ancoras]
    return links

# %%

links = get_links()
data = []
for i in tqdm(links):
    d = get_personagens_info(i)
    d['link'] = i
    nome = i.split('/')[-1].replace('-', ' ').title()
    d['Nome'] = nome
    data.append(d)
    
# %%

df = pd.DataFrame(data)
df

# %%
df.to_parquet('dados_re.parquet', index=False)

# %%
df.to_pickle('dados_re.pkl')
df