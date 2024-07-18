from DrissionPage import ChromiumPage, ChromiumOptions

# 设置ChromiumOptions
co = ChromiumOptions().set_paths(local_port=3002)  # 端口号，如果冲突就换一个
page = ChromiumPage(addr_or_opts=co)
page.set.timeouts(0.1)

def unretweet(page, user):
    reg = 0
    page.get(f'https://x.com/{user}')
    while True:
        unretweet = page('@data-testid=unretweet')
        if unretweet:
            ele = unretweet.parent(2)
            unlike = ele('@data-testid=unlike')
            if unlike:
                unlike.click()
                page.wait(0.5)
            unretweet.click()
            page.wait(0.5)
        else:
            page.scroll.down(800)
            continue

        unretweetConfirm = page('@data-testid=unretweetConfirm')
        if unretweetConfirm:
            unretweetConfirm.click()
            page.wait(0.5)
            reg += 1
            print(f'已撤销{reg}个转推。')
        else:
            break

def del_tweet(page, user):
    reg = 0
    page.get(f'https://x.com/{user}')
    while True:
        more = page('@aria-label=More')
        if more:
            more.click()
            page.wait(0.5)
            delete = page('text=Delete')
            if delete:
                delete.click()
                page.wait(0.2)
                confirm_delete = page('text=Delete')
                if confirm_delete:
                    confirm_delete.click()
                    page.wait(0.2)
                    reg += 1
                    print(f'已删除{reg}个推文。')
            if page.tabs_count > 1:
                print('任务异常结束')
                break
        else:
            page.scroll.down(800)
    page.wait(0.2)

def del_replies(page, user):
    reg = 0
    page.get(f'https://x.com/{user}/with_replies')
    while True:
        tw = page(f't:article@@text():{user}')
        if tw:
            more = tw('@aria-label=More')
            if more:
                more.click()
                page.wait(0.5)
                delete = page('text=Delete')
                if delete:
                    delete.click()
                    page.wait(0.2)
                    confirm_delete = page('text=Delete')
                    if confirm_delete:
                        confirm_delete.click()
                        page.wait(0.2)
                        reg += 1
                        print(f'已删除{reg}个回复。')
                if page.tabs_count > 1:
                    print('任务异常结束')
                    break
        else:
            page.scroll.down(800)
        page.wait(0.2)


def main():
    if not 'x.com' in page.url:
        page.get('https://x.com')
    while True:
        if page('@aria-label=Home timeline', timeout=10):
            break
        else:
            print("请先登录到推特首页，10秒后重试。")

    try:
        user = input("请输入自己的用户名:(例如：lumaoyangmao): ")
        type = int(input("请输入要删除的类型(1、撤回转推点赞 2、删除推文 3、删除回复): "))
        if type == 1:
            unretweet(page, user)
        elif type == 2:
            del_tweet(page, user)
        elif type == 3:
            del_replies(page, user)
        else:
            print("无效的选项，请输入1、2或3")
    except ValueError:
        print("请输入有效的数字")

if __name__ == "__main__":
    main()
