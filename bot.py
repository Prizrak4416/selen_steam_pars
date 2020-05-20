#! /usr/bin/python3
from selenium import webdriver
import requests
import time
import sqlite3
import os


'''
option.add_extension()
download  Steam Inventory Helper https://www.crx4chrome.com/crx/16732/

webdriver.Chrome()
download webdriver for Chrome https://chromedriver.chromium.org/downloads


'''
# Open or create base

name_db = 'guns.db'
cur_dir = os.path.dirname(os.path.abspath(__file__))
path_db = os.path.join(cur_dir, name_db)
if not os.path.exists(path_db, ):
    print("create base")
    conn = sqlite3.connect(path_db)
    c = conn.cursor()
    c.execute('CREATE TABLE stocks (url text, float real, potern integer);')
    conn.commit()
else:
    conn = sqlite3.connect(path_db)
    c = conn.cursor()
    print('base is created')


# avtorization
def start_chrome():
    option = webdriver.ChromeOptions()
    option.add_extension(r"/home/prizrak/PycharmProjects/python/selenium00/extension_1_17_32_0.crx")
    global driver
    driver = webdriver.Chrome('/home/prizrak/PycharmProjects/python/selenium00/chromedriver', options=option)
    driver.get('https://steamcommunity.com/login/home/?goto=')
    name = driver.find_element_by_id("steamAccountName")
    password = driver.find_element_by_id("steamPassword")
    name.send_keys(name_steam)
    password.send_keys(password_steam)
    driver.find_element_by_id("SteamLogin").click()
    input("pres ENTER:")


class Pars_Bot:
    def __init__(self, url_links, flot, pot, max_gun, percent):
        self.url_links = url_links
        self.pot = pot
        self.flot = flot
        self.max_gun = max_gun
        self.percent = percent

    # find potern and flot
    def analiz(self, sait):
        try:
            res = requests.get('https://api.csgofloat.com/?url=' + sait, headers={'Accept': 'application/json'})
            data = res.json()
            flot = data['iteminfo']["floatvalue"]
            potern = data['iteminfo']["paintindex"]
            return [flot, potern]
        except Exception:
            print('Not get flot and potern')
            return [1, 1000]

    def get_price(self):
        price = driver.find_elements_by_xpath("//span[@class='market_listing_price market_listing_price_with_fee']")
        for i in range(len(price)):
            try:
                if ',' in price[i].text:
                    zap = price[i].text.index(',')
                    price[i] = float(price[i].text[0:zap] + '.' + price[i].text[zap + 1: -5])
                else:
                    price[i] = float(price[i].text[:-5])
            except Exception:
                price[i] = 'sold'
        return price

    def buy_gun(self, buy):
        try:
            buy.click()
            time.sleep(1)
            driver.find_element_by_xpath("//input[@id='market_buynow_dialog_accept_ssa']").click()
            driver.find_element_by_xpath("//a[@id='market_buynow_dialog_purchase']").click()
            time.sleep(4)
            driver.find_element_by_xpath("//a[@id='market_buynow_dialog_close']").click()
            time.sleep(8)
            self.max_gun -= 1
        except Exception:
            print('You cannot purchase this item because somebody else has already purchased it.')
            driver.find_element_by_xpath("//div[@class='newmodal_close with_label']").click()

    # find the best flotof and patern
    def inspekt_elem(self, flot, pot, max_price):
        page = True
        i_page = 1
        stop = False
        while page:
            if self.max_gun <= 0:
                break
            try:
                element = driver.find_elements_by_class_name("sih-inspect-magnifier")
                buy_keys = driver.find_elements_by_xpath(
                    "//a[@class='item_market_action_button btn_green_white_innerfade btn_small']")
                price = self.get_price()
            except:
                break
            if len(element) != len(buy_keys):
                driver.refresh()
                time.sleep(5)
                continue
            for elem in range(len(element)):
                ssilka = element[elem].get_attribute('href')
                select_from_base = 'SELECT url, float, potern FROM stocks WHERE url="{}";'.format(ssilka)
                c.execute(select_from_base)
                check = c.fetchone()
                # check[0] ssilka na gun,
                # check[1] float na gun,
                # check[2] potern na gun,
                if check != None:
                    proanaliz = [check[1], check[2]]
                    if price[elem] <= max_price:
                        print("\033[31m Old gun", end=" - ")
                else:
                    proanaliz = self.analiz(ssilka)
                    if proanaliz[0] != 1:
                        # zapis' v bazu dannih proverennih ssilok
                        data = (ssilka, proanaliz[0], proanaliz[1])
                        insert_in_base = 'INSERT INTO stocks VALUES (?, ?, ?);'
                        c.execute(insert_in_base, data)
                        conn.commit()
                if price[elem] <= max_price:
                    if proanaliz[0] < flot or proanaliz[1] in pot:
                        print("\033[32m naideno: float = ", proanaliz[0], " :  potern = ", proanaliz[1], ' - price = ',
                              price[elem], '\033[0m')
                        self.buy_gun(buy_keys[elem])
                        stop = True
                        break
                    else:
                        print(proanaliz[1], "  ", proanaliz[0], ' - price = ', price[elem], '\033[0m')
                else:
                    page = False
                    break
            # Next page
            if stop == True:
                driver.refresh()
                time.sleep(2)
                i_page = 1
                stop = False
                continue
            if i_page < 4:
                driver.find_element_by_xpath("//span[@class='market_paging_pagelink'][" + str(i_page) + "]").click()
                i_page += 1
                # print("----------------------Next page--", i_page, "--------------------")
            else:
                driver.find_element_by_xpath("//span[@class='market_paging_pagelink'][4]").click()
                i_page += 1
                # print("----------------------Next page too--", i_page, "-----------------------")
            time.sleep(5)

    # low price weapon search
    def link_parc_gun(self, url_linkss):
        driver.get(url_linkss)
        time.sleep(3)
        market_listing_row_link = driver.find_elements_by_xpath("//a[@class='market_listing_row_link']")
        normal_prices = driver.find_elements_by_xpath("//span[@class='normal_price']")
        for i in range(len(normal_prices)):
            if ',' in normal_prices[i].text:
                zap = normal_prices[i].text.index(',')
                normal_prices[i] = float(normal_prices[i].text[0:zap] + '.' + normal_prices[i].text[zap + 1: -5])
            else:
                normal_prices[i] = float(normal_prices[i].text[:-5])
            market_listing_row_link[i] = market_listing_row_link[i].get_attribute('href')
        # max price
        max_price = min(normal_prices) + min(normal_prices) * self.percent
        price_links = list(zip(normal_prices, market_listing_row_link))
        price_links_good = []
        for j in price_links:
            if j[0] < max_price:
                price_links_good.append(j)
        for i in range(len(price_links_good)):
            price_links_good[i] = price_links_good[i][1]
        return [price_links_good, max_price]

    def start_parce(self):
        while self.max_gun > 0:
            for i in self.url_links:
                try:
                    parc_gun = self.link_parc_gun(i)
                    price_links_good = parc_gun[0]
                    max_price = parc_gun[1]
                    print("max_price - ", max_price)
                    for link in price_links_good:
                        driver.get(link)
                        self.inspekt_elem(self.flot, self.pot, max_price)
                    if self.max_gun < 1:
                        break
                except:
                    continue
            print('\n\n')
            print('wait 30 sec')
            time.sleep(30)
        print('________________Program end________________')


name_steam = ""
password_steam = ""
FLOOT = 0.17
MAX_BUY_GUN = 2
POT = []
MAX_PRICE_GUN_PERCENT = 0.04



# ----------------------------SG 553 | Colony IV-----------------------------------------------------------
url_linkss5 = "https://steamcommunity.com/market/search?category_730_ProPlayer%5B0%5D=any&category_730_StickerCapsule%" \
              "5B0%5D=any&category_730_TournamentTeam%5B0%5D=any&category_730_Weapon%5B0%5D=any&category_730_Exterior%5B0%5D=tag" \
              "_WearCategory2&category_730_Quality%5B0%5D=tag_normal&appid=730&q=Colony+IV"
url_linkss1 = "https://steamcommunity.com/market/search?q=SSG+08+%7C+Bloodshot&category_730_ItemSet%5B%5D=any&catego" \
              "ry_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any" \
              "&category_730_Weapon%5B%5D=any&category_730_Exterior%5B%5D=tag_WearCategory2&category_730_Quality%5B%5" \
              "D=tag_normal&appid=730"

url_test = "https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=tag_set_community_21&category_730" \
            "_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&categor" \
            "y_730_Weapon%5B%5D=any&category_730_Exterior%5B%5D=tag_WearCategory2&category_730_Quality%5B%5D=tag_norm" \
            "al&category_730_Rarity%5B%5D=tag_Rarity_Rare_Weapon&appid=730#p1_price_asc"

url_linkss = [url_linkss5, url_linkss1]

start_chrome()
danger_zone_collection = Pars_Bot(url_links=url_linkss,
                                  flot=FLOOT,
                                  pot=POT,
                                  max_gun=MAX_BUY_GUN,
                                  percent=MAX_PRICE_GUN_PERCENT)
danger_zone_collection.start_parce()
