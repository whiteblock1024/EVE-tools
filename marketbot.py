import datetime
import requests
import json
import re
from bs4 import BeautifulSoup


server_available: bool = True


DIC = {
    "pa" : "皮特姆多谱式护盾增强器 A型",
    "皮a" : "皮特姆多谱式护盾增强器 A型",
    "pc" : "皮特姆多谱式护盾增强器 C型",
    "皮c" : "皮特姆多谱式护盾增强器 C型",
    "皮中a" : "皮特中型护盾回充增量器 A型",
    "皮超大x" : "皮特超大型护盾回充增量器 X型",
    "吉超大x" : "吉斯特超大型护盾回充增量器 X型",
    "海军膜" : "帝国海军多谱式电压薄膜",
    "28抗" : "科波姆多谱式电压薄膜 A型",
    "科x" : "科波斯大型装甲维修器 X型",
    "x修" : "科波斯大型装甲维修器 X型",
    "x推" : "科尔500MN微型跃迁推进器 X型",
    "小鱼" : "逆戟鲸级",
    "yst" : "伊什塔级",
    "hkt" : "赫卡特级",
    "pld" : "帕拉丁级",
    "plex" : "伊甸币",
    "月卡" : "月卡",
    "洛基全套" : "洛基全套",
    "脑抽" : "技能提取器",
    "脑浆" : "大型技能注入器",
    "小脑浆" : "小型技能注入器"
}


# 1000000 -> 1,000,000
def num_process(num) -> str:
    to_str = str(num)
    count = 0
    sum_str=''
    for one_str in to_str[::-1]:
        count += 1
        if count %3==0 and count != len(to_str):
            one_str = ',' + one_str
            sum_str = one_str + sum_str
        else:
            sum_str = one_str + sum_str
    return sum_str


# 查询物品ID
def get_item(name: str) -> dict:
    for key,value in DIC.items():
        if name == key:
            name = value

    proxies = {'http': None, 'https': None}
    data = {
            'name':name
            }

    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Key': '332213fa4a9d4288b5668ddd9'}
    search_ID_url = 'https://www.ceve-market.org/api/searchname'
    ID_json = requests.post(search_ID_url, headers=HEADERS, data=data, proxies=proxies)       

    ID_dict = json.loads(ID_json.text)

    if len(ID_dict) == 0:
        return  None

    for i in range(len(ID_dict)):
        if name == ID_dict[i]['typename']:
            return ID_dict[i]
    
    return ID_dict[0]


#根据物品ID查询出售价格
def get_price_sell(ID: str) -> str:
    proxies = {'http': None, 'https': None}
    search_price_url = 'https://www.ceve-market.org/api/market/region/10000002/type/'
    search_price_url += ID
    search_price_url += '.json'

    price_json = requests.get(search_price_url, proxies=proxies)
    price_dict = json.loads(price_json.text)

    ret = price_dict['sell']['min']

    return ret


# 根据物品ID查询收购价格
def get_price_buy(ID: str) -> str:
    proxies = {'http': None, 'https': None}
    search_price_url = 'https://www.ceve-market.org/api/market/region/10000002/type/'
    search_price_url += ID
    search_price_url += '.json'

    price_json = requests.get(search_price_url, proxies=proxies)
    price_dict = json.loads(price_json.text)

    ret = price_dict['buy']['max']

    return ret


# 提取copy中的物品信息
def process(copy: str) -> list:
    item_list = copy.split('\n')
    for i in range(len(item_list)):
        item_list[i] = item_list[i].replace(' ', '/')
        item_list[i] = item_list[i].split('\t')
        if len(item_list[i]) > 1:
            item_list[i] = item_list[i][0] + '+' + item_list[i][1]
        else:
            item_list[i] = item_list[i][0] + '+' + 'N'
        item_list[i] = item_list[i].replace(' ', '')
        item_list[i] = item_list[i].split('+')
        item_list[i][0] = item_list[i][0].replace('/', ' ')
        if item_list[i][1] == 'N':
            item_list[i][1] = '1'
    return item_list


# 获取物品的卖单价格
def get_price_list_sell(copy: str) -> str:
    item_list:list = process(copy)
    final_price = 0
    ret = '\n物品名    数量    单价    总价'
    for i in range(len(item_list)):
        name:str = item_list[i][0]
        count:str = item_list[i][1].replace(',', '')
        try:
            price:str = get_price_sell(str(get_item(item_list[i][0])['typeid']))
        except:
            return f"物品名不存在：{item_list[i][0]}"
        add_price:int = int(price) * int(count)
        final_price += int(add_price)
        ret += f'\n{name}    {num_process(count)}    {num_process(price)}    {num_process(add_price)}'
    # ret += f'\n\n卖单总价: {num_process(final_price)} isk'
    ret = f'\n卖单总价: {num_process(final_price)} isk'
    return ret


# 获取物品的收单价格
def get_price_list_buy(copy: str) -> str:
    item_list:list = process(copy)
    final_price = 0
    # ret = '\n物品名    数量    单价    总价'
    for i in range(len(item_list)):
    #     name:str = item_list[i][0]
        count:str = item_list[i][1].replace(',', '')
        try:
            price:str = get_price_buy(str(get_item(item_list[i][0])['typeid']))
        except:
            return f"物品名不存在：{item_list[i][0]}"
        add_price:int = int(price) * int(count)
        final_price += int(add_price)
    #     ret += f'\n{name}    {num_process(count)}    {num_process(price)}    {num_process(add_price)}'
    # ret += f'\n\n收单总价: {num_process(final_price)} isk'
    ret = f'\n收单总价: {num_process(final_price)} isk'
    return ret


# 市场查询
def market(name: str) -> str:

    for key,value in DIC.items():
        if name == key:
            name = value

    ret = ' '
    proxies = {'http': None, 'https': None}
    data = {
            'name':name
            }

    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Key': '332213fa4a9d4288b5668ddd9'}
    search_ID_url = 'https://www.ceve-market.org/api/searchname'
    ID_json = requests.post(search_ID_url, headers=HEADERS, data=data, proxies=proxies)       

    ID_dict = json.loads(ID_json.text)

#########################
    if name == '月卡':

        type_ID = '44992'
        type_name = '月卡'

        search_price_url = 'https://www.ceve-market.org/api/market/region/10000002/type/'
        search_price_url += type_ID
        search_price_url += '.json'

        price_json = requests.get(search_price_url, proxies=proxies)
        price_dict = json.loads(price_json.text)

        ret += type_name
        ret += ':\n'
        ret += '收购:  '
        ret += num_process(price_dict['buy']['max'] * 500)
        ret += '\n'
        ret += '出售:  '
        ret += num_process(price_dict['sell']['min'] * 500)

        return ret
#########################
    if name == '洛基全套':

        type_ID_Loki = '29990'
        type_ID_LokiM1 = '45595'
        type_ID_LokiM2 = '45608'
        type_ID_LokiM3 = '45621'
        type_ID_LokiM4 = '45632'
        type_name = '洛基全套'

        search_price_url_Loki = 'https://www.ceve-market.org/api/market/region/10000002/type/'
        search_price_url_Loki += type_ID_Loki
        search_price_url_Loki += '.json'

        price_json_Loki = requests.get(search_price_url_Loki, proxies=proxies)
        price_dict_Loki = json.loads(price_json_Loki.text)

        search_price_url_LokiM1 = 'https://www.ceve-market.org/api/market/region/10000002/type/'
        search_price_url_LokiM1 += type_ID_LokiM1
        search_price_url_LokiM1 += '.json'

        price_json_LokiM1 = requests.get(search_price_url_LokiM1, proxies=proxies)
        price_dict_LokiM1 = json.loads(price_json_LokiM1.text)

        search_price_url_LokiM2 = 'https://www.ceve-market.org/api/market/region/10000002/type/'
        search_price_url_LokiM2 += type_ID_LokiM2
        search_price_url_LokiM2 += '.json'

        price_json_LokiM2 = requests.get(search_price_url_LokiM2, proxies=proxies)
        price_dict_LokiM2 = json.loads(price_json_LokiM2.text)

        search_price_url_LokiM3 = 'https://www.ceve-market.org/api/market/region/10000002/type/'
        search_price_url_LokiM3 += type_ID_LokiM3
        search_price_url_LokiM3 += '.json'

        price_json_LokiM3 = requests.get(search_price_url_LokiM3, proxies=proxies)
        price_dict_LokiM3 = json.loads(price_json_LokiM3.text)

        search_price_url_LokiM4 = 'https://www.ceve-market.org/api/market/region/10000002/type/'
        search_price_url_LokiM4 += type_ID_LokiM4
        search_price_url_LokiM4 += '.json'

        price_json_LokiM4 = requests.get(search_price_url_LokiM4, proxies=proxies)
        price_dict_LokiM4 = json.loads(price_json_LokiM4.text)

        ret += type_name
        ret += ':\n'
        ret += '收购:  '
        ret += num_process(price_dict_Loki['buy']['max'] + price_dict_LokiM1['buy']['max'] + price_dict_LokiM2['buy']['max'] + price_dict_LokiM3['buy']['max'] + price_dict_LokiM4['buy']['max'])
        ret += '\n'
        ret += '出售:  '
        ret += num_process(price_dict_Loki['sell']['min'] + price_dict_LokiM1['buy']['max'] + price_dict_LokiM2['buy']['max'] + price_dict_LokiM3['buy']['max'] + price_dict_LokiM4['buy']['max'])

        return ret
#########################

    if len(ID_dict) == 0:
        ret += '查无结果，好似喵啊'

    for i in range(len(ID_dict)):
        if name == ID_dict[i]['typename']:
            temp = ID_dict[0]
            ID_dict[0] = ID_dict[i]
            ID_dict[i] = temp

    for x in range(3):

        if x < len(ID_dict):

            type_ID = str(ID_dict[x]['typeid'])
            type_name = str(ID_dict[x]['typename'])

            search_price_url = 'https://www.ceve-market.org/api/market/region/10000002/type/'
            search_price_url += type_ID
            search_price_url += '.json'

            price_json = requests.get(search_price_url, proxies=proxies)
            price_dict = json.loads(price_json.text)

            ret += '\n'
            ret += type_name
            ret += ':  '
            ret += '收购:  '
            ret += num_process(price_dict['buy']['max'])
            ret += '  ||  '
            ret += '出售:  '
            ret += num_process(price_dict['sell']['min'])

    return ret


# 头像查询
def profile(name):
    proxies = {'http': None, 'https': None}

    try:
        char_url = 'https://esi.evepc.163.com/latest/search/?categories=character&datasource=serenity&language=zh&search='
        char_url += str(name) + '   '
        char_url += '&strict=true'
        char_json = requests.get(char_url, proxies=proxies)       
        char_dict = json.loads(char_json.text)
        if char_dict == {}:
            return 'None!'
    except:
        return 'None!'

    try:
        pic_url = 'https://image.evepc.163.com/Character/'
        pic_url += str(char_dict['character'][0])
        pic_url += '_1024.jpg'
        ret = pic_url
    except:
        return 'error!'

    return ret


# 角色信息查询
def character(name: str) -> str:
    proxies = {'http': None, 'https': None}

    try:
        char_url = 'https://esi.evepc.163.com/latest/search/?categories=character&datasource=serenity&language=zh&search='
        char_url += str(name) + '   '
        char_url += '&strict=true'
        char_json = requests.get(char_url, proxies=proxies)       
        char_dict = json.loads(char_json.text)
        char_ID = str(char_dict['character'][0])
    except:
        return  'None!'

    try:
        info_url = 'https://esi.evepc.163.com/latest/characters/'
        info_url += char_ID
        info_url += '/?datasource=serenity'
        info_json = requests.get(info_url, proxies=proxies)
        info_dict = json.loads(info_json.text)
        security_status = str(round(float(info_dict['security_status']), 2))
        birthday = str(info_dict['birthday']).split("T")[0]
    except:
        return ' 查询失败!'

    try:
        if 'alliance_id' in info_dict:
            alliance_ID = str(info_dict['alliance_id'])
            alliance_url = 'https://esi.evepc.163.com/latest/alliances/'
            alliance_url += alliance_ID
            alliance_url += '/?datasource=serenity'
            alliance_json = requests.get(alliance_url, proxies=proxies)
            alliance_dict = json.loads(alliance_json.text)
            alliance = str(alliance_dict['name'])
        else:
            alliance = '无联盟'
    except:
        return ' error!'

    try:
        if 'corporation_id' in info_dict:
            corporation_ID = str(info_dict['corporation_id'])
            corporation_url = 'https://esi.evepc.163.com/latest/corporations/'
            corporation_url += corporation_ID
            corporation_url += '/?datasource=serenity'
            corporation_json = requests.get(corporation_url, proxies=proxies)
            corporation_dict = json.loads(corporation_json.text)
            corporation = str(corporation_dict['name'])
        else:
            corporation = '无军团'
    except:
        return ' error!'

    ret = f"\nID: {name}\n联盟: {alliance}\n军团: {corporation}\n创建时间: {birthday}\n安全等级: {security_status}"

    return ret


# 雇佣记录查询
def history(name: str) -> str:
    ret = ' '

    proxies = {'http': None, 'https': None}

    try:
        char_url = 'https://esi.evepc.163.com/latest/search/?categories=character&datasource=serenity&language=zh&search='
        char_url += str(name) + '   '
        char_url += '&strict=true'
        char_json = requests.get(char_url, proxies=proxies)       
        char_dict = json.loads(char_json.text)
        if char_dict == {}:
            return ' 查无此角色'
        char_ID = str(char_dict['character'][0])
    except:
        return  ' error!'

    try:
        history_url = 'https://esi.evepc.163.com/latest/characters/'
        history_url += char_ID
        history_url += '/corporationhistory/?datasource=serenity'
        history_json = requests.get(history_url, proxies=proxies)
        history_dict = json.loads(history_json.text)
    except:
        return ' error!'

    try:
        dict_len = len(history_dict)
        ret += f'共查询到 {dict_len} 条记录:'
        for i in range(dict_len):
            corporation_ID = str(history_dict[i]['corporation_id'])
            corporation_url = 'https://esi.evepc.163.com/latest/corporations/'
            corporation_url += corporation_ID
            corporation_url += '/?datasource=serenity'
            corporation_json = requests.get(corporation_url, proxies=proxies)
            corporation_dict = json.loads(corporation_json.text)
            corporation = str(corporation_dict['name'])
            start_date = history_dict[i]['start_date'].split("T")[0]
            ret += f'\n{corporation} : {start_date}'
        return ret
    except:
        return ' error!'


#def distance_bd(star_search_1, star_search_2):
#
#    with open('C:\\Users\\whiteblock\\Desktop\\mirai-plu\\pyp\\systemID.json', 'r', encoding='utf8')as fp:
#        systemID = json.load(fp)
#
#    star_search_1 = difflib.get_close_matches(star_search_1.upper(), systemID)
#    if star_search_1 == []:
#        return ' 星系1不存在或关键词过短'
#    star_search_1 = star_search_1[0]
#    star_search_2 = difflib.get_close_matches(star_search_2.upper(), systemID)
#    if star_search_2 == []:
#        return ' 星系2不存在或关键词过短'
#    star_search_2 = star_search_2[0]
#
#    ret = ' '
#    proxies = {'http': None, 'https': None}
#    url = 'https://www.eve-xcs.com/sde/caldist/' + f'{star_search_1}' + '/' + f'{star_search_2}'
#    requestMsg = requests.get(url, proxies=proxies)
#    dist = requestMsg.text
#    ret += f'{star_search_1} 至 {star_search_2} 的距离为 {dist}光年'
#    return ret
#


def onejump(star_search, max_distance, min_distance = 0) -> str:

    ret = ' '
    proxies = {'http': None, 'https': None}

    url = 'https://eve.sgfans.org/navigator/ajax/auto_complete/solar_system_name?term=' + str(star_search)
    try:
        star_request = requests.get(url, proxies=proxies)
    except:
        return ' 无此起始星系'
    star_request = json.loads(star_request.text)
    try:
        star = star_request[0]['value']
        for i in range(len(star_request)):
            if star_request[i]['value'] == star_search:
                star = star_request[i]['value']
                break
    except:
        return ' 无此起始星系'

    if min_distance == 0:
        ret += str(star) + '   ' + str(max_distance) + ' 光年范围内星系: '
    else:
        ret += str(star) + '   ' + str(min_distance) + ' 至 ' + str(max_distance) + ' 光年范围内星系: '

    proxies = {'http': None, 'https': None}
    url = 'https://www.eve-xcs.com/sde/caljump/' + f'{star}' + '/10'
    requestMsg = requests.get(url, proxies=proxies)
    DIC = json.loads(requestMsg.text)
    DIC = DIC['names']
    for i in range(len(DIC)):
        if float(DIC[i]['dist']) >= float(min_distance) and float(DIC[i]['dist']) <= float(max_distance):
            ret += '\n' + str(DIC[i]['name']) + '    ' + str(DIC[i]['dist'])

    return ret


def distance(star_search_1: str, star_search_2: str) -> str:

    ret = ' '
    proxies = {'http': None, 'https': None}

    url_1 = 'https://eve.sgfans.org/navigator/ajax/auto_complete/solar_system_name?term=' + str(star_search_1)
    try:
        star_request_1 = requests.get(url_1, proxies=proxies)
    except:
        return ' 无此起始星系'
    star_request_1 = json.loads(star_request_1.text)
    try:
        star_1 = star_request_1[0]['value']
        for i in range(len(star_request_1)):
            if star_request_1[i]['value'] == star_search_1:
                star_1 = star_request_1[i]['value']
                break
    except:
        return ' 无此起始星系'

    url_2 = 'https://eve.sgfans.org/navigator/ajax/auto_complete/solar_system_name?term=' + str(star_search_2)
    try:
        star_request_2 = requests.get(url_2, proxies=proxies)
    except:
        return ' 无此终点星系'
    star_request_2 = json.loads(star_request_2.text)
    try:
        star_2 = star_request_2[0]['value']
        for i in range(len(star_request_2)):
            if star_request_2[i]['value'] == star_search_2:
                star_2 = star_request_2[i]['value']
                break
    except:
        return ' 无此终点星系'

    params = {
        "csrfmiddlewaretoken": 'SIiIPKOO5GUpHRgKBr5Cv3tDT30ho3fitLlRxMgtNlihtrF2Ykrd597dz52czfEZ',
        "start_solar_system": star_1,
        "end_solar_system": star_2
    }
    distance_url = 'https://eve.sgfans.org/navigator/a2b_distance'
    try:
        data = requests.post(url=distance_url, data=params, proxies=proxies, timeout=5)
    except:
        return ' 查询错误'

    soup = BeautifulSoup(data.text)
    try:
        dist = soup.body.main.div.find_all('td')[0].get_text()
    except:
        return ' 查询错误'

    ret += star_1 + ' 至 ' + star_2 + ' 距离为 ' + str(dist) + '光年'

    return ret


#def onejump(star_search, max_distance, min_distance = 0):
#
#    ret = ' '
#    proxies = {'http': None, 'https': None}
#
#    url = 'https://eve.sgfans.org/navigator/ajax/auto_complete/solar_system_name?term=' + str(star_search)
#    try:
#        star_request = requests.get(url, proxies=proxies)
#    except:
#        return ' 无此起始星系'
#    star_request = json.loads(star_request.text)
#    try:
#        star = star_request[0]['value']
#    except:
#        return ' 无此起始星系'
#    print(star)
#
#    if min_distance == 0:
#        ret += str(star) + '   ' + str(max_distance) + ' 光年范围内星系: '
#    else:
#        ret += str(star) + '   ' + str(min_distance) + ' 至 ' + str(max_distance) + ' 光年范围内星系: '
#
#    params = {
#        "csrfmiddlewaretoken": 'SIiIPKOO5GUpHRgKBr5Cv3tDT30ho3fitLlRxMgtNlihtrF2Ykrd597dz52czfEZ',
#        "shipType": '方舟级',
#        "CharacterJumpDriveCalibration": '5',
#        "CharacterJumpFuelConservation": '5',
#        "CharacterJumpFreighters": '5',
#        "start_solar_system": star,
#    }
#    distance_url = 'https://eve.sgfans.org/navigator/one_jump_reachable'
#    try:
#        data = requests.post(url=distance_url, data=params, proxies=proxies, timeout=5)
#    except:
#        return ' 查询错误 0'
#
#    soup = BeautifulSoup(data.text)
#    try:
#        target_list = soup.body.main.div.find_all('tbody')[1].find_all('tr')
#    except:
#        return ' 查询错误 1'
#
#    DIC = {}
#
#    for i in range(len(target_list)):
#        #ret += '\n' + target_list[i].td.get_text().replace(' ', '').replace('\n', '') + '    ' + target_list[i].find_all('td')[1].get_text().replace(' ', '').replace('\n', '')
#        DIC[target_list[i].td.get_text().replace(' ', '').replace('\n', '')] = float(target_list[i].find_all('td')[1].get_text().replace(' ', '').replace('\n', ''))
#
#    sort = sorted(DIC.items(), key=lambda x: x[1])
#    DIC = dict(list(sort))
#
#    for key, value in DIC.items():
#        if value >= float(min_distance) and value <= float(max_distance):
#            ret += '\n' + str(key) + '    ' + str(value)
#
#    return ret


# 查询星座所属星域id
def get_region_id(constellation_id: str) -> str:
    url = 'https://esi.evepc.163.com/latest/universe/constellations/{}/?datasource=serenity&language=zh'.format(constellation_id)
    r = requests.get(url)
    return r.json()['region_id']


# 查询星域名称
def get_region_name(region_id: str) -> str:
    url = 'https://esi.evepc.163.com/latest/universe/regions/{}/?datasource=serenity&language=zh'.format(region_id)
    r = requests.get(url)
    return r.json()['name']


# 查询星系名称列表
def get_solar_system_name(infested_solar_systems: str) -> list:
    solar_system_name = []
    for i in infested_solar_systems:
        url = 'https://esi.evepc.163.com/latest/universe/systems/{}/?datasource=serenity&language=zh'.format(i)
        r = requests.get(url)
        solar_system_name.append(r.json()['name'])
    return solar_system_name


# 查询eve esi中的入侵信息
def invasion() -> str:
    url = 'https://esi.evepc.163.com/latest/incursions/?datasource=serenity'
    try:
        r = requests.get(url)
    except Exception as e:
        print(e)
        return '查询失败'
    count = len(r.json())
    ret = '当前共有 ' + str(count) + ' 处入侵:'
    # 获取星座id
    for i in range(count):
        # 获取星座id
        constellation_id: str = str(r.json()[i]['constellation_id'])
        # 获取星座所属星域名称
        constellation_name: str = get_region_name(get_region_id(constellation_id))
        # 获取星系id
        infested_solar_systems: list = r.json()[i]['infested_solar_systems']
        # 获取星系名称列表
        solar_system_name: list = get_solar_system_name(infested_solar_systems)
        # 获取入侵阶段
        state: str = r.json()[i]['state']
        # 将入侵阶段转换为中文
        if state == 'mobilizing':
            state = '动员阶段'
        elif state == 'withdrawing':
            state = '撤退阶段'
        elif state == 'established':
            state = '立足阶段'
        else:
            state = '未知'
        # 获取入侵影响
        influence = str(int(r.json()[i]['influence'] * 100)) + '%'
        # 获取boss状态
        has_boss: bool = r.json()[i]['has_boss']
        boss_state = '出现' if has_boss else '未出现'
        ret += '\n' + '星域: ' + str(constellation_name) + '    ' + '星系: ' + str(solar_system_name) + '    ' + '进度: ' + str(state) + '    ' + '入侵影响: ' + str(influence) + '    ' + 'boss状态: ' + str(boss_state)

    return ret


# 服务器状态
def status() -> str:

    global server_available
    proxies = {'http': None, 'https': None}
    status_url = 'https://esi.evepc.163.com/latest/status/?datasource=serenity'
    try:
        status_json = requests.get(status_url, proxies=proxies)       
        ID_dict = json.loads(status_json.text)
    except:
        server_available = False
        return 'ESI查询超时'
    try:
        ret = "当前人数: "
        ret += str(ID_dict['players'])
        ret += "\n"
    except:
        server_available = False
        print("ESI查询超时")
    if len(ID_dict) == 4:
        ret += "维护中"
        server_available = False
    else:
        ret += "已开服"
        server_available = True

    return ret


dt: bool = False
status()
if server_available == False:
    dt = True


# 服务器状态变更检测
def status_changed() -> bool:
    global server_available
    global dt
    # 判断时间是否在维护时间内
    now = datetime.datetime.now()
    # 判断时间是否为10点
    if now.hour == 10:
        dt = True

    if now.hour >= 11 and now.hour <= 15 and dt == True:
        return False
    pre_status = server_available
    status()
    if pre_status != server_available and server_available == True:
        dt = False
        return True


# 股票
def stock(stock_code) -> str:

    ret = ' '
    headers = {'referer': 'http://finance.sina.com.cn'}
    proxies = {'http': None, 'https': None}
    res = requests.get('http://hq.sinajs.cn/list=' + stock_code, headers=headers, timeout=6, proxies=proxies)
    data = res.text
    print("\n")
    searchObj = re.match( r'(.*)=', data, re.M|re.I)
    data = data[(len(searchObj.group(1))+2):-3]

    data = data.split(',')

    ret += f'{stock_code} {data[1]}: \n'
    ret += f'实时: {data[6]}\n'
    ret += f'涨幅: {data[8]}\n'
    ret += f'今开: {data[2]}\n'
    ret += f'最高: {data[4]}'

    if stock_code == "hk03800":
        if float(data[6]) >= 4.0:
            ret += "\n0 VVV 0 超旗队集结"
        else:
            war_process = float(data[6]) / 4 * 100
            war_process = round(war_process, 2)
            ret += f"\n决战进度: {war_process}%"

    return ret


# # 龙图上传
# def add_loong(url):
#     proxies = {'http': None, 'https': None}
#     post_url = 'http://42.193.246.47:8000/post/loong/'
#     params = {
#         "url" : f"{url}"
#         }
#     try:
#         img_url = requests.post(url=post_url, data=json.dumps(params), proxies=proxies)
#         img_url = json.loads(img_url.text)
#         ret = '成功上传: ' + str(img_url['url'])
#         ret = '上传成功'
#         return ret
#     except:
#         return '上传失败了捏'

