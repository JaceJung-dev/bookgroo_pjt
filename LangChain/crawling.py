import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin

# 기본 설정
base_url = "https://www.yes24.com"
data = []
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 크롤링 실행
for i in range(1, 5):
    url = f"https://www.yes24.com/Product/Category/NewProduct?pageNumber={i}"
    print(f"📄 [페이지 {i}] 크롤링 시작]")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ [페이지 {i}] 요청 실패: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.select(".item_info")

    for book_index, book in enumerate(books, start=1):
        print(f"🔍 [페이지 {i} - 책 {book_index}] 데이터 수집 중...")

        category_element = book.select_one(".gd_res")
        if not category_element or "[도서]" not in category_element.text:
            print(f"   ⏩ [페이지 {i} - 책 {book_index}] 도서가 아님, 건너뜀")
            continue

        title_element = book.select_one("a.gd_name")
        if not title_element:
            print(f"   ⚠️ [페이지 {i} - 책 {book_index}] 제목 없음, 건너뜀")
            continue

        title = title_element.text.strip()
        href = title_element["href"]
        if href.startswith("https"):
            print(f"   ⏩ [페이지 {i} - 책 {book_index}] 절대 URL, 건너뜀: {href}")
            continue

        detail_url = urljoin(base_url, href)
        author_element = book.select_one(
            "div.info_row.info_pubGrp > span.info_auth > a:not(.moreAuthArea a)"
        )
        author = author_element.text.strip() if author_element else "저자 없음"
        publisher_element = book.select_one(
            "div.info_row.info_pubGrp > span:nth-of-type(2)"
        )
        publisher = (
            publisher_element.text.strip() if publisher_element else "출판사 없음"
        )
        pub_date_element = book.select_one(
            "div.info_row.info_pubGrp > span:nth-of-type(3)"
        )
        pub_date = pub_date_element.text.strip() if pub_date_element else "출판일 없음"

        description = "설명 없음"
        genres = "장르 없음"
        if detail_url:
            try:
                detail_response = requests.get(detail_url, headers=headers, timeout=10)
                detail_response.raise_for_status()
                detail_soup = BeautifulSoup(detail_response.text, "html.parser")

                # 책 설명
                detail_description = detail_soup.select_one("textarea.txtContentText")
                description = (
                    detail_description.text.strip()
                    if detail_description
                    else "설명 없음"
                )

                # 장르 데이터 추출 (올바른 yesAlertLi 선택)
                genre_section = detail_soup.select_one(
                    "dl.yesAlertDl ul.yesAlertLi"
                )  # 정확한 부모 요소 선택
                if genre_section:
                    genre_list = genre_section.select_one("li")  # 첫 번째 li 선택
                    if genre_list:
                        genre_elements = genre_list.select(
                            "a"
                        )  # 첫 번째 li 내부의 a 태그 가져오기
                        genres = (
                            ", ".join([g.text.strip() for g in genre_elements])
                            if genre_elements
                            else "장르 없음"
                        )
                    else:
                        genres = "장르 없음"
                else:
                    genres = "장르 없음"
            except requests.exceptions.RequestException as e:
                print(f"   ⚠️ [페이지 {i} - 책 {book_index}] 상세 페이지 요청 실패: {e}")

        print(f"✅ [페이지 {i} - 책 {book_index}] 수집 완료: {title} ({author})")
        data.append([title, author, publisher, pub_date, genres, description])

    time.sleep(random.uniform(1, 3))

# 결과 저장
df = pd.DataFrame(
    data, columns=["title", "author", "publisher", "pub_date", "genres", "description"]
)
df.to_csv("data/result_final_with_genres_test.csv", index=False, encoding="utf-8-sig")
