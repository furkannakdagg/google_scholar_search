import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import warnings
warnings.filterwarnings("ignore")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
pd.set_option('display.width', 500)

driver_path = "/Users/furkanakdag/Desktop/loto_analysis/chromedriver"
driver = webdriver.Chrome(driver_path)
driver.get("https://scholar.google.com")

########################
# İstenilen Key'i Arama
########################
# search_keys = input("Enter Keys")
search_keys = "machine learning"
driver.find_element(by=By.NAME, value="q").send_keys(search_keys + Keys.ENTER)

#######################
# Yıl Aralıklarını Gir
#######################
driver.find_element(by=By.ID, value="gs_res_sb_yyc").click()  # "Özel Aralık" seçeneğine bas
driver.find_element(by=By.XPATH, value='//*[@id="gs_res_sb_yyf"]/div[@class="gs_res_sb_yyr"]/div[1]/input').send_keys(
    "2017")
# driver.find_element(by=By.ID, value="gs_as_ylo").send_keys("2017")  => bu şekilde de alınabilir
driver.find_element(by=By.XPATH, value='//*[@id="gs_res_sb_yyf"]/div[@class="gs_res_sb_yyr"]/div[2]/input').send_keys(
    "2022")
driver.find_element(by=By.XPATH, value='//*[@id="gs_res_sb_yyf"]/div[2]/button').click()  # "Ara" butonuna bas

# Makaleleri İncele
driver.find_element(by=By.XPATH, value='//*[@id="gs_bdy_sb_in"]/ul[3]/li[2]').click()

df = pd.DataFrame(columns=["Article Type", "Title", "Authors", "Paper", "Year", "URL"])
def article_process(dataframe):
    # Makale Linkleri
    article_title = driver.find_elements(by=By.XPATH, value='//*[@class="gs_ri"]/h3[@class="gs_rt"]')
    article_info = driver.find_elements(by=By.XPATH, value='//*[@id="gs_res_ccl_mid"]/div[@class="gs_r gs_or gs_scl"]'
                                                           '/div[@class="gs_ri"]/div[@class="gs_a"]')
    article_types = driver.find_elements(by=By.XPATH, value='//*[@class="gs_r gs_or gs_scl"]')
    articles_url = driver.find_elements(by=By.XPATH, value='//*[@class="gs_ri"]/h3[@class="gs_rt"]/a[@href]')

    for ty, i, tit, url in zip(article_types, article_info, article_title, articles_url):
        # Type
        if "PDF" in ty.text.split("\n")[0]:
            art_type = "PDF"
        elif "HTML" in ty.text.split("\n")[0]:
            art_type = "HTML"
        else:
            art_type = "Unspecified"

        # Authors
        authors = i.text.split("-")[0].strip()

        # Paper
        journal_info = i.text.split("-")[1]
        paper = journal_info.split(",")[0].strip()
        year = journal_info.split(",")[1].strip()

        # Title
        if "PDF" in tit.text:
            title = tit.text.strip("[PDF] ")
        elif "HTML" in tit.text:
            title = tit.text.strip("[HTML] ")
        else:
            title = tit.text.strip()

        # URL
        article_url = url.get_attribute("href")

        new_art = pd.DataFrame({"Article Type": art_type,
                                "Title": title,
                                "Authors": authors,
                                "Paper": paper,
                                "Year": year,
                                "URL": article_url}, index=[0])
        dataframe = pd.concat([dataframe, new_art], axis=0, ignore_index=True)
    return dataframe


# Kaç sayfa gitmek istiyoruz
num_of_pages = 2
for _ in range(num_of_pages):
    df = article_process(df)
    driver.find_element(By.XPATH, '//*[@id="gs_n"]/center/table/tbody/tr/td[12]/a/b').click()
