from selenium import webdriver
import requests, bs4
import time
'''
option.add_extension()
download  Steam Inventory Helper https://www.crx4chrome.com/crx/16732/

webdriver.Chrome()
download webdriver for Chrome https://chromedriver.chromium.org/downloads


'''

# avtorization
def start_chrome():
    option = webdriver.ChromeOptions()
    option.add_extension(r"/home/prizrak/PycharmProjects/python/selenium/extension_1_17_21_0.crx")
    global driver
    driver = webdriver.Chrome('/home/prizrak/PycharmProjects/python/selenium/chromedriver', chrome_options=option)
    driver.get('https://steamcommunity.com/login/home/?goto=')
    name = driver.find_element_by_id("steamAccountName")
    password = driver.find_element_by_id("steamPassword")
    name.send_keys(name_steam)
    password.send_keys(password_steam)
    driver.find_element_by_id("SteamLogin").click()
    input("pres ENTER:")


class Pars_Bot:
    def __init__(self, url_links, flot, pot, max_gun):
        self.url_links = url_links
        self.pot = pot
        self.flot = flot
        self.max_gun = max_gun

    # get text and data from the site csgofloat.com
    def csgofloat(self, url):
        try:
            res = requests.get('https://api.csgofloat.com/?url=' + url)
            noStarchSoup = bs4.BeautifulSoup(res.text, "html.parser")
            return str(noStarchSoup)
        except Exception:
            print('Not open web-page')
            return ''

    # find potern and float
    def analiz(self, sait):
        try:
            result = self.csgofloat(sait)[13:-2]
            result = result.split(',')
            for i in result:
                if 'floatvalue' in i:
                    flot = float(i.split(':')[1])
                if 'paintseed' in i:
                    potern = int(i.split(':')[1])
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

    # find the best float and patern
    def inspekt_elem(self, flot, pot, max_price):
        page = True
        i_page = 1
        stop = False
        while page:
            if self.max_gun <= 0:
                break
            element = driver.find_elements_by_class_name("sih-inspect-magnifier")
            buy_keys = driver.find_elements_by_xpath(
                "//a[@class='item_market_action_button btn_green_white_innerfade btn_small']")
            price = self.get_price()
            if len(element) != len(buy_keys):
                driver.refresh()
                time.sleep(5)
                continue
            for elem in range(len(element)):
                proanaliz = self.analiz(element[elem].get_attribute('href'))
                if price[elem] == 'sold':
                    print(proanaliz[1], "  ", proanaliz[0], ' - price = ', price[elem])
                elif price[elem] <= max_price:
                    if proanaliz[0] < flot or proanaliz[1] in pot:
                        print("naideno: float = ", proanaliz[0], " :  potern = ", proanaliz[1], ' - price = ',
                              price[elem])
                        self.buy_gun(buy_keys[elem])
                        stop = True
                        break
                    else:
                        print(proanaliz[1], "  ", proanaliz[0], ' - price = ', price[elem])
                else:
                    page = False
                    break
            # Next page
            if stop == True:
                driver.refresh()
                time.sleep(3)
                i_page = 1
                stop = False
                continue
            if i_page < 4:
                driver.find_element_by_xpath("//span[@class='market_paging_pagelink'][" + str(i_page) + "]").click()
                i_page += 1
            else:
                driver.find_element_by_xpath("//span[@class='market_paging_pagelink'][4]").click()
                i_page += 1
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
        max_price = min(normal_prices) + min(normal_prices) * 0.09
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
            price_links_good = self.link_parc_gun(self.url_links)[0]
            max_price = self.link_parc_gun(self.url_links)[1]
            print("max_price - ", max_price)
            for link in price_links_good:
                driver.get(link)
                self.inspekt_elem(self.flot, self.pot, max_price)
            print('wait 3 minutes')
            time.sleep(180)
        print('________________Program end________________')


name_steam = ""
password_steam = ""
FLOOT = 0.17
MAX_BUY_GUN = 10
POT = []
url_linkss = "https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=tag_set_community_21&category_730" \
             "_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category" \
             "_730_Weapon%5B%5D=any&category_730_Exterior%5B%5D=tag_WearCategory2&category_730_Quality%5B%5D=tag" \
             "_normal&category_730_Rarity%5B%5D=tag_Rarity_Mythical_Weapon&appid=730"
# url_linkss = "https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=tag_set_community_21&category_730" \
#              "_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category" \
#              "_730_Weapon%5B%5D=any&category_730_Exterior%5B%5D=tag_WearCategory2&category_730_Quality%5B%5D=tag" \
#              "_normal&category_730_Rarity%5B%5D=tag_Rarity_Rare_Weapon&appid=730#p1_price_asc"

start_chrome()
danger_zone_collection = Pars_Bot(url_links=url_linkss, flot=FLOOT, pot=POT, max_gun=MAX_BUY_GUN)
danger_zone_collection.start_parce()
