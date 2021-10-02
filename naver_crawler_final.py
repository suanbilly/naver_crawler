# 네이버 크롤러 Version 1.0
from bs4 import BeautifulSoup #html 읽기
from selenium import webdriver #chrome연결
import time #시간
import sys
from selenium.webdriver.common.keys import Keys #스크롤,페이지다운
import pandas as pd #정보 표형태로 만듦
import os #폴더생성
import shutil #폴더, 파일삭제
import math
import jw #개인모듈


class Searcher:
    def naver(self):
        print("="*80)
        print(f'{"네이버크롤러 version 1.0": ^65}')
        print("="*80)
        # 검색어 입력받기
        while True:
            self.search = input("검색어를 입력해주세요. > ")
            print('='*80)
            if self.search == '':
                print("크롤링할 검색어를 입력해주세요.")
                print('='*80)
                continue
            else:
                break

        # 크롬으로 네이버 연결
        path = "C:\python_temp\chromedriver_win32\chromedriver.exe"
        self.driver = webdriver.Chrome(path)
        self.driver.get("https://www.naver.com")

        # 전체화면으로 변환
        self.driver.maximize_window()
        time.sleep(1)

        # 검색어 입력 후 검색버튼 클릭
        element = self.driver.find_element_by_class_name("input_text")
        element.send_keys(self.search)
        self.driver.find_element_by_class_name("btn_submit").click()
        time.sleep(1)


class Crawler(Searcher):
    # 동일 저장리스트
    no2 = []
    title2 = []
    content2 = []
    # 카페와 블로그만 동일
    writer2 = []
    dates2 = []
    # 다른 저장리스트들
    sources = []
    dic2 = []
    s_title2 = []

    ###### 블로그 #######
    def blog(self):
        # 리스트 비우기
        self.no2.clear()
        self.writer2.clear()
        self.title2.clear()
        self.content2.clear()
        self.dates2.clear()

        JW = jw.JW()
        JW.view(self.search, self.driver)
        self.no2 = JW.no2
        self.title2 = JW.titles
        self.content2 = JW.contents
        self.writer2 = JW.writers
        self.dates2 = JW.dates

        # 표형태로 정보 변환
        self.data = pd.DataFrame()
        self.data['번호'] = self.no2
        self.data['제목'] = self.title2
        self.data['내용'] = self.content2
        try:
            self.data['작성일'] = self.dates2
        except:
            pass
        self.data['작성자'] = self.writer2

        # 통합으로 돌아가기
        self.driver.find_element_by_xpath(
            '//*[@id="lnb"]/div[1]/div/ul/li[1]/a').click()

    ###### 뉴스 #######
    def news(self):
        global no2
        global writer2
        global title2
        global content2
        global dates2

        # 리스트 비우기
        self.no2.clear()
        self.writer2.clear()
        self.title2.clear()
        self.content2.clear()
        self.dates2.clear()
        time.sleep(2)

        try:
            # 페이지 링크 가져오기
            self.driver.find_element_by_css_selector(
                '#main_pack > section.sc_new.sp_nnews._prs_nws_all > div > div.api_more_wrap > a').click()
        except:
            print("뉴스 정보가 없습니다.")
            print("="*80)
        else:
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            try:
                div = soup.find("div", class_="group_news")
                data_list = []
                data = div.find_all("li", "bx")
            except AttributeError:
                print("정보가 없습니다.")
                print("="*80)
            else:
                # 크롤링할 개수 입력받기
                self.save_num = int(input("크롤링할 글 개수를 입력해주세요: "))
                print('\n')

                # 개수만큼 페이지 넘기기

                for page in range(2, math.ceil(self.save_num/10)+2):
                    html = self.driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')

                    div = soup.find("div", class_="group_news")
                    data = div.find_all("li", "bx")
                    for i in data:
                        if len(data_list) == self.save_num:
                            break
                        else:
                            data_list.append(i)

                    self.driver.find_element_by_xpath(
                        '//*[@id="main_pack"]/div[2]/div/div/a[%d]' % page).click()
                    time.sleep(1)

                # 시작시간
                s_time = time.time()
                # 반복문으로 입력받은 개수만큼 정보 추출하기
                no = 1
                for i in data_list:
                    if no <= self.save_num:
                        try:
                            title = i.find(
                                'a', class_="news_tit").get_text().strip()
                        except AttributeError:
                            title = '제목이 없습니다.'
                            self.title2.append(title)
                            print("2) 게시글 제목:", title)
                        else:
                            self.no2.append(no)
                            print("1) 글 번호:", no)
                            no += 1
                            self.title2.append(title)
                            print("2) 게시글 제목:", title)

                        try:
                            content = i.find(
                                'a', class_="api_txt_lines dsc_txt_wrap").get_text().strip()
                        except AttributeError:
                            content = '내용이 없습니다.'
                            self.content2.append(content)
                            print("3) 게시글 요약내용:", content)
                        else:
                            self.content2.append(content)
                            print("3) 게시글 요약내용:", content)

                        try:
                            dates = i.find(
                                'span', class_="info").get_text().strip()
                        except AttributeError:
                            dates = '내용이 없습니다.'
                            self.dates2.append(dates)
                            print("4) 게시글 작성날짜:", dates)
                        else:
                            self.dates2.append(dates)
                            print("4) 게시글 작성날짜:", dates)

                        try:
                            writer = i.find(
                                'a', class_="info press").get_text().strip()
                        except AttributeError:
                            writer = '내용이 없습니다.'
                            self.writer2.append(writer)
                            print("5) 언론사:", writer)
                        else:
                            self.writer2.append(writer)
                            print("5) 언론사:", writer)
                            print('\n')
                    else:
                        break

                time.sleep(2)
                print(f"""크롤링이 완료되었습니다.\n크롤링된 글의 개수는 {len(self.no2)}입니다.\n""")

                # 작업시간 표시
                e_time = time.time()
                t_time = e_time-s_time
                print('='*80)
                print('출력에 걸린시간은 %s초 입니다' % round(t_time, 1))
                print('='*80)

                # 표형태로 정보 변환
                self.data = pd.DataFrame()
                self.data['번호'] = self.no2
                self.data['제목'] = self.title2
                self.data['내용'] = self.content2
                self.data['작성일'] = self.dates2
                self.data['언론사'] = self.writer2

                # 통합페이지로 돌아가기
                self.driver.execute_script("window.scrollTo(0, 0)")
                time.sleep(2)
                self.driver.find_element_by_xpath(
                    '//*[@id="lnb"]/div[1]/div/ul/li[1]/a').click()

    def news_text(self):
        try:
            # 페이지 링크 가져오기
            self.driver.find_element_by_css_selector(
                '#main_pack > section.sc_new.sp_nnews._prs_nws_all > div > div.api_more_wrap > a').click()
        except:
            print("뉴스 정보가 없습니다.")
            print("="*80)
        else:
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            try:
                div = soup.find("div", class_="group_news")
                data_list = []
                data = div.find_all("li", "bx")
            except AttributeError:
                print("정보가 없습니다.")
                print("="*80)
            else:
                # 개수만큼 페이지 넘기기
                for page in range(2, math.ceil(self.save_num/10)+2):
                    html = self.driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')

                    div = soup.find("div", class_="group_news")
                    data = div.find_all("li", "bx")
                    for i in data:
                        if len(data_list) == self.save_num:
                            break
                        else:
                            data_list.append(i)

                    self.driver.find_element_by_xpath(
                        '//*[@id="main_pack"]/div[2]/div/div/a[%d]' % page).click()
                    time.sleep(1)

                # 반복문으로 입력받은 개수만큼 정보 추출하기
                no = 1
                for i in data_list:
                    if no <= self.save_num:
                        try:
                            title = i.find(
                                'a', class_="news_tit").get_text().strip()
                        except AttributeError:
                            title = '제목이 없습니다.'
                            print("2) 게시글 제목:", title)
                        else:
                            print("1) 글 번호:", no)
                            no += 1
                            print("2) 게시글 제목:", title)

                        try:
                            content = i.find(
                                'a', class_="api_txt_lines dsc_txt_wrap").get_text().strip()
                        except AttributeError:
                            content = '내용이 없습니다.'
                            print("3) 게시글 요약내용:", content)
                        else:
                            print("3) 게시글 요약내용:", content)
                        try:
                            dates = i.find(
                                'span', class_="info").get_text().strip()
                        except AttributeError:
                            dates = '내용이 없습니다.'
                            print("4) 게시글 작성날짜:", dates)
                        else:
                            print("4) 게시글 작성날짜:", dates)

                        try:
                            writer = i.find(
                                'a', class_="info press").get_text().strip()
                        except AttributeError:
                            writer = '내용이 없습니다.'
                            print("5) 언론사:", writer)
                        else:
                            print("5) 언론사:", writer)
                            print('\n')
                    else:
                        break

                # 통합페이지로 돌아가기
                self.driver.execute_script("window.scrollTo(0, 0)")
                time.sleep(2)
                self.driver.find_element_by_xpath(
                    '//*[@id="lnb"]/div[1]/div/ul/li[1]/a').click()

    ###### 카페 #######
    def cafe(self):
        global no2
        global writer2
        global title2
        global content2
        global dates2

        # 리스트 비우기
        self.no2.clear()
        self.writer2.clear()
        self.title2.clear()
        self.content2.clear()
        self.dates2.clear()
        time.sleep(2)

        # 페이지 링크 가져오기
        full_html = self.driver.page_source
        # 페이지 해석
        soup = BeautifulSoup(full_html, 'html.parser')
        # VIEW카테고리에 카페글로 가기
        self.driver.find_element_by_link_text("VIEW").click()
        time.sleep(1)
        self.driver.find_element_by_link_text("카페").click()
        time.sleep(1)

        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        try:
            div = soup.find("div", class_="api_subject_bx")
            data_list = div.select('ul > li')
        except AttributeError:
            print("정보가 없습니다.")
            print("="*80)
        else:
            # 크롤링할 개수 입력받기
            self.save_num = int(input("크롤링할 글 개수를 입력해주세요: "))
            print('\n')

            # 개수만큼 스크롤 내리기
            body = self.driver.find_element_by_css_selector('body')
            while len(data_list) < self.save_num:
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(1)

                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                div = soup.find("div", class_="api_subject_bx")
                data_list = div.select('ul > li')

            # 시작시간
            s_time = time.time()
            # 반복문으로 입력받은 개수만큼 정보 추출하기
            no = 1
            for i in data_list:
                if no <= self.save_num:
                    try:
                        title = i.find(
                            'a', class_="api_txt_lines total_tit").get_text().strip()
                        content = i.find(
                            'div', class_="api_txt_lines dsc_txt").get_text().strip()
                        dates = i.find(
                            'span', class_="sub_time sub_txt").get_text().strip()
                        writer = i.find(
                            'a', class_="sub_txt sub_name").get_text().strip()
                    except AttributeError:
                        title = '제목이 없습니다.'
                        self.title2.append(title)
                        print("2) 게시글 제목:", title)
                        content = '내용이 없습니다.'
                        self.content2.append(content)
                        print("3) 게시글 요약내용:", content)
                        print('\n')
                    else:
                        self.no2.append(no)
                        print("1) 글 번호:", no)
                        self.title2.append(title)
                        print("2) 게시글 제목:", title)
                        self.content2.append(content)
                        print("3) 게시글 요약내용:", content)
                        self.dates2.append(dates)
                        print("4) 게시글 작성날짜:", dates)
                        self.writer2.append(writer)
                        print("5) 카페명:", writer)
                        print('\n')
                        no += 1
                else:
                    break

            time.sleep(2)
            print(f"""크롤링이 완료되었습니다.\n크롤링된 글의 개수는 {len(self.no2)}입니다.\n""")

            # 작업시간 표시
            e_time = time.time()
            t_time = e_time-s_time
            print('='*80)
            print('출력에 걸린시간은 %s초 입니다' % round(t_time, 1))
            print('='*80)

            # 표형태로 정보 변환
            self.data = pd.DataFrame()
            self.data['번호'] = self.no2
            self.data['제목'] = self.title2
            self.data['내용'] = self.content2
            self.data['작성일'] = self.dates2
            self.data['카페명'] = self.writer2
            # 통합페이지로 돌아가기
            self.driver.execute_script("window.scrollTo(0, 0)")
            time.sleep(2)
            self.driver.find_element_by_xpath(
                '//*[@id="lnb"]/div[1]/div/ul/li[1]/a').click()

    ###### 카페 텍스트 저장 #######
    def cafe_text(self):
        global no2
        global writer2
        global title2
        global content2
        global dates2

        # 페이지 링크 가져오기
        full_html = self.driver.page_source
        # 페이지 해석
        soup = BeautifulSoup(full_html, 'html.parser')
        # VIEW카테고리에 카페글로 가기
        self.driver.find_element_by_link_text("VIEW").click()
        time.sleep(1)
        self.driver.find_element_by_link_text("카페").click()
        time.sleep(1)

        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        try:
            div = soup.find("div", class_="api_subject_bx")
            data_list = div.select('ul > li')
        except AttributeError:
            print("정보가 없습니다.")
        else:
            # 개수만큼 스크롤 내리기
            body = self.driver.find_element_by_css_selector('body')
            while len(data_list) < self.save_num:
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(1)

                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                div = soup.find("div", class_="api_subject_bx")
                data_list = div.select('ul > li')

            # 반복문으로 개수만큼 정보 추출하기
            no = 1
            for i in data_list:
                if no <= self.save_num:
                    try:
                        title = i.find(
                            'a', class_="api_txt_lines total_tit").get_text().strip()
                        content = i.find(
                            'div', class_="api_txt_lines dsc_txt").get_text().strip()
                        dates = i.find(
                            'span', class_="sub_time sub_txt").get_text().strip()
                        writer = i.find(
                            'a', class_="sub_txt sub_name").get_text().strip()
                    except AttributeError:
                        title = '제목이 없습니다.'
                        print("2) 게시글 제목:", title)
                        content = '내용이 없습니다.'
                        print("3) 게시글 요약내용:", content)
                        print('\n')
                    else:
                        print("1) 글 번호:", no)
                        print("2) 게시글 제목:", title)
                        print("3) 게시글 요약내용:", content)
                        print("4) 게시글 작성날짜:", dates)
                        print("5) 카페명:", writer)
                        print('\n')
                        no += 1
                else:
                    break
            time.sleep(2)

            # 통합페이지로 돌아가기
            self.driver.execute_script("window.scrollTo(0, 0)")
            time.sleep(2)
            self.driver.find_element_by_xpath(
                '//*[@id="lnb"]/div[1]/div/ul/li[1]/a').click()

    ###### 백과사전 #######
    def know(self):
        global no2
        global title2
        global content2
        global sources
        global s_title2

        # 리스트 비우기
        self.no2.clear()
        self.title2.clear()
        self.content2.clear()
        self.sources.clear()
        self.s_title2.clear()
        time.sleep(2)

        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        encyclopedia = soup.find_all(
            'section', 'sc_new sp_nkindic _au_kindic_collection')

        # 시작시간
        s_time = time.time()

        # 지식백과가 없을 시
        if len(encyclopedia) == 0:
            self.driver.find_element_by_xpath(
                '//*[@id="_nx_lnb_more"]/a').click()
            time.sleep(1)
            self.driver.find_element_by_xpath(
                '//*[@id="_nx_lnb_more"]/div/ul/li[2]/a').click()
            encyclopedia = soup.find_all('div', 'nkindic_area')
            print()

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            encyclopedia = soup.find_all(
                'section', 'sc_new sp_nkindic _au_kindic_collection')

            if encyclopedia == []:
                # 통합페이지로 돌아가기
                self.driver.find_element_by_xpath(
                    '//*[@id="lnb"]/div[1]/div/ul/li[1]/a').click()

                return print("지식백과 정보가 없습니다.", end='\n')
            # 크롤링할 페이지 입력받기
            self.cnt = 0
            while self.cnt <= 0:
                try:
                    self.cnt = int(input("크롤링할 페이지는 몇 페이지 입니까?: "))
                    print()
                    if self.cnt <= 0:
                        print("1부터 입력가능합니다.")
                        print()
                        continue
                except:
                    print("1이상의 숫자로 입력해주세요.")
                    print()
                    continue

            print()
            print('='*80)

            no = 1
            count = 1
            # 반복문으로 정보추출
            for x in range(1, self.cnt+1):
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                encyclopedia = soup.find_all('div', 'nkindic_area')

                for i in encyclopedia:
                    subject = i.find_all('div', 'nkindic_tit _svp_content')
                    for j in subject:
                        content = i.find('div', 'api_txt_lines desc')
                        source = i.find('span', 'source_txt')
                        print('번호:', no)
                        self.no2.append(no)
                        print("제목:", j.text.strip())
                        self.title2.append(j.text.strip())
                        print("내용:", content.text.strip())
                        self.content2.append(content.text.strip())
                        print("출처:", source.text.strip())
                        self.sources.append(source.text.strip())
                        print()
                        no += 1
                if self.cnt > count:
                    self.driver.find_element_by_xpath(
                        '//*[@id="main_pack"]/div[2]/div/a[2]').click()
                    count += 1
                    print(
                        f'-------------------{count}번째 페이지입니다.---------------')
                    time.sleep(1)

        # 지식백과가 있을 시
        else:
            no = 1
            count = 1
            # 반복문으로 정보추출
            for i in encyclopedia:
                title = i.find_all('div', 'nkindic_tit _svp_content')
                content = i.find_all('div', 'api_txt_lines desc')
                source = i.find_all('div', 'nkindic_source')
                d = 0
                for a in title:
                    b = a.find_all('a')
                    print()
                    print('번호:', no)
                    self.no2.append(no)
                    print('1.제목:', b[0].text)
                    self.title2.append(b[0].text)
                    if len(b) > 1:
                        print('부제목:', b[1].text)
                        self.s_title2.append(b[1].text)
                        print('내용:', content[d].text)
                        self.content2.append(content[d].text)
                        print('출처:', source[d].text.strip())
                        self.sources.append(source[d].text)
                        print()
                    else:
                        print('부제목:', '')  # 부제목 없을시
                        print('내용:', content[d].text)
                        self.content2.append(content[d].text)
                        print('출처:', source[d].text.strip())
                        self.sources.append(source[d].text.strip())
                        print()
                    d += 1
                    no += 1
        # 작업시간 표시
        e_time = time.time()
        t_time = e_time-s_time
        print('='*80)
        print('출력에 걸린시간은 %s초 입니다' % round(t_time, 1))
        print('='*80)

        # 표형태로 정보 변환
        self.data = pd.DataFrame()
        self.data['번호'] = self.no2
        self.data['제목'] = self.title2
        try:
            self.data['부제목'] = self.s_title2
        except:
            pass
        self.data['내용'] = self.content2
        self.data['출처'] = self.sources

        # 통합으로 돌아가기
        self.driver.find_element_by_xpath(
            '//*[@id="lnb"]/div[1]/div/ul/li[1]/a').click()

    ###### 백과사전 텍스트 저장 #######
    def know_text(self):
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        encyclopedia = soup.find_all(
            'section', 'sc_new sp_nkindic _au_kindic_collection')

        # 지식백과가 없을 시
        if len(encyclopedia) == 0:
            self.driver.find_element_by_xpath(
                '//*[@id="_nx_lnb_more"]/a').click()
            time.sleep(1)
            self.driver.find_element_by_xpath(
                '//*[@id="_nx_lnb_more"]/div/ul/li[2]/a').click()
            encyclopedia = soup.find_all('div', 'nkindic_area')
            print()

            no = 1
            count = 1
            # 반복문으로 정보추출
            for x in range(1, self.cnt+1):
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                encyclopedia = soup.find_all('div', 'nkindic_area')

                for i in encyclopedia:
                    subject = i.find_all('div', 'nkindic_tit _svp_content')
                    for j in subject:
                        content = i.find('div', 'api_txt_lines desc')
                        source = i.find('span', 'source_txt')
                        print('번호:', no)
                        print("제목:", j.text.strip())
                        print("내용:", content.text.strip())
                        print("출처:", source.text.strip())
                        print()
                        no += 1
                if self.cnt > count:
                    self.driver.find_element_by_xpath(
                        '//*[@id="main_pack"]/div[2]/div/a[2]').click()
                    count += 1
                    print(
                        f'-------------------{count}번째 페이지입니다.---------------')
                    time.sleep(1)

        # 지식백과가 있을 시
        else:
            no = 1
            count = 1
            for i in encyclopedia:
                title = i.find_all('div', 'nkindic_tit _svp_content')
                content = i.find_all('div', 'api_txt_lines desc')
                source = i.find_all('div', 'nkindic_source')
                d = 0
                # 반복문으로 정보추출
                for a in title:
                    b = a.find_all('a')
                    print()
                    print('번호:', no)
                    print('1.제목:', b[0].text)
                    if len(b) > 1:
                        print('부제목:', b[1].text)
                        print('내용:', content[d].text)
                        print('출처:', source[d].text.strip())
                        print()
                    else:
                        print('부제목:', '')  # 부제목 없을시
                        print('내용:', content[d].text)
                        print('출처:', source[d].text.strip())
                        print()
                    d += 1
                    no += 1

        # 통합으로 돌아가기
        self.driver.find_element_by_xpath(
            '//*[@id="lnb"]/div[1]/div/ul/li[1]/a').click()

    ###### 어학사전 #######
    def lan_dic(self):
        global no2
        global title2
        global content2
        global dic2

        # 리스트 비우기
        self.no2.clear()
        self.dic2.clear()
        self.title2.clear()
        self.content2.clear()
        time.sleep(2)

        page = self.driver.page_source
        soup = BeautifulSoup(page, 'html.parser')

        # 시작시간
        s_time = time.time()
        no = 1
        try:
            contents_title = soup.find(
                'section', '_au_dictionary').find('div', '_popup_wrap')
        except AttributeError:
            print('어학사전이 존재하지 않습니다.')
            print('='*80)
        else:
            # 어학사전일때 사전정보 찾기
            content_list = soup.find_all("div", "dic_area")
            # 그외 사전일때 사전정보 찾기
            content_list2 = soup.find_all("section", "_au_dictionary")

            # 사전 타이틀 추출하기
            word_f = soup.find_all("h2", "api_title")
            for word in word_f:
                #### 어학사전 크롤링 ####
                if word.get_text() == '어학사전':
                    for i in content_list:
                        try:
                            dic = i.find(
                                "h3", "dic_title_sub").get_text().strip()
                        except:
                            dic = '사전 정보가 없습니다.'
                            self.dic2.append(dic)
                            print("사전:", dic)
                        else:
                            self.no2.append(no)
                            print("번호:", no)
                            self.dic2.append(dic)
                            print("사전:", dic)
                        try:
                            title = i.find("a", "title").get_text().strip()
                        except:
                            title = '단어 정보가 없습니다.'
                            self.title2.append(title)
                            print("단어:", title)
                        else:
                            self.title2.append(title)
                            print("단어:", title)
                        try:
                            content = i.find(
                                "dd", "word_dsc").get_text().strip()
                        except:
                            content = '뜻 정보가 없습니다.'
                            self.content2.append(content)
                            print("뜻:", content)
                        else:
                            self.content2.append(content)
                            print("뜻:", content)
                            no += 1
                            print()

                #### 그외 사전 크롤링 ####
                elif '사전' in word.get_text():
                    for i in content_list2:
                        try:
                            dic = i.find("h2", "api_title").get_text().split()
                        except:
                            dic = '사전 정보가 없습니다.'
                            self.dic2.append(dic)
                            print("사전:", dic)
                        else:
                            self.no2.append(no)
                            print("번호:", no)
                            self.dic2.append(dic[0][:9])
                            print("사전:", dic[0][:9])
                        try:
                            title = i.find("a", "title").get_text().strip()
                        except:
                            title = '단어 정보가 없습니다.'
                            self.title2.append(title)
                            print("단어:", title)
                        else:
                            self.title2.append(title)
                            print("단어:", title)
                        try:
                            content = i.find(
                                "dd", "word_dsc").get_text().strip()
                        except:
                            content = '뜻 정보가 없습니다.'
                            self.content2.append(content)
                            print("뜻:", content)
                        else:
                            self.content2.append(content)
                            print("뜻:", content)
                            no += 1
                            print()
            # 작업시간 표시
            e_time = time.time()
            t_time = e_time-s_time
            print('='*80)
            print('출력에 걸린시간은 %s초 입니다' % round(t_time, 1))
            print('='*80)

            # 표형태로 정보 변환
            self.data = pd.DataFrame()
            self.data['번호'] = self.no2
            self.data['사전'] = self.dic2
            self.data['단어'] = self.title2
            self.data['뜻'] = self.content2


class SaveMenu(Crawler):
    # c:\ezen_ai\2021-09-15-16-21-가을 여행-view.txt로 저장되었습니다.
    def save_folder(self):
        while True:
            if self.save_re == 0:
                self.f_dir = input(
                    "수집된 데이터를 저장할 폴더명을 입력해주세요.\n(예: c:\ezen_python_data\\) > ")
                if self.f_dir == "":
                    print("저장할 폴더명을 입력해주세요.")
                    continue
                elif self.f_dir[-1] != "\\":
                    print("폴더명을 제대로 입력해주세요.")
                    continue
                else:
                    print("="*80)
                    try:
                        os.makedirs(self.f_dir)
                    except OSError:
                        while True:
                            save_again = input("해당 폴더명이 이미 존재합니다. 폴더명을 다시 입력하시겠습니까?\
                            \n[메뉴] Y : 폴더명 다시 입력 / M : 존재하는 폴더에 저장 / D: 존재하는 폴더 삭제 > ")
                            print("="*80)
                            if save_again.upper() == "Y":
                                break
                            elif save_again.upper() == "M":
                                while True:
                                    save_again2 = input(
                                        "이미 존재하는 폴더명에 저장하시겠습니까?(Y/N) > ")
                                    if save_again2.upper() == "Y":
                                        self.save_re += 1
                                        return os.chdir(self.f_dir)
                                        break
                                    elif save_again2.upper() == "N":
                                        print("존재하는 폴더에 저장하기를 선택하지 않으셨습니다.")
                                        print("="*80)
                                        break
                                    else:
                                        print("(Y/N)로 입력해주시길 바랍니다.")
                                        continue
                            elif save_again.upper() == "D":
                                try:
                                    os.rmdir(self.f_dir)
                                except OSError:
                                    while True:
                                        have = input(
                                            "해당 폴더에 있는 파일까지 모두 삭제하시겠습니까?(Y/N) > ")
                                        if have.upper() == "Y":
                                            try:
                                                os.chmod(self.f_dir, 0o777)
                                                shutil.rmtree(self.f_dir)
                                            except OSError:
                                                msg = '[WinError 32] 다른 프로세스가 파일을 사용 중으로 폴더를 삭제하지 못하였습니다.'
                                                print(msg)
                                                break
                                            else:
                                                time.sleep(1)
                                                print(
                                                    f"{self.f_dir}폴더를 삭제하였습니다.")
                                                print("="*80)
                                                break
                                        elif have.upper() == "N":
                                            break
                                        else:
                                            print("(Y/N)로 입력해주시길 바랍니다.")
                                            continue
                                break
                            else:
                                print("(Y /M /D)만 입력해주시길 바랍니다.")
                                continue
                    else:
                        os.chdir(self.f_dir)
                        self.save_re += 1
                        break
            else:
                while True:
                    dir_again = input("이전에 요청하신 저장폴더에 계속 저장하시겠습니까?(Y/N) > ")
                    if dir_again.upper() == "Y":
                        self.save_re += 1
                        return os.chdir(self.f_dir)
                        break
                    elif dir_again.upper() == "N":
                        self.save_re = 0
                        break
                    else:
                        print("(Y/N)로 입력해주시길 바랍니다.")
                        continue

    def save_txt(self, searchType):
        try:
            if self.cnt >= 1:
                Crawler.know_text()
            else:
                Crawler.know()
        except:
            pass

        now = time.localtime()
        f_name = "%04d-%02d-%02d-%02d-%02d" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
        searchMenu = {"1": "블로그", "2": "뉴스",
                      "3": "카페", "4": "지식백과", "5": "어학사전"}
        for key, value in searchMenu.items():
            if int(key) == searchType:
                ff_name = self.f_dir+f_name+"-"+self.search+"-"+value+".txt"
            else:
                pass
        orig_stdout = sys.stdout
        f = open(ff_name, 'a', encoding='utf-8')
        sys.stdout = f

        if searchType == 1:
            self.blog()
        elif searchType == 2:
            self.news_text()
        elif searchType == 3:
            self.cafe_text()
        elif searchType == 4:
            self.know_text()
        elif searchType == 5:
            self.lan_dic()
        else:
            print("숫자를 제대로 입력해주세요.")

        sys.stdout = orig_stdout
        f.close()
        print('txt 파일 저장 경로 : %s' % ff_name)
        print("="*80)
        pass

    def save_csv(self, searchType):
        now = time.localtime()
        f_name = "%04d-%02d-%02d-%02d-%02d" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
        searchMenu = {"1": "블로그", "2": "뉴스",
                      "3": "카페", "4": "지식백과", "5": "어학사전"}
        for key, value in searchMenu.items():
            if int(key) == searchType:
                fc_name = self.f_dir+f_name+"-"+self.search+"-"+value+".csv"
            else:
                pass

        #### 블로그 ####
        if searchType == 1:
            self.data.to_csv(fc_name, encoding='utf-8-sig')
            print('csv 파일 저장 경로 : %s' % fc_name)
            print("="*80)

        #### 뉴스 ####
        elif searchType == 2:
            self.data.to_csv(fc_name, encoding='utf-8-sig')
            print('csv 파일 저장 경로 : %s' % fc_name)
            print("="*80)

        #### 카페 ####
        elif searchType == 3:
            self.data.to_csv(fc_name, encoding='utf-8-sig')
            print('csv 파일 저장 경로 : %s' % fc_name)
            print("="*80)

        #### 지식백과 ####
        elif searchType == 4:
            self.data.to_csv(fc_name, encoding='utf-8-sig')
            print('csv 파일 저장 경로 : %s' % fc_name)
            print("="*80)

        #### 어학사전 ####
        elif searchType == 5:
            self.data.to_csv(fc_name, encoding='utf-8-sig')
            print('csv 파일 저장 경로 : %s' % fc_name)
            print("="*80)

    def save_xls(self, searchType):
        now = time.localtime()
        f_name = "%04d-%02d-%02d-%02d-%02d" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
        searchMenu = {"1": "블로그", "2": "뉴스",
                      "3": "카페", "4": "지식백과", "5": "어학사전"}
        for key, value in searchMenu.items():
            if int(key) == searchType:
                fx_name = self.f_dir+f_name+"-"+self.search+"-"+value+".xls"
            else:
                pass

        #### 블로그 ####
        if searchType == 1:
            self.data.to_excel(fx_name)
            print('xls 파일 저장 경로 : %s' % fx_name)
            print("="*80)

        #### 뉴스 ####
        elif searchType == 2:
            self.data.to_excel(fx_name)
            print('xls 파일 저장 경로 : %s' % fx_name)
            print("="*80)

        #### 카페 ####
        elif searchType == 3:
            self.data.to_excel(fx_name)
            print('xls 파일 저장 경로 : %s' % fx_name)
            print("="*80)

        #### 지식백과 ####
        elif searchType == 4:
            self.data.to_excel(fx_name)
            print('xls 파일 저장 경로 : %s' % fx_name)
            print("="*80)

        #### 어학사전 ####
        elif searchType == 5:
            self.data.to_excel(fx_name)
            print('xls 파일 저장 경로 : %s' % fx_name)
            print("="*80)


class Run(SaveMenu):
    def save_run(self, searchType):
        if not len(self.no2):
            while self.done > 0:
                try:
                    question = input(
                        "저장할 정보가 없습니다. 다른 메뉴로 크롤링 하시겠습니까?(Y/N) > ")
                except ValueError:
                    print("(Y/N)를 입력해주세요.")
                    print("="*80)
                    continue
                else:
                    if question.upper() == "Y":
                        break
                    elif question.upper() == "N":
                        while True:
                            try:
                                self.new = int(
                                    input("새로운 검색어로 검색하시겠습니까?(1:예/ 2:아니오) > "))
                            except ValueError:
                                print("숫자를 입력해주세요.")
                                print("="*80)
                                continue
                            else:
                                if self.new == 1:
                                    self.driver.close()
                                    self.new = 1
                                    self.done = 0
                                    break
                                elif self.new == 2:
                                    self.new = 2
                                    self.done = 0
                                    break
                                else:
                                    print("숫자만 입력해주시길 바랍니다.")
                                    continue
                    else:
                        print("(Y/N)만 입력해주세요.")
                        print("="*80)
                        continue
        else:
            self.save_done = 1
            while self.save_done > 0:
                try:
                    save_q = input("추출된 데이터를 파일로 저장하시겠습니까?(Y/N) > ")
                except ValueError:
                    print("(Y/N)를 입력해주세요.")
                    print("="*80)
                    continue
                else:
                    if save_q.upper() == "Y":
                        saveType = 1
                        self.save_re = 0
                        while True:
                            try:
                                saveType = int(
                                    input("""[메뉴] 1.txt 2.csv 3.xls (종료: 0)\n메뉴를 선택해주세요 > """))
                            except ValueError:
                                print("메뉴를 입력해주세요.")
                                print("="*80)
                                continue
                            else:
                                print("="*80)
                                if saveType == 1:
                                    self.save_folder()
                                    self.save_txt(searchType)
                                    self.save_re += 1
                                elif saveType == 2:
                                    self.save_folder()
                                    self.save_csv(searchType)
                                    self.save_re += 1
                                elif saveType == 3:
                                    self.save_folder()
                                    self.save_xls(searchType)
                                    self.save_re += 1
                                elif saveType == 0:
                                    self.save_done = 0
                                    self.save_re += 0
                                    print("저장 프로그램을 종료합니다.")
                                    print("="*80)
                                    break
                                else:
                                    print("숫자를 제대로 입력해주세요.")
                                    print("="*80)
                                    continue
                    elif save_q.upper() == "N":
                        print("저장 프로그램을 종료합니다.")
                        print("="*80)
                        break
                    else:
                        print("(Y/N)만 입력해주세요.")
                        continue

    def run(self):
        self.new = 1
        self.done = 1
        self.save_done = 1
        while True:
            # 네이버크롤러 시작
            if self.new == 1:
                self.naver()
                self.done = 1
            else:
                print("네이버크롤러 version 1.0를 종료합니다.")
                print("웹 브라우저를 종료하겠습니다.")
                print("="*80)
                self.driver.close()
                break
            while self.done > 0:
                # 메뉴 선택하여 크롤링 하기
                try:
                    searchType = int(
                        input("""[메뉴] 1.블로그 2.뉴스 3.카페 4.지식백과 5.어학사전 (종료: 0)\n메뉴를 선택해주세요 > """))
                except ValueError:
                    print("메뉴를 선택해주세요.")
                    print("="*80)
                    continue
                else:
                    print("="*80)
                    #### 블로그 크롤링 ####
                    if searchType == 1:
                        self.blog()
                        self.save_run(searchType)

                    #### 뉴스 크롤링 ####
                    elif searchType == 2:
                        self.news()
                        self.save_run(searchType)

                    #### 카페 크롤링 ####
                    elif searchType == 3:
                        self.cafe()
                        self.save_run(searchType)

                    #### 백과사전 크롤링 ####
                    elif searchType == 4:
                        self.know()
                        self.save_run(searchType)

                    #### 어학사전 크롤링 ####
                    elif searchType == 5:
                        self.lan_dic()
                        self.save_run(searchType)

                    #### 크롤링 종료 ####
                    elif searchType == 0:
                        while True:
                            try:
                                self.new = int(
                                    input("새로운 검색어로 검색하시겠습니까?(1:예/ 2:아니오) > "))
                            except ValueError:
                                print("숫자를 입력해주세요.")
                                print("="*80)
                                continue
                            else:
                                if self.new == 1:
                                    self.driver.close()
                                    self.new = 1
                                    self.done = 0
                                    break
                                elif self.new == 2:
                                    self.new = 2
                                    self.done = 0
                                    print("="*80)
                                    break
                                else:
                                    print("숫자만 입력해주시길 바랍니다.")
                                    continue
                    else:
                        print("숫자를 제대로 입력해주세요.")
                        print("="*80)
                        continue
