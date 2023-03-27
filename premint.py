import datetime
import random
import threading

import pyperclip
import requests
import time
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from colorama import init
import pandas as pd
# from datetime import datetime, timedelta
import os

# from analysis_captcha import base64_api
# import sys
init(autoreset=True)


#  修改时间2022年11月11日16点11分


# excel
def modify_excel_format(excel_data, writer, df):
    # ----------调整excel格式 ---------------
    workbook = writer.book
    fmt = workbook.add_format({"font_name": u"宋体"})
    col_fmt = workbook.add_format(
        {'bold': True, 'font_size': 11, 'font_name': u'宋体', 'border': 1, 'bg_color': '#0265CB', 'font_color': 'white',
         'valign': 'vcenter', 'align': 'center'})
    detail_fmt = workbook.add_format(
        {"font_name": u"宋体", 'border': 0, 'valign': 'vcenter', 'align': 'center', 'font_size': 11, 'text_wrap': True})
    worksheet1 = writer.sheets['Sheet1']
    for col_num, value in enumerate(df.columns.values):
        worksheet1.write(0, col_num, value, col_fmt)
    # 设置列宽行宽
    worksheet1.set_column('A:B', 20, fmt)
    worksheet1.set_column('C:C', 65, fmt)
    worksheet1.set_column('D:D', 15, fmt)
    worksheet1.set_row(0, 30, fmt)
    for i in range(1, len(excel_data) + 1):
        worksheet1.set_row(i, 27, detail_fmt)


def excel_new():
    if os.path.exists('任务日志.xlsx'):
        pass
    else:
        excel_data = []
        columns = ["完成时间", "平台", "项目地址", "已执行序号", "未执行序号"]
        # tmp = ["张同学", "张同学", "pd 生成excel", "pandas", "pd", "python"]
        # excel_data.append(tmp)
        df = pd.DataFrame(data=excel_data, columns=columns)
        with pd.ExcelWriter(path='任务日志.xlsx', engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name='Sheet1', header=False, index=False, startcol=0,
                        startrow=1)
            modify_excel_format(excel_data, writer, df)
            # writer.save()
            print('已在根目录创建任务日志,请勿删除!')


def excel_re(adsarr, unexecuted, type_text):
    original_data = pd.read_excel('任务日志.xlsx')
    d_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    if url:
        data2 = {'完成时间': [d_time],
                 '平台': [type_text],
                 '项目地址': [url],
                 '已执行序号': [adsarr],
                 '未执行序号': [unexecuted]}
        data2 = pd.DataFrame(data2)
    else:
        sheet = pd.read_excel('待操作项目.xlsx')
        col = sheet['url']
        data2 = {'完成时间': [d_time],
                 '平台': [type_text],
                 '项目地址': [col],
                 '已执行序号': [adsarr],
                 '未执行序号': [unexecuted]}
        data2 = pd.DataFrame(data2)
    # 将新数据与旧数据合并起来
    save_data = pd.concat([original_data, data2], axis=0)
    # save_data.to_excel('demo.xlsx', index=False)
    with pd.ExcelWriter(path='任务日志.xlsx', engine="xlsxwriter") as writer:
        save_data.to_excel(writer, sheet_name='Sheet1', header=False, index=False, startcol=0,
                           startrow=1)
        modify_excel_format(save_data, writer, original_data)
        # writer.save()
        # print('任务已存储!')


# 关闭当前窗口
def webclose(driver):  # 关闭当前窗口
    handles = driver.window_handles
    if len(handles) >= 1:
        driver.switch_to.window(handles[-1])
        driver.close()
    else:
        driver.close()


def switch_window(driver):  # 切换当前窗口
    handles = driver.window_handles
    driver.switch_to.window(handles[-1])


def check_windows(driver, main_windows):
    windows = "open"
    try:  # 检查浏览器是否关闭
        all_windows = driver.window_handles
        if main_windows in all_windows:
            pass
        else:
            windows = "close"
    except WebDriverException:
        windows = "close"
    return windows


def recaptcha(driver, x):
    try:
        WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '[title="reCAPTCHA"]')))
        # print("发现验证码")
        reg = 0
        err = 0
        while True:
            try:
                recaptcha1 = driver.find_element(By.CSS_SELECTOR, '[title="reCAPTCHA"]')
                driver.switch_to.frame(recaptcha1)
                # print("切入第一个窗口")
            except:
                pass
            try:
                driver.find_element(By.CLASS_NAME, 'recaptcha-checkbox-border').click()
                # print("点击验证码")
                time.sleep(3)
            except:
                pass
            try:
                driver.find_element(By.CSS_SELECTOR, '[aria-checked="true"]')
                # print("验证成功")
                driver.switch_to.default_content()  # 返回主窗口
                # print("返回1")
                break
            except:
                pass
            driver.switch_to.default_content()  # 返回主窗口
            # print("返回2")
            try:
                recaptcha2 = driver.find_element(By.XPATH, '//iframe[contains(@title, "recaptcha challenge")]')
                driver.switch_to.frame(recaptcha2)
                # print("切入第二个窗口")
            except:
                pass
            time.sleep(2)
            try:
                driver.find_element(By.XPATH, '//div[contains(text(), "Try again later")]')
                if err < 3:
                    try:
                        driver.find_element(By.CSS_SELECTOR, '[title="Reset the challenge"]').click()
                        # print("点击刷新")
                        err += 1
                    except:
                        pass
                if err == 3:
                    print('\033[0;31m浏览器[%s]:需手动操作验证码\033[0m' % x)
                    driver.switch_to.default_content()  # 返回主窗口
                    break
            except:
                pass
            try:
                driver.find_element(By.CSS_SELECTOR, '[class="button-holder help-button-holder"]').click()
                # print("点击耳机")
                reg += 1
                time.sleep(2)
            except:
                pass
            if reg >= 5:
                try:
                    driver.find_element(By.CSS_SELECTOR, '[id="recaptcha-reload-button"]').click()
                    print('\033[0;31m浏览器[%s]:刷新验证码\033[0m' % x)
                    time.sleep(2)
                    reg = 0
                except:
                    pass
            # while True:
            #     # print("开始判断")
            #     try:
            #         driver.find_element(By.XPATH, '//iframe[contains(@title, "recaptcha challenge")]')
            #         time.sleep(2)
            #     except :
            #         break
            #     try:
            #         driver.find_element(By.CSS_SELECTOR, '[class="button-holder help-button-holder"]').click()
            #         time.sleep(2)
            #         reg += 1
            #     except :
            #         pass
            #     if reg >= 3:
            #         driver.find_element(By.CSS_SELECTOR, '[id="recaptcha-reload-button"]').click()
            #         time.sleep(2)
            #         reg = 0
            driver.switch_to.default_content()  # 返回主窗口
            # print("返回3")
    except:
        print('浏览器[%s]:未发现验证码' % x)


def scroll(driver, order):
    temp_height = 0
    scroll_height = 100
    check_order = 0
    while True:
        scroll_height += 1000 * random.random()
        # _browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        driver.execute_script('window.scrollTo(' + str(temp_height) + ', ' + str(scroll_height) + ')')
        check_height = driver.execute_script(
            "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
        # 如果两者相等说明到底了
        check_order += 1
        # print(check_order)
        if check_height == temp_height:
            break
        if check_order == order:
            break
        temp_height = check_height
        time.sleep(random.uniform(1.228, 2.345))


def twitter_bot(driver, x):
    starttime = datetime.datetime.now().replace(microsecond=0)
    time.sleep(random.uniform(1, 2))
    driver.switch_to.new_window()
    time.sleep(random.uniform(1, 2))
    switch_window(driver)
    driver.get('https://twitter.com/home')
    try:
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#react-root section')))
        try:
            WebDriverWait(driver, 8).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="sheetDialog"]')))
            driver.refresh()
            time.sleep(4)
        except TimeoutException:
            pass
        # twitter = driver.find_element(By.CSS_SELECTOR, "#step-twitter .col-12>div>a")
        tasknum = random.randint(13, 30)  # 任务次数
        temp_height = 0
        scroll_height = 100
        print("浏览器[%s]:养号任务执行[%s]次" % (x, tasknum - 1))
        for t in range(1, tasknum):
            switch_window(driver)
            order = random.randint(5, 10)  # 滚动次数
            # print("浏览器[%s]:生成首页滚动次数[%s]" % (x,order))
            check_order = 0
            while True:
                scroll_height += 1000 * random.random()
                # print(temp_height)
                # _browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                driver.execute_script('window.scrollTo(' + str(temp_height) + ', ' + str(scroll_height) + ')')
                check_height = driver.execute_script(
                    "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
                # 如果两者相等说明到底了
                check_order += 1
                # print(check_order)
                if check_height == temp_height:
                    break
                if check_order == order:
                    break
                temp_height = check_height

                # print(check_height)
                time.sleep(random.uniform(1.228, 2.345))
            # driver.execute_script('window.scrollTo(' + str(temp_height) + ', 2)')
            # time.sleep(random.uniform(1.228, 2.345))
            try:
                tweetText = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetText"]')))
                driver.execute_script("arguments[0].scrollIntoView(false);", tweetText)
                time.sleep(random.uniform(1.328, 4.045))
                tweetText.click()
                # print("浏览器[%s]:点击推文" %x)
                time.sleep(random.uniform(1.228, 2.045))
                switch_window(driver)
                t_url = driver.current_url  # 获取当前url
                t_type = "status" in t_url  # 寻找当前url是否包含status
                if t_type:  # 寻找当前url是否包含status
                    try:
                        WebDriverWait(driver, 30).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, '[role="group"]')))
                        order = random.randint(3, 6)  # 滚动次数
                        # print("浏览器[%s]:生成内页滚动次数[%s]" % (x, order))
                        time.sleep(random.uniform(5.28, 12.14))
                        scroll(driver, order)
                        try:
                            # driver.find_element(By.CSS_SELECTOR, '').click()
                            like = driver.find_element(By.CSS_SELECTOR, 'div[aria-label~=Like]')
                            if random.randint(0, 2) == 0:
                                # print("浏览器[%s]:执行点赞操作" % x)
                                like.click()
                                # print('点赞成功')
                            elif random.randint(0, 5) == 0:
                                # print("浏览器[%s]:执行关注操作" % x)
                                avatar = driver.find_element(By.CSS_SELECTOR,
                                                             '[data-testid="Tweet-User-Avatar"]')
                                ActionChains(driver).move_to_element(avatar).perform()
                                time.sleep(random.uniform(3.228, 5.145))
                                try:
                                    WebDriverWait(driver, 5).until(
                                        EC.visibility_of_element_located(
                                            (By.CSS_SELECTOR, '[aria-label~=Follow]'))).click()
                                except:
                                    pass
                        except:
                            pass
                        time.sleep(random.uniform(1.228, 2.145))
                        driver.back()
                        # home = driver.find_element(By.CSS_SELECTOR, '[data-testid="AppTabBar_Home_Link"]')
                        # home.click()
                        # print('返回首页')
                    except:
                        pass
                else:
                    t_type = "twitter" in t_url  # 寻找当前url是否包含twitter
                    if t_type:
                        driver.back()
                        print("浏览器[%s]:可能未正确打开推文，返回上一页" % x)
                    else:
                        webclose(driver)
                        print("浏览器[%s]:跳转到站外，关闭网页" % x)
            except:
                print("\033[0;31m浏览器[%s]:未点击推文，尝试刷新\033[0m" % x)
                driver.refresh()
            # print("浏览器[%s]:任务进度[%s/%s]" % (x, t, tasknum - 1))
        webclose(driver)  # 关闭网页
    except:
        print("\033[0;31m浏览器[%s]:未成功打开推特或出现错误\033[0m" % x)
    endtime = datetime.datetime.now().replace(microsecond=0)
    print("浏览器[%s]:养号任务完成,耗时[%s]" % (x, endtime - starttime))

def getuser(driver):
    user = WebDriverWait(driver, 60).until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, '[aria-label="Profile"]')))
    username = user.get_attribute("href")
    username = username.replace('https://twitter.com/', '@')
    return username


def twitter_reply(driver, x):  # 推特评论
    global reply_url
    sheet = pd.read_excel('ads.xlsx')
    col = sheet[sheet['reply'].notna()]
    reply_text = col['reply']
    num = random.randint(0, reply_text.shape[0] - 1)  # 随机取一行
    # print(reply_text[num])
    try:
        reply = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-contents="true"]>div')))
        reply.click()
        time.sleep(random.uniform(1.328, 2.045))
        pyperclip.copy(reply_text[num])
        time.sleep(random.uniform(0.5, 0.7))
        reply.send_keys(Keys.CONTROL, 'a')
        time.sleep(random.uniform(1, 2))
        reply.send_keys(Keys.BACK_SPACE)
        time.sleep(random.uniform(1, 2))
        reply.send_keys(Keys.CONTROL, 'v')
        time.sleep(random.uniform(1.328, 2.045))
        reply.send_keys(Keys.SPACE)
        time.sleep(random.uniform(1.328, 2.045))
        col = sheet[sheet['friends'].notna()]
        friends = col['friends']
        friends_num = random.randint(0, 3)  # 频道数量
        res = friends.sample(n=friends_num)
        for i, goods in enumerate(res):
            reply.send_keys(goods)
            time.sleep(random.uniform(0.528, 1.045))
            reply.send_keys(Keys.SPACE)
            time.sleep(random.uniform(0.528, 1.045))
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '[tabindex="0"][data-testid="tweetButtonInline"]'))).click()
            while True:
                # print("开始判断")
                try:
                    driver.find_element(By.CSS_SELECTOR, '[tabindex="0"][data-testid="tweetButtonInline"]')
                    time.sleep(1)
                except:
                    # print("发表推文完成")
                    break
            try:  # 保存评论链接
                reply_link = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, '[data-testid="toast"] [aria-hidden="true"] a')))
                time.sleep(2)
                reply_url = reply_link.get_attribute("href")
            except:
                pass
        except:
            pass
    except:
        print('\033[0;31m浏览器[%s]:Twitter回复推文失败\033[0m' % x)


def twitter_step(driver, x):  # 推特三连任务
    # t_windows = driver.current_window_handle  # 获取当前标签页句柄
    # first_windows(driver, t_windows)  # 切换句柄
    global handle
    switch_window(driver)
    retries = 1
    while retries <= 5:
        try:
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#react-root section')))
            time.sleep(2)
            try:
                driver.find_element(By.XPATH, '//span[text()="This Tweet is unavailable. "]')
                driver.refresh()
            except:
                pass
            try:
                driver.find_element(By.XPATH, '//span[contains(text(),"Accept all cookies")]').click()
                time.sleep(random.uniform(1, 2))
            except Exception:
                pass
            # print('找到推特首页')
            t_url = driver.current_url  # 获取当前url
            t_type = "status" in t_url  # 寻找当前url是否包含status
            tweet_id = "tweet_id" in t_url  # 寻找当前url是否包含status
            if t_type or tweet_id:
                try:
                    driver.find_element(By.XPATH, '//span[text()="Cancel"]').click()
                    time.sleep(1)
                    # try:
                    #     driver.find_element(By.XPATH, '//span[text()="Thread"]').click()
                    #     time.sleep(2)
                    # except :
                    #     pass
                except:
                    pass
                try:
                    WebDriverWait(driver, 1).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, '[tabindex="-1"] div[aria-label~=Liked]')))
                    # print('已点赞过，跳过')
                except:
                    # print('浏览器[%s]:开始执行推特任务' %(x))
                    try:
                        like = WebDriverWait(driver, 20).until(
                            EC.visibility_of_element_located(
                                (By.CSS_SELECTOR, '[tabindex="-1"] div[aria-label~=Like]')))
                        # print('找到点赞按钮')
                        scroll_origin = ScrollOrigin.from_element(like)
                        ActionChains(driver) \
                            .scroll_from_origin(scroll_origin, 0, 200) \
                            .perform()
                        time.sleep(random.uniform(1, 2))
                        like.click()
                    except:
                        retries += 1
                try:
                    driver.find_element(By.CSS_SELECTOR, '[tabindex="-1"] div[data-testid="unretweet"]')
                    # print('已转推过，跳过')
                except:
                    try:
                        retweet = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located(
                                (By.CSS_SELECTOR, '[tabindex="-1"] div[aria-label~=Retweet]')))
                        time.sleep(random.uniform(1, 2))
                        retweet.click()
                        menuitem = WebDriverWait(driver, 15).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[role="menuitem"]')))
                        time.sleep(random.uniform(1, 2))
                        menuitem.click()
                        # time.sleep(random.uniform(2, 3))
                        # twitter_reply(driver, x)
                    except:
                        pass
                time.sleep(random.uniform(2, 3))
                try:
                    driver.find_element(By.CSS_SELECTOR, '[tabindex="-1"] div[aria-label~=Liked]') \
                    and driver.find_element(By.CSS_SELECTOR, '[tabindex="-1"] div[data-testid="unretweet"]')
                    # driver.get_screenshot_as_file(x + '.png')
                    handle = getuser(driver)
                    time.sleep(random.uniform(3, 5))
                    webclose(driver)  # 关闭网页
                    break  # 结束循环
                except:
                    pass
            else:
                try:
                    driver.find_element(By.CSS_SELECTOR, '[aria-label="Close"]').click()
                except:
                    pass
                try:
                    driver.find_element(By.XPATH, '//span[text()="Cancel"]').click()
                except:
                    pass
                try:
                    driver.find_element(By.CSS_SELECTOR, '[data-testid="placementTracking"] [aria-label~=Following]')
                    # print('已关注过，关闭网页')
                    webclose(driver)  # 关闭网页
                    break  # 结束循环
                except:
                    # print('开始执行关注操作')
                    try:
                        follow = WebDriverWait(driver, 30).until(
                            EC.visibility_of_element_located(
                                (By.CSS_SELECTOR, '[data-testid="placementTracking"] [aria-label~=Follow]')))
                        time.sleep(random.uniform(1, 2))
                        follow.click()
                        # print('关注成功')
                        time.sleep(random.uniform(3, 4.2))
                        try:
                            driver.find_element(
                                By.CSS_SELECTOR, '[data-testid="placementTracking"] [aria-label~=Following]')
                            handle = getuser(driver)
                            webclose(driver)  # 关闭网页
                            break  # 结束循环
                        except:
                            pass
                    except:
                        pass
        except:
            try:
                driver.find_element(By.XPATH, '//span[text()="Retry"]').click()
                retries -= 1
            except:
                print('\033[0;31m浏览器[%s]:Twitter加载失败，尝试刷新页面\033[0m' % x)
                driver.refresh()
                retries += 1



def discord_step(driver, x):  # discord任务
    captcha = 0
    # print("需要切换的句柄%s" % pre_windows)
    # d_windows = driver.current_window_handle  # 获取当前标签页句柄
    # first_windows(driver, d_windows)  # 切换句柄
    switch_window(driver)
    while True:
        try:
            driver.find_element(By.CSS_SELECTOR, '[aria-label="Channel header"]')
            break
        except:
            pass
    try:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[starts-with(@class, "wrapper")] //button[contains(@class, "lookFilled")]'))).click()
    except:
        pass
    try:
        closs = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Close"]')))
        closs.click()
    except:
        pass
    try:  # 协议完成按钮
        d_button = WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//form//div[text()='Complete']")))
        time.sleep(1)
        d_button.click()
        try:  # 协议打勾
            d_checkbox = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//div[contains(@class, "labelClickable")]')))
            time.sleep(1)
            d_checkbox.click()
            try:  # 协议完成按钮
                d_submit = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]')))
                time.sleep(1)
                d_submit.click()
            except:
                pass
        except:
            pass
    except:
        pass
    try:  # 验证流程
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[starts-with(@class, "label")][contains(text(),"Verify")]'))).click()
        time.sleep(random.uniform(3, 5))
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//div[starts-with(@class, "label")][contains(text(),"Continue")]'))).click()
        except:
            pass
        time.sleep(random.uniform(3, 5))
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//div[starts-with(@class, "label")][contains(text(),"Continue")]'))).click()
        except:
            pass
    except:
        pass
    # try:
    #     button = WebDriverWait(driver, 60).until(
    #         EC.visibility_of_element_located(
    #             (By.XPATH, "//div[text()='Accept Invite']")))
    #     time.sleep(random.uniform(5, 10))
    #     button.click()
    #     while True:
    #         try:
    #             driver.find_element(By.CSS_SELECTOR, '[aria-label="CAPTCHA"]')
    #             if captcha == 0:
    #                 print('\033[0;97;41m浏览器[%s]:检测到验证码,请手动操作...\033[0m' % x)
    #                 captcha = 1
    #             time.sleep(2)
    #         except :
    #             try:
    #                 driver.find_element(By.CSS_SELECTOR, '[aria-label="Channel header"]')
    #                 break
    #             except :
    #                 pass
    #         # 检查浏览器是否关闭
    #         object_existed = False
    #         if driver is not None:
    #             try:
    #                 driver.execute_script('javascript:void(0);')
    #                 object_existed = True
    #             except :
    #                 # webdriver要求浏览器执行Javascript出现异常
    #                 try:
    #                     print('\033[0;31m浏览器[%s]:已关闭，释放线程\033[0m' % x)
    #                     # pool_sema.release()  # 解锁
    #                     break
    #                 finally:
    #                     driver = None
    #             finally:
    #                 pass
    #         if not object_existed:
    #             # 浏览器已关闭或标签页已关闭或其他异常
    #             ...
    #     time.sleep(2)
    #     try:
    #         closs = WebDriverWait(driver, 5).until(
    #             EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Close"]')))
    #         closs.click()
    #     except :
    #         pass
    #     try:  # 协议完成按钮
    #         d_button = WebDriverWait(driver, 8).until(
    #             EC.visibility_of_element_located(
    #                 (By.XPATH, "//form//div[text()='Complete']")))
    #         time.sleep(1)
    #         d_button.click()
    #         try:  # 协议打勾
    #             d_checkbox = WebDriverWait(driver, 20).until(
    #                 EC.visibility_of_element_located(
    #                     (By.XPATH, '//div[contains(@class, "labelClickable")]')))
    #             time.sleep(1)
    #             d_checkbox.click()
    #             try:  # 协议完成按钮
    #                 d_submit = WebDriverWait(driver, 10).until(
    #                     EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]')))
    #                 time.sleep(1)
    #                 d_submit.click()
    #             except :
    #                 pass
    #         except :
    #             pass
    #     except :
    #         pass
    #     try:  # 验证流程
    #         WebDriverWait(driver, 60).until(
    #             EC.visibility_of_element_located(
    #                 (By.XPATH, '//div[starts-with(@class, "label")][contains(text(),"Verify")]'))).click()
    #         time.sleep(random.uniform(3, 5))
    #         try:
    #             WebDriverWait(driver, 10).until(
    #                 EC.visibility_of_element_located(
    #                     (By.XPATH, '//div[starts-with(@class, "label")][contains(text(),"Continue")]'))).click()
    #         except :
    #             pass
    #         time.sleep(random.uniform(3, 5))
    #         try:
    #             WebDriverWait(driver, 10).until(
    #                 EC.visibility_of_element_located(
    #                     (By.XPATH, '//div[starts-with(@class, "label")][contains(text(),"Continue")]'))).click()
    #         except :
    #             pass
    #     except :
    #         pass
    # except :
    #     pass


def gettwitterlink(driver, x, type_no):  # 取twitter链接
    switch_window(driver)
    # print('取twitter链接')
    if type_no == 1:
        try:
            twitter = WebDriverWait(driver, 10).until(
                EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '#step-twitter .col-12>div>a')))
            # twitter = driver.find_element(By.CSS_SELECTOR, "#step-twitter .col-12>div>a")
            print("浏览器[%s]:开始执行Twitter任务" % x)
            for i, goods in enumerate(twitter):
                # first_windows(driver, pre_windows)  # 切换句柄
                switch_window(driver)
                href = goods.get_attribute("href")
                # print("第[%s]个链接，[%s]" % (i + 1, href))
                goods.click()
                time.sleep(1)
                twitter_step(driver, x)
                time.sleep(1)
            print('浏览器[%s]:Twitter任务结束' % x)
        except:
            print('\033[0;31m浏览器[%s]:获取Twitter链接出错...\033[0m' % x)
    if type_no == 2:
        try:
            twitter = WebDriverWait(driver, 60).until(
                EC.visibility_of_any_elements_located(
                    (By.XPATH, '//div[starts-with(@class, "MuiBox-root css-0")]'
                               '//div[contains(@class, "MuiAlert-standard")]//a')))
            # twitter = driver.find_element(By.CSS_SELECTOR, "#step-twitter .col-12>div>a")
            print("浏览器[%s]:开始执行Twitter任务" % x)
            for i, goods in enumerate(twitter):
                # first_windows(driver, pre_windows)  # 切换句柄
                switch_window(driver)
                href = goods.get_attribute("href")
                # print("第[%s]个链接，[%s]" % (i + 1, href))
                if "twitter" in href:
                    goods.click()
                    time.sleep(1)
                    twitter_step(driver, x)
                    time.sleep(1)
            print('浏览器[%s]:Twitter任务结束' % x)
        except:
            print('\033[0;31m浏览器[%s]:获取Twitter链接出错.\033[0m' % x)
    if type_no == 3:
        try:
            twitter = WebDriverWait(driver, 60).until(
                EC.visibility_of_any_elements_located(
                    (By.CSS_SELECTOR, '[class="list-disc pl-5"] a')))
            print("浏览器[%s]:开始执行Twitter任务" % x)
            for i, goods in enumerate(twitter):
                # first_windows(driver, pre_windows)  # 切换句柄
                switch_window(driver)
                href = goods.get_attribute("href")
                # print("第[%s]个链接，[%s]" % (i + 1, href))
                if "twitter" in href:
                    goods.click()
                    time.sleep(1)
                    twitter_step(driver, x)
                    time.sleep(1)
            print('浏览器[%s]:Twitter任务结束' % x)
        except:
            print('\033[0;31m浏览器[%s]:获取Twitter链接出错.\033[0m' % x)


def getdiscordlink(driver, x, type_no):  # 取discord链接
    if type_no == 1:
        try:
            discord = WebDriverWait(driver, 3).until(
                EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '#step-discord .col-12>div>a')))
            print("浏览器[%s]：开始执行discord任务" % x)
            for i, goods in enumerate(discord):
                # first_windows(driver, pre_windows)  # 切换句柄
                switch_window(driver)
                href = goods.get_attribute("href")
                # print("第[%s]个链接，[%s]" % (i + 1, href))
                goods.click()
                # 新建窗口
                # discord_ls.append(href)
                # time.sleep(1)
                # discord_step(driver, x)
        except:
            print('\033[0;31m浏览器[%s]:获取discord链接出错.\033[0m' % x)
    if type_no == 2:
        try:
            discord = WebDriverWait(driver, 60).until(
                EC.visibility_of_any_elements_located(
                    (By.XPATH, '//div[starts-with(@class, "MuiBox-root css-0")]'
                               '//div[contains(@class, "MuiAlert-standard")]//a')))
            # twitter = driver.find_element(By.CSS_SELECTOR, "#step-twitter .col-12>div>a")
            for i, goods in enumerate(discord):
                # first_windows(driver, pre_windows)  # 切换句柄
                switch_window(driver)
                href = goods.get_attribute("href")
                # print("第[%s]个链接，[%s]" % (i + 1, href))
                if "discord" in href:
                    goods.click()
        except:
            print('\033[0;31m浏览器[%s]:获取discord链接出错.\033[0m' % x)
    if type_no == 3:
        try:
            discord = WebDriverWait(driver, 3).until(
                EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '[class="grid gap-1"] a')))
            print("浏览器[%s]：开始执行discord任务" % x)
            for i, goods in enumerate(discord):
                # first_windows(driver, pre_windows)  # 切换句柄
                switch_window(driver)
                href = goods.get_attribute("href")
                # print("第[%s]个链接，[%s]" % (i + 1, href))
                # if href not in discord_ls:
                goods.click()
        except:
            print('\033[0;31m浏览器[%s]:获取discord链接出错.\033[0m' % x)
    time.sleep(30)
    switch_window(driver)
    try:
        driver.find_element(By.XPATH, '//div[text()="Accept Invite"]').click()
        print('\033[0;36m>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>浏览器[%s]:等待手动操作discord任务\033[0m' % x)
        time.sleep(10)
    except:
        pass
    discord_step(driver, x)
    while True:
        handles = driver.window_handles
        if len(handles) <= 1:
            break


def getemail(driver, x, type_no):  # 取Email
    sheet = pd.read_excel(os.getcwd() + r'\ads.xlsx', index_col=0)
    # print(sheet)
    col = sheet['Email']
    time.sleep(1)
    if type_no == 1:
        driver.find_element(By.CSS_SELECTOR, 'input[name="custom_field"]').send_keys(col[int(x)])
    if type_no == 2:
        driver.find_element(By.CSS_SELECTOR, 'input[id="email"]').send_keys(col[int(x)])


def getwallet(driver, x, type_no):  # 取Email
    # file = os.getcwd() + r'\ads.xlsx'
    sheet = pd.read_excel(os.getcwd() + r'\ads.xlsx', index_col=0)
    # print(sheet)
    col = sheet['wallet_address']
    time.sleep(1)
    if type_no == 1:
        driver.find_element(By.CSS_SELECTOR, 'input[name="custom_field"]').send_keys(col[int(x)])
    if type_no == 2:
        driver.find_element(By.CSS_SELECTOR, 'input[id="wallet"]').send_keys(col[int(x)])


def first_windows(driver, now_windows):  # 切换句柄
    all_windows = driver.window_handles
    # print("所有句柄%s" % all_windows)
    # print("now_windows:%s" % now_windows)
    if len(all_windows) <= 1:  # 如果只有一个页面
        # print("执行了操作1")
        driver.switch_to.window(now_windows)
    else:
        for handle in all_windows:
            # print("handle:%s" % handle)
            if handle != now_windows:
                # print("句柄切换成:%s" % handle)
                driver.switch_to.window(handle)


def clicksubmit_bot(driver, x, close_url, dc_open, t1, t2, main_windows):
    # first_windows(driver, pre_windows)  # 切换pre句柄
    switch_window(driver)
    try:  # 检查提交按钮
        submit = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '[type="submit"]')))
        if dc_open == 0:
            t = round(random.uniform(int(t1), int(t2)), 2)
            print("浏览器[%s]:%s秒后提交任务" % (x, t))
            # time.sleep(t)
            while t > 0:
                try:
                    driver.find_element(By.XPATH, '//h5[text()="Registered successfully"]')
                    check_bot(driver, x, close_url, dc_open, main_windows)  # 检查任务状态
                    break
                except:
                    pass
                # 检查浏览器是否关闭
                if check_windows(driver, main_windows) == "close":
                    print('\033[0;31m浏览器[%s]:已关闭,释放线程\033[0m' % x)
                    break
                t -= 1
                time.sleep(1)
        else:
            print("浏览器[%s]:discord任务完成，提交任务" % x)
        # driver.execute_script("arguments[0].scrollIntoView();", submitpre)  # 跳转到元素
        ActionChains(driver) \
            .scroll_to_element(submit) \
            .perform()
        time.sleep(random.uniform(1, 2))
        driver.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
        # submit.click()
        check_bot(driver, x, close_url, dc_open, main_windows)  # 检查任务状态
    except:
        print('\033[0;31m浏览器[%s]:提交任务出错..\033[0m' % x)


def check_bot(driver, x, close_url, dc_open, main_windows):
    reg = 0
    while True:
        time.sleep(3)
        try:
            driver.find_element(By.XPATH, '//h5[text()="Registered successfully"]')
            # print('\033[0;32m浏览器[%s]:任务完成\033[0m' % x)
            break
        except:
            pass
        try:
            driver.find_element(By.CSS_SELECTOR, '[data-testid="CancelIcon"]')
            if reg == 0:
                print('\033[0;31m浏览器[%s]部分任务未完成,等待手动操作\033[0m' % x)
                reg = 1
        except:
            pass
        t_url = driver.current_url  # 获取当前url
        t_type = "premint" in t_url  # 寻找当前url是否包含status
        if t_type:
            pass
        else:
            print('\033[0;31m浏览器[%s]部分任务无法完成,跳过\033[0m' % x)
            break
        # 检查浏览器是否关闭
        if check_windows(driver, main_windows) == "close":
            print('\033[0;31m浏览器[%s]:已关闭,释放线程\033[0m' % x)
            break


def clicksubmit_heymint(driver, x, close_url, dc_open, t1, t2, main_windows):
    # first_windows(driver, pre_windows)  # 切换pre句柄
    switch_window(driver)
    check = 0
    try:  # 检查提交按钮
        submit = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '[type="submit"]')))
        if dc_open == 0:
            t = round(random.uniform(int(t1), int(t2)), 2)
            print("浏览器[%s]:%s秒后提交任务" % (x, t))
            # time.sleep(t)
            while t > 0:
                try:
                    driver.find_element(By.CSS_SELECTOR, '[data-icon="check"]')
                    check_heymint(driver, x, main_windows)  # 检查任务状态
                    check = 1
                    break
                except:
                    pass
                # 检查浏览器是否关闭
                if check_windows(driver, main_windows) == "close":
                    print('\033[0;31m浏览器[%s]:已关闭,释放线程\033[0m' % x)
                    check = 1
                    break
                t -= 1
                time.sleep(1)
        else:
            print("浏览器[%s]:discord任务完成，提交任务" % x)
        if check == 0:
            ActionChains(driver) \
                .scroll_to_element(submit) \
                .perform()
            time.sleep(random.uniform(1, 2))
            driver.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
            # submit.click()
            check_heymint(driver, x, main_windows)  # 检查任务状态
    except:
        print('\033[0;31m浏览器[%s]:提交任务出错..\033[0m' % x)


def clicksubmit_superful(driver, x, close_url, dc_open, t1, t2, main_windows):
    # first_windows(driver, pre_windows)  # 切换pre句柄
    switch_window(driver)
    try:  # 检查提交按钮
        submit = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((
            By.XPATH, "//p[text()='Join']")))
        ActionChains(driver) \
            .scroll_to_element(submit) \
            .perform()
        time.sleep(random.uniform(1, 2))
        driver.find_element(By.XPATH, '//p[text()="Join"]').click()
        clicks_superful(driver, x, main_windows, t1, t2)  # 检查任务状态
    except:
        print('\033[0;31m浏览器[%s]:提交任务出错..\033[0m' % x)


def check_heymint(driver, x, main_windows):
    reg = 0
    while True:
        time.sleep(3)
        try:
            driver.find_element(By.CSS_SELECTOR, '[data-icon="check"]')
            # print('\033[0;32m浏览器[%s]:任务完成\033[0m' % x)
            break
        except:
            pass
        try:
            driver.find_element(By.CLASS_NAME, 'bg-red-200')
            if reg == 0:
                print('\033[0;31m浏览器[%s]部分任务未完成,等待手动操作\033[0m' % x)
                reg = 1
        except:
            pass
        # 检查浏览器是否关闭
        if check_windows(driver, main_windows) == "close":
            print('\033[0;31m浏览器[%s]:已关闭,释放线程\033[0m' % x)
            break


def clicks_superful(driver, x, main_windows, t1, t2):
    reg = 0
    while True:
        time.sleep(3)
        try:
            driver.find_element(By.XPATH, '//p[text()="You have joined the raffle!"]')
            t = round(random.uniform(int(t1), int(t2)), 2)
            print('\033[0;32m浏览器[%s]:任务完成 %s秒后切换下一个任务\033[0m' % (x, t))
            while t > 0:
                # 检查浏览器是否关闭
                if check_windows(driver, main_windows) == "close":
                    print('\033[0;31m浏览器[%s]:已关闭,释放线程\033[0m' % x)
                    check = 1
                    break
                t -= 1
                time.sleep(1)
            break
        except:
            pass
        try:
            driver.find_element(By.XPATH, '//p[text()="Error"]')
            if reg == 0:
                print('\033[0;31m浏览器[%s]部分任务未完成,等待手动操作\033[0m' % x)
                reg = 1
        except:
            pass
        # 检查浏览器是否关闭
        if check_windows(driver, main_windows) == "close":
            print('\033[0;31m浏览器[%s]:已关闭,释放线程\033[0m' % x)
            break


def clicksubmit(driver, x, close_url, dc_open, t1, t2, main_windows, t_bot):
    # first_windows(driver, pre_windows)  # 切换pre句柄
    switch_window(driver)
    check = 0
    try:  # 检查提交按钮
        submitpre = WebDriverWait(driver, 30).until(EC.visibility_of(driver.find_element(By.ID, 'register-submit')))
        if dc_open == 0:
            if t_bot == 1:
                twitter_bot(driver, x)
                t_bot = 0
                switch_window(driver)
            t = round(random.uniform(int(t1), int(t2)), 2)
            print("浏览器[%s]:%s秒后提交任务" % (x, t))
            # time.sleep(t)
            while t > 0:
                try:
                    driver.find_element(By.CSS_SELECTOR, '.fa-3x')
                    checkpre(driver, x, close_url, dc_open, main_windows)  # 检查任务状态
                    check = 1
                    break
                except:
                    pass
                if check_windows(driver, main_windows) == "close":
                    print('\033[0;31m浏览器[%s]:已关闭,释放线程\033[0m' % x)
                    check = 1
                    break
                t -= 1
                time.sleep(1)
        else:
            print("浏览器[%s]:discord任务完成，提交任务" % x)
        if check == 0:
            ActionChains(driver) \
                .scroll_to_element(submitpre) \
                .perform()
            time.sleep(random.uniform(1, 2))
            driver.find_element(By.ID, 'register-submit').click()
            # submitpre.click()
            checkpre(driver, x, close_url, dc_open, main_windows)  # 检查任务状态
    except:
        print('\033[0;31m浏览器[%s]:没找到提交按钮\033[0m' % x)


def checkpre(driver, x, close_url, dc_open, main_windows):  # 检查pre任务状态
    reg = 0
    while True:
        try:
            driver.find_element(By.CSS_SELECTOR, '.fa-3x')
            # print('\033[0;32m浏览器[%s]:任务完成\033[0m' % x)
            break
        except:
            pass
        try:
            driver.find_element(By.CSS_SELECTOR, 'div[class="heading heading-3 mb-3"]')
            print('\033[0;32m浏览器[%s]:项目已结束\033[0m' % x)
            break
        except:
            pass
        # try:
        #     driver.find_element(By.XPATH, "//form//div[text()='Complete']")
        #     print('\033[0;32m浏览器[%s]:任务完成\033[0m' % x)
        #     break
        # except :
        #     pass
        try:
            driver.find_element(By.CSS_SELECTOR, '[role="alert"]')
            try:
                driver.find_element(By.XPATH, "//div[@class='card-title']//div[contains(.,'in your wallet')]")
                if reg == 0:
                    print('\033[0;31m浏览器[%s]钱包余额不满足要求，跳过此任务\033[0m' % x)
                    reg = 1
                    break
            except:
                try:
                    driver.find_element(
                        By.XPATH, "//div[@class='card-title']//div[contains(.,' please try again in 5 minutes')]")
                    if reg == 0:
                        print('\033[0;31m浏览器[%s]部分任务未完成，重新检查。\033[0m' % x)
                        reg = 1
                        gettwitterlink(driver, x, type_no)
                        switch_window(driver)
                        try:
                            submitpre = driver.find_element(By.ID, 'register-submit')
                            reg = 0
                            ActionChains(driver) \
                                .scroll_to_element(submitpre) \
                                .perform()
                            time.sleep(random.uniform(1, 2))
                            submitpre.click()
                        except:
                            pass
                except:
                    if reg == 0:
                        print('\033[0;31m浏览器[%s]部分任务未完成,等待手动操作\033[0m' % x)
                        reg = 1
        except:
            pass
        try:
            driver.find_element(By.CSS_SELECTOR, '[class="invalid-feedback"]')
            if reg == 0:
                print('\033[0;31m浏览器[%s]有必填项任务未完成,等待手动操作\033[0m' % x)
                reg = 1
            time.sleep(5)
        except:
            pass
        try:
            driver.find_element(By.CSS_SELECTOR, 'button[id="details-button"]')
            print('\033[0;31m浏览器[%s]提交任务超时,尝试刷新\033[0m' % x)
            driver.refresh()
        except:
            pass
        try:
            driver.find_element(By.CSS_SELECTOR, '[class="text-danger strong-700 p-2"]')
            print('\033[0;31m浏览器[%s]无法提交任务,请检查.60秒后退出\033[0m' % x)
            time.sleep(60)
            break
        except:
            pass
        # 检查浏览器是否关闭
        if check_windows(driver, main_windows) == "close":
            print('\033[0;31m浏览器[%s]:已关闭,释放线程\033[0m' % x)
            break
        time.sleep(1)
        reg += 1
        if reg == 30:
            try:
                submitpre = driver.find_element(By.ID, 'register-submit')
                reg = 0
                ActionChains(driver) \
                    .scroll_to_element(submitpre) \
                    .perform()
                time.sleep(random.uniform(1, 2))
                submitpre.click()
            except:
                pass


def premint(driver, x, close_url, dc_open, type_no, t1, t2, t_bot):
    # 开始PRE网页任务
    main_windows = driver.current_window_handle  # 获取当前标签页句柄
    # first_windows(driver, pre_windows)  # 切换句柄
    # print("浏览器[%s]:开始检测pre" % x)
    switch_window(driver)
    # checkc_loudflare(driver, x)
    try:
        WebDriverWait(driver, 60).until(EC.visibility_of(driver.find_element(By.ID, 'register-submit')))
        gettwitterlink(driver, x, type_no)
        switch_window(driver)
        # first_windows(driver)  # 切换PRE句柄

        # print("切换句柄")

        try:  # 检查邮箱任务
            driver.find_element(By.CSS_SELECTOR, '#step-custom #id_custom_field')
            try:
                driver.find_element(By.XPATH, "//*[contains(@placeholder, 'mail')]")
                getemail(driver, x, type_no)
            except NoSuchElementException:
                try:
                    driver.find_element(By.XPATH, "//*[contains(@placeholder, 'wallet')]")
                    getwallet(driver, x, type_no)
                except NoSuchElementException:
                    print('\033[0;38m浏览器[%s]:检测到未知必填项，跳过...\033[0m' % x)
        except:
            pass
        # ------可删除
        try:  # 检查额外任务
            driver.find_element(By.CSS_SELECTOR, '#step-custom #id_custom_field')
            try:
                user = driver.find_element(By.XPATH, "//*[contains(@placeholder, 'Account')]")
                user.send_keys(handle)
            except:
                pass
        except:
            pass
        # ------可删除
        try:  # 检查dc任务
            driver.find_element(By.CSS_SELECTOR, '#step-discord .col-12>div>a')
            dc_open = 1
            # print('\033[0;36m浏览器[%s]:等待手动操作discord任务\033[0m' % x)
            # getdiscordlink(driver, x, type_no)
            # while True:
            #     handles = driver.window_handles
            #     if len(handles) > 1:
            #         # discord_step(driver, x)
            #         while True:
            #             handles = driver.window_handles
            #             if len(handles) <= 1:
            #                 break
            #             time.sleep(1)
            #         break
            #     time.sleep(1)
            getdiscordlink(driver, x, type_no)
        except:
            pass
        clicksubmit(driver, x, close_url, dc_open, t1, t2, main_windows, t_bot)  # 提交任务
    except:
        checkpre(driver, x, close_url, dc_open, main_windows)


def alphabot(driver, x, close_url, type_no, dc_open, t1, t2):
    main_windows = driver.current_window_handle  # 获取当前标签页句柄
    # first_windows(driver, pre_windows)  #
    print("开始执行alphabot")
    switch_window(driver)
    try:
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR, '[type="submit"]')))
        gettwitterlink(driver, x, type_no)
        switch_window(driver)
        # 检查dc任务
        try:
            discord = WebDriverWait(driver, 60).until(
                EC.visibility_of_any_elements_located(
                    (By.XPATH, '//div[starts-with(@class, "MuiBox-root css-0")]'
                               '//div[contains(@class, "MuiAlert-standard")]//a')))
            for i, goods in enumerate(discord):
                href = goods.get_attribute("href")
                if "discord" in href:
                    dc_open = 1
            if dc_open == 1:
                getdiscordlink(driver, x, type_no)
                print('\033[0;36m浏览器[%s]:等待手动操作discord任务\033[0m' % x)
                while True:
                    handles = driver.window_handles
                    if len(handles) <= 1:
                        break
                    time.sleep(1)
        except:
            print('\033[0;31m浏览器[%s]:获取discord链接出错.\033[0m' % x)
        switch_window(driver)
        recaptcha(driver, x)  # recaptcha验证码
        clicksubmit_bot(driver, x, close_url, dc_open, t1, t2, main_windows)  # 提交任务
    except:
        pass


def heymint(driver, x, close_url, type_no, dc_open, t1, t2):
    main_windows = driver.current_window_handle  # 获取当前标签页句柄
    # first_windows(driver, pre_windows)  #
    # print("开始执行alphabot")
    switch_window(driver)
    try:
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR, '[type="submit"]')))
        gettwitterlink(driver, x, type_no)
        switch_window(driver)
        try:  # 检查dc任务
            driver.find_element(By.CSS_SELECTOR, '[class="grid gap-1"] a')
            dc_open = 1
            getdiscordlink(driver, x, type_no)
            reg = 0
            while True:
                handles = driver.window_handles
                if len(handles) <= 1:
                    break
                if reg == 0:
                    print('\033[0;36m浏览器[%s]:等待手动操作discord任务\033[0m' % x)
                    reg = 1
                time.sleep(1)
        except:
            pass
        try:  # 推特用户名
            user = driver.find_element(By.XPATH, '//textarea[contains(@id, "question")]')
            user.send_keys(handle)
            time.sleep(2)
        except:
            pass
        clicksubmit_heymint(driver, x, close_url, dc_open, t1, t2, main_windows)  # 提交任务
    except:
        pass


def getlink(driver, x, type_no):
    try:
        link = WebDriverWait(driver, 10).until(
            EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '[class="mt-2 flex-col"] a')))
        # twitter = driver.find_element(By.CSS_SELECTOR, "#step-twitter .col-12>div>a")
        # print("浏览器[%s]:开始执行Twitter任务" % x)
        for i, goods in enumerate(link):
            switch_window(driver)
            href = goods.get_attribute("href")
            if 'twitter' in href:
                goods.click()
                time.sleep(1)
                twitter_step(driver, x)
            time.sleep(1)
            if 'discord' in href:
                goods.click()
                time.sleep(1)
                # discord_step(driver, x)
                reg = 0
                while True:
                    handles = driver.window_handles
                    if len(handles) <= 1:
                        break
                    if reg == 0:
                        print('\033[0;36m浏览器[%s]:等待手动操作discord任务\033[0m' % x)
                        reg = 1
                    if len(handles) >= 3:
                        time.sleep(1)
                        switch_window(driver)
                        if driver.title == "New Tab":
                            webclose(driver)
                            time.sleep(1)
                            print('\033[0;36m浏览器[%s]:检查discord任务\033[0m' % x)
                            discord_step(driver, x)
                    time.sleep(1)
            time.sleep(1)
        switch_window(driver)
        # 转发任务
        reg = 0
        while True:
            try:
                twitter_iframe = driver.find_element(By.CSS_SELECTOR, '[title="Twitter Tweet"]')
                driver.switch_to.frame(twitter_iframe)
                # print("切入第二个窗口")
                try:
                    read = driver.find_element(By.CSS_SELECTOR, '[aria-label="View on Twitter"]')
                    scroll_origin = ScrollOrigin.from_element(read)
                    ActionChains(driver) \
                        .scroll_from_origin(scroll_origin, 0, -200) \
                        .perform()
                    time.sleep(1)
                    read.click()
                    time.sleep(1)
                    twitter_step(driver, x)
                    time.sleep(1)
                    switch_window(driver)
                    break
                except:
                    pass
                driver.switch_to.default_content()  # 返回主窗口
            except:
                pass
            try:
                read = driver.find_element(By.XPATH, '//a[contains(text(),"This Tweet")]')
                scroll_origin = ScrollOrigin.from_element(read)
                ActionChains(driver) \
                    .scroll_from_origin(scroll_origin, 0, -200) \
                    .perform()
                time.sleep(1)
                read.click()
                time.sleep(1)
                twitter_step(driver, x)
                time.sleep(1)
                switch_window(driver)
                break
            except:
                pass
            time.sleep(1)
            reg += 1
            if reg == 60:
                print('\033[0;31m浏览器[%s]:加载转发链接出错\033[0m' % x)
                driver.refresh()
    except:
        print('\033[0;31m浏览器[%s]:获取Twitter链接出错...\033[0m' % x)
    print('浏览器[%s]:Twitter任务结束,操作验证码' % x)
    recaptcha(driver, x)


def superful(driver, x, close_url, type_no, dc_open, t1, t2):
    main_windows = driver.current_window_handle  # 获取当前标签页句柄
    # first_windows(driver, pre_windows)  #
    # print("开始执行alphabot")
    switch_window(driver)
    try:
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((
                By.XPATH, "//p[text()='Join']")))
        getlink(driver, x, type_no)
        switch_window(driver)
        try:  # 推特用户名
            user = driver.find_element(By.XPATH, '//textarea[contains(@id, "question")]')
            user.send_keys(handle)
            time.sleep(2)
        except:
            pass
        clicksubmit_superful(driver, x, close_url, dc_open, t1, t2, main_windows)  # 提交任务
    except:
        clicks_superful(driver, x, main_windows, t1, t2)


def openads(x, url, dc_open, i, serial_number_all, t1, t2, t_bot):
    global type_no
    print('\033[95m>>>>>>>>>>浏览器[%s]:等待执行  当前总进度[%s/%s]<<<<<<<<<<\033[0m' % (x, i + 1, serial_number_all))
    # get直接返回，不再等待界面加载完成
    ads_id = str(x)
    ads_query = "&open_tabs=1&ip_tab=1"
    open_url = "http://local.adspower.net:50325/api/v1/browser/start?serial_number=" + ads_id + ads_query
    close_url = "http://local.adspower.net:50325/api/v1/browser/stop?serial_number=" + ads_id
    # print(open_url)
    while True:
        resp = requests.get(open_url).json()
        if resp:
            if resp["code"] != 0:
                print("\033[0;31m浏览器[%s]打开出错,正在重试...\033[0m" % x)
                print("\033[0;31m浏览器[%s]错误信息:[%s]\033[0m" % (x, resp))
                # pool_sema.release()  # 解锁
                # sys.exit()
            else:
                break
        time.sleep(2)
    # 打开浏览器
    chrome_driver = Service(resp["data"]["webdriver"])
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
    # 禁止图片加载
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    # 设置页面加载策略，none表示非阻塞模式。
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["pageLoadStrategy"] = "eager"
    driver = webdriver.Chrome(service=chrome_driver, options=chrome_options, desired_capabilities=desired_capabilities)
    # 关闭多余窗口
    while True:
        handles = driver.window_handles
        if len(handles) > 1:
            webclose(driver)
        else:
            break
        time.sleep(1)
    # 新建窗口
    time.sleep(random.uniform(1, 2))
    # driver.switch_to.new_window()
    # time.sleep(random.uniform(1, 2))
    switch_window(driver)
    # 获取url
    if url:
        col = [url]
    else:
        sheet = pd.read_excel('待操作项目.xlsx')
        col = sheet['url']
        # print(col)
    links = []
    for i, goods in enumerate(col):
        links.append(goods)
    random.shuffle(links)
    for i, url in enumerate(links):
        print("浏览器[%s]:开始执行项目[%s/%s]:[%s]" % (x, i + 1, len(links), url))
        # 关闭多余窗口
        while True:
            handles = driver.window_handles
            if len(handles) > 1:
                webclose(driver)
            else:
                break
            time.sleep(1)
        time.sleep(random.uniform(1, 2))
        switch_window(driver)
        if "premint" in url:
            type_no = 1
        elif "alphabot" in url:
            type_no = 2
        elif "heymint" in url:
            type_no = 3
        elif "superful" in url:
            type_no = 4
        # 打开网页
        try:
            driver.get(url)
            if type_no == 1:
                premint(driver, x, close_url, dc_open, type_no, t1, t2, t_bot)
            if type_no == 2:
                alphabot(driver, x, close_url, type_no, dc_open, t1, t2)
            if type_no == 3:
                heymint(driver, x, close_url, type_no, dc_open, t1, t2)
            if type_no == 4:
                superful(driver, x, close_url, type_no, dc_open, t1, t2)
            time.sleep(3)
        except:
            print('\033[0;31m浏览器[%s]:加载网页失败,尝试重启浏览器\033[0m' % x)
            requests.get(close_url).json()
            time.sleep(5)
            openads(x, url, dc_open, i, serial_number_all, t1, t2, t_bot)

    # 关闭浏览器
    while True:
        # requests.get(close_url)
        closeresp = requests.get(close_url).json()
        time.sleep(3)
        if closeresp:
            if closeresp["code"] == 0:
                print('\033[0;32m浏览器[%s]:任务完成\033[0m' % x)
                break
            if closeresp["msg"] == 'User_id is not open':
                # print("\033[0;31m浏览器[%s]已关闭.释放线程\033[0m" % x)
                break
            if closeresp["code"] != 0:
                print("\033[0;31m浏览器[%s]关闭出错，正在重试...错误代码：[%s]\033[0m" % (x, closeresp))
                # pool_sema.release()  # 解锁
                # sys.exit()
        time.sleep(2)
    pool_sema.release()  # 解锁


threads = []  # 定义线程组

type_no = 0
discord_ls = []
dc_open = 0  # discord任务开关
excel_new()
url = input("请输入要执行的项目链接:")

max_connections = int(input("请输入最大线程数(默认3):") or 3)  # 定义最大线程数
pool_sema = threading.BoundedSemaphore(max_connections)  # 或使用Semaphore方法

t_bot = int(input("是否开启推特养号(默认开启):") or 1)  # 推特养号

if t_bot == 1:
    t1, t2 = 1, 2
else:
    t1, t2 = str(input("请输入提交延迟,格式:[10-100],(默认45-90):") or '45-90').split('-')  # 定义提交延迟

adsarr = input("请输入浏览器序号，支持格式：【1】,【1,3,8】,【1-20】:") or "1 - 50"

executed_num = int(input("请输入本轮执行数量:") or "50")
start_time = datetime.datetime.now().replace(microsecond=0)
# max_connections = 1
# pool_sema = threading.BoundedSemaphore(max_connections)  # 或使用Semaphore方法
# t1,t2 = 1,2
# adsarr = "1"
# executed_num = 1
serial_number = []

if adsarr.isdigit():
    serial_number.append(adsarr)
elif '-' in adsarr:
    adsarrs = adsarr.split('-')
    ads_start_num = int(adsarrs[0])
    ads_stop_num = int(adsarrs[1]) + 1
    for x in range(ads_start_num, ads_stop_num):  # 创建线程，并追加入线程数组
        serial_number.append(x)
elif ',' in adsarr:
    adsarrs = adsarr.split(',')
    for x in range(len(adsarrs)):
        serial_number.append(int(adsarrs[x]))
else:
    print("输入的格式有误")
random.shuffle(serial_number)
executed = serial_number[0:executed_num]
del serial_number[0:executed_num]
type_text = "未知"
if url:
    if "premint" in url:
        type_text = "premint"
    elif "alphabot" in url:
        type_text = "alphabot"
excel_re(adsarr=executed, unexecuted=serial_number, type_text=type_text)
serial_number_all = len(executed)
print("本次操作顺序：%s" % executed)
for i, x in enumerate(executed):  # 创建线程，并追加入线程数组
    thread = threading.Thread(target=openads, args=(x, url, dc_open, i, serial_number_all, t1, t2, t_bot),
                              name='浏览器[' + str(x) + ']')
    threads.append(thread)

# 获取线程数
loops = range(len(threads))

# 启动线程
for i in loops:
    # print('线程名称%s' % threads[i].name)
    pool_sema.acquire()  # 加锁，限制线程数
    threads[i].start()
    time.sleep(1.5)
# 守护线程
# for i in loops:
#     pool_sema.acquire()  # 加锁，限制线程数
#     threads[i].join()
#     time.sleep(1.2)
while True:
    if len(threading.enumerate()) <= 1:
        end_time = datetime.datetime.now().replace(microsecond=0)
        all_time = end_time - start_time
        print('\033[0;30;47m♦♦♦♦♦♦♦♦♦\033[0m')
        print('\033[0;30;47m♦所有任务执行完毕!♦\033[0m')
        print('\033[0;30;47m♦♦♦♦♦♦♦♦♦\033[0m')
        print('\033[0;30;47m♦完成时间:[%s]♦\033[0m' % end_time)
        print('\033[0;30;47m♦累计用时:[%s]♦\033[0m' % all_time)
        break
    else:
        time.sleep(3)
# input('所有任务执行完成...按回车结束...')
