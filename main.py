from selenium import webdriver
from selenium.webdriver.common.by import By
import telebot
import time
from config import TOKEN, CHAT_ID
import pytz
from pytz import timezone
from datetime import datetime
import pickle
import schedule

bot = telebot.TeleBot(TOKEN)
price_list = ['', '']
discount_list = ['', '']

class Parser:
    def go_to_browser(self):
        url = "https://www.wildberries.ru/catalog/88848742/detail.aspx?targetUrl=GP"
        url_2 = "https://seller.wildberries.ru/"
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1200')
        self.driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
        self.driver.get(url=url)
        time.sleep(5)
        for cookie in pickle.load(open("cookies", "rb")):
            self.driver.add_cookie(cookie)
        time.sleep(5)
        self.driver.refresh()
        time.sleep(2)
        self.handle = self.driver.current_window_handle
        self.driver.execute_script("window.open('about:blank','secondtab');")
        self.driver.switch_to.window("secondtab")
        self.driver.get(url=url_2)
        time.sleep(2)
        self.driver.refresh()
        time.sleep(5)
        self.driver.switch_to.window(self.handle)
        self.location = pytz.timezone("Europe/Moscow")
        time.sleep(2)
        print(price_list)

    # проверить на хостинге

    def get_stats(self):
        self.driver.switch_to.window("secondtab")
        time.sleep(3)
        self.driver.refresh()
        time.sleep(8)
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div/div/div/ul/li[1]/span/div/div[2]/div/div/div/div[3]/ul/li[1]/a").click()
        time.sleep(3)
        orders_count = self.driver.find_element(By.XPATH,
                                                     "/html/body/div[1]/div/div[1]/div[1]/div/div/div/ul/li[1]/span/div/div[2]/div/div/div/div[1]/div[2]/div/span[2]/span").text
        time.sleep(4)
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div/div/div/ul/li[1]/span/div/div[2]/div/div/div/div[3]/ul/li[2]/a").click()
        time.sleep(4)
        ransoms_count = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div/div/div/ul/li[1]/span/div/div[2]/div/div/div/div[1]/div[2]/div/span[2]/span").text
        time.sleep(4)
        bot.send_message(chat_id=CHAT_ID, text=f"➥Количество заказов: {orders_count} (+)\n➥Количество выкупов: {ransoms_count} (+)")


    def parse(self):
        self.driver.switch_to.window(self.handle)
        time.sleep(3)
        self.driver.refresh()
        time.sleep(5)
        moscow_time = datetime.now(self.location).strftime("%m/%d/%Y, %H:%M:%S")
        time.sleep(6)
        item_price = self.driver.find_element(By.XPATH,
                                              "//div[@class='product-page__price-block product-page__price-block--aside']//ins[@class='price-block__final-price']").text
        self.driver.find_element(By.XPATH, "//div[@class='product-page__price-block product-page__price-block--aside']//del[@class='price-block__old-price j-final-saving j-wba-card-item-show']").click()
        time.sleep(1)
        item_discount = self.driver.find_element(By.XPATH, "//div[@class='tooltip i-tooltip-add-discount']//p[3]//span").text
        if item_price not in price_list:
            price_list[0] = item_price
            print(price_list)
            bot.send_message(chat_id=CHAT_ID,
                         text=f"╔════════════════╗\n  📅 {moscow_time}\n\n➥ Цена изменилась на : \n{item_price} \n\n➥ СПП сейчас: {item_discount[:-3]}\n╚════════════════╝")
        if item_discount not in discount_list:
            discount_list[0] = item_discount
            print(discount_list)
            bot.send_message(chat_id=CHAT_ID,
                         text=f"╔════════════════╗\n  📅 {moscow_time}\n\n➥ СПП изменилась на : \n{item_discount[:-3]} \n\n➥ Цена сейчас: {item_price}\n╚════════════════╝")


    def main(self):
        self.go_to_browser()
        schedule.every(30).seconds.do(self.get_stats)
        schedule.every().minute.at(":59").do(self.parse)
        while True:
            schedule.run_pending()




if __name__ == "__main__":
    p = Parser()
    p.main()
    schedule.every().day.at("00:00", timezone("Europe/Moscow")).do(p.main())
    while True:
        schedule.run_pending()