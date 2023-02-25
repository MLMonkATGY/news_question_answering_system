import requests
from bs4 import BeautifulSoup
from loguru import logger
import time

from playwright.sync_api import Playwright, sync_playwright
from tqdm import tqdm
from src.scrape.db import Raw_Data
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import Session
from dataclasses import dataclass


@dataclass
class News_Raw_Data:
    title: str = None
    news_creation_time: str = None
    content: str = None


def scrape_malaysiakini(response_html):
    # "https://www.malaysiakini.com/news/656427"
    # cookie = {
    #     "nl____accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7InVzZXJfaWQiOiJFNzQ2dDFZUHE3eTU4SE1NUVNmWCIsImVtYWlsIjoiYWxleHRheWdlZXlhbmc5NkBnbWFpbC5jb20iLCJmdWxsbmFtZSI6Ik1hbGF5c2lha2luaSBSZWFkZXIiLCJsYXN0bmFtZSI6bnVsbCwic3RhdHVzIjoyLCJ1c2VybmFtZSI6bnVsbCwiZXhwaXJ5X2RhdGUiOm51bGwsImV4cGlyeV9kYXRlaCI6IjI1LTA1LTIwMjMiLCJzdWJzY3JpcHRpb25fZW5kIjoxNjg0OTc4NDcwLCJ2ZXJzaW9uIjoyLCJwYWNrYWdlX25hbWUiOiIzIE1vbnRocyBSTTYwICggUmVjdXIgKSIsInBhY2thZ2VfaWQiOiJsc1h3UE9wZjg2dE1vRFozb1V6diIsInBob25lX25vIjpudWxsLCJzdHJpcGVJZCI6ImN1c19OUTJrVDhOUEJ0eDJPQyIsImNyZWF0ZWRBdCI6MTY3NzMwNTg3OCwiaXNfcmVjdXJyaW5nIjp0cnVlLCJpc19yZWN1cnJpbmdfY2FuY2VsbGluZyI6ZmFsc2UsImlzTWFuYWdlZEJ5R3JvdXAiOmZhbHNlLCJncm91cElkIjpudWxsLCJncm91cE5hbWUiOm51bGwsImxvZ2luTWV0aG9kIjoiTE9DQUwifSwiaWF0IjoxNjc3MzA1ODc4LCJleHAiOjE2NzczMDY3Nzh9.NMopJKZqLr9dxSNCCS7pVp06EQ6hQFTaMl4u_sywhTM",
    #     "nl____refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiamNEdEJZTmVYbjA2WWpNSGp5dWMiLCJpYXQiOjE2NzczMDQ5MzEsImV4cCI6MTY4NTA4MDkzMX0.RMMOj1bzz8DPhL9wyPPFmG0yP12KIVPSCe_XGyx_DrQ",
    #     "ncpush_hide_mk": "yes",
    # }

    soup = BeautifulSoup(response_html, "html.parser")
    title_div = soup.find(
        "div",
        {
            "class": "text-3xl font-semibold leading-snug text-coolGray-600 mt-2 tracking-normal print:text-lg"
        },
    )
    content_div = soup.find(
        "div",
        {"id": "full-content-container"},
    )
    news_creation_div = soup.find(
        "div",
        {
            "class": "flex flex-wrap items-center text-xs lg:text-sm opacity-90 font-normal"
        },
    )
    title_text = ""
    article_text = ""
    news_creation_date_txt = ""
    if title_div is not None:
        title_text = title_div.get_text().replace("\n", "") + ". "
    if content_div is not None:
        article_text = content_div.get_text() + ". "
    if news_creation_div is not None:
        news_creation_date_txt = news_creation_div.get_text().replace("\n", "") + ". "
    if len(article_text) == 0:
        logger.warning("")
    logger.success(article_text)

    return News_Raw_Data(
        title=title_text,
        content=article_text,
        news_creation_time=news_creation_date_txt,
    )
    # logger.error(url)


def malaysiakini_scheduler():
    template = "https://www.malaysiakini.com/news/###"
    newsId = 656426
    username = "alextaygeeyang96@gmail.com"
    password = "Iamalextay96"
    engine = create_engine(
        "postgresql://postgres:Iamalextay96@192.168.1.3:5433/nlp",
        echo=False,
        connect_args={"connect_timeout": 0},
    )
    with Session(engine) as session:
        last_news_query = (
            select(Raw_Data)
            .where(Raw_Data.source.contains("malaysiakini.com"))
            .order_by(Raw_Data.source)
            .limit(2)
        )
        last_news_result = session.scalars(last_news_query).all()
        last_news_id = int(last_news_result[0].source.split("/")[-1])
        newsId = last_news_id
        logger.success(f"Starting from last news id : {newsId}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(
                "https://membership.malaysiakini.com/auth/local?redirectUrl=https://www.malaysiakini.com/&flow=normal&lang=en"
            )
            page.wait_for_timeout(1000)

            username_selector = "#__next > div > div > div > div.jsx-2450343050.banner-card-content > form > div:nth-child(1) > input"
            password_selector = "#__next > div > div > div > div.jsx-2450343050.banner-card-content > form > div:nth-child(2) > input"
            enter_div = "#__next > div > div > div > div.jsx-2450343050.banner-card-content > form > div.jsx-1504941063.floating-action > div.jsx-2309431947.floating-button > button"
            page.locator(username_selector).fill(username)
            page.locator(password_selector).fill(password)
            page.locator(enter_div).click()
            page.wait_for_timeout(2000)
            for i in tqdm(range(20000)):
                targetUrl = template.replace("###", f"{newsId - i}")
                page.goto(targetUrl)
                parsed_news = scrape_malaysiakini(page.content())
                newData = Raw_Data(
                    source=targetUrl,
                    content=parsed_news.content,
                    remarks="",
                    title=parsed_news.title,
                    news_creation_date=parsed_news.news_creation_time,
                )

                session.add_all([newData])
                session.commit()
                time.sleep(0.5)


if __name__ == "__main__":
    malaysiakini_scheduler()
