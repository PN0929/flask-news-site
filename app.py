from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

# 設定新聞關鍵字
KEYWORDS = ["社會住宅", "國家住都中心"]

def get_google_news():
    """ 爬取 Google 新聞並回傳新聞資料 """
    news_list = []
    base_url = "https://www.google.com/search?q={query}&hl=zh-TW&tbm=nws"

    for keyword in KEYWORDS:
        url = base_url.format(query=keyword)
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        one_month_ago = datetime.now() - timedelta(days=30)

        for item in soup.select(".SoaBEf"):
            try:
                title = item.select_one(".nDgy9d").text  
                link = item.select_one(".WlydOe")["href"]  
                source = item.select_one(".NUnG9d").text  
                time_ago = item.select_one(".OSrXXb").text  

                # 轉換時間格式
                if "小時" in time_ago:
                    hours = int(time_ago.split("小時")[0])
                    pub_date = datetime.now() - timedelta(hours=hours)
                elif "天" in time_ago:
                    days = int(time_ago.split("天")[0])
                    pub_date = datetime.now() - timedelta(days=days)
                elif "週" in time_ago:
                    weeks = int(time_ago.split("週")[0])
                    pub_date = datetime.now() - timedelta(weeks=weeks)
                else:
                    pub_date = datetime.now()  

                # 過濾最近一個月內的新聞
                if pub_date >= one_month_ago:
                    news_list.append({
                        "標題": title,
                        "來源": source,
                        "時間": pub_date.strftime("%Y-%m-%d"),
                        "連結": link
                    })
            except Exception as e:
                print(f"解析錯誤: {e}")

    return news_list

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_news")
def get_news():
    """ 透過 AJAX 呼叫，爬取最新新聞並回傳 JSON """
    news_data = get_google_news()
    return jsonify(news_data)

if __name__ == "__main__":
app.run(host="0.0.0.0", port=5000, debug=True)
