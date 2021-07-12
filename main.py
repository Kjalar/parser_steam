import os.path
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


file_path = os.path.normpath(os.path.dirname(__file__))
url_login = "https://store.steampowered.com/login/"


def get_user_url():
    while True:
        user_url = input('Введите url страницы пользователя: ')
        try:
            if user_url[-1] == '/':
                user_url = user_url[:-1]
            list_user_url = user_url.split('/')
            assert list_user_url[0] in ['http:', 'https:']
            for index, i in enumerate(list_user_url):
                if i in ['id', 'profiles']:
                    result += f'/{i}/{list_user_url[index + 1]}/games/?tab=all'
                    break
                if index == 0:
                    result = f'{i}/'
                    continue
                result += f'/{i}'
            break
        except AssertionError:
            print('Введите url с указанием http:// или https://\n')
        except:
            print('Некорректный url.\n')
    return result


def get_choice_auth():
    choice_auth = input('Некоторые пользователи скрывают в настройках приватности информацию о своем аккаунте.\n\
Вы можете авторизироваться и подсчитать количество часов в играх, если этот пользователь находится у вас в друзьях.\n\
Хотите авторизироваться? (Yes/No): ')

    if choice_auth.lower() in ['yes', 'y', 'l', 'lf', 'да', 'д']:
        return True
    return False


def setup_webdriver(choice_auth=False):
    if choice_auth:
        return webdriver.Chrome(executable_path=os.path.join(file_path, 'chromedriver'))
    else:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        return webdriver.Chrome(executable_path=os.path.join(file_path, 'chromedriver'), options=options)


def parse_info(driver):
    try:
        # для иностранных языков лучше сделать проверку другую для поиска часов
        games_list = driver.find_elements_by_class_name('gameListRowItemTopPrimary')
        error_list = driver.find_elements_by_id('message')

        if games_list:
            result = 0
            for game in games_list:
                list_pages_html = game.text.split('\n')
                if len(list_pages_html) == 2:
                    result += float(list_pages_html[1].split()[0])
            print(f'Всего часов в играх: {round(result, 2)}')
            print(f'Всего дней в играх: {round(result / 24, 2)}')

            detail_info = input('Вывести подробную информацию? (yes/no): ')
            if detail_info.lower() in ['yes', 'y', 'l', 'lf', 'да', 'д']:
                print()
                for game in games_list:
                    print(game.text)

        elif error_list:
            if 'Указанный профиль не найден.' in error_list[0].text:
                print('Указанный профиль не найден.')
            else:
                print('Произошла ошибка при поиске. Проверьте корректность введенных данных.')
        else:
            print('Информация по играм не найдена.')

    except Exception as ex:
        print(ex)


def auth_for_parse(driver, url_profile):
    count = 10
    while count:
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "account_pulldown"))
            )
            print('Вы успешно авторизировались.')
            driver.get(url_profile)
            parse_info(driver)
            break
        except TimeoutException:
            print('Пожалуйста, войдите в свой аккаунт чтобы продолжить.')
            count -= 1
    if count == 0:
        print('Время ожидания закончилось.')


def start_without_auth(url_profile):
    try:
        driver = setup_webdriver()
        driver.get(url_profile)
        parse_info(driver)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def start_with_auth(url_profile):
    try:
        driver = setup_webdriver(choice_auth=True)
        driver.get(url_login)
        auth_for_parse(driver, url_profile)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():
    url_profile = get_user_url()

    # ручная авторизация пользователя
    if get_choice_auth():
        start_with_auth(url_profile)

    # без авторизации
    else:
        start_without_auth(url_profile)


if __name__ == '__main__':
    main()
