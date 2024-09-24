class PageNames:
    ENTRY_POINT = 'entry-point'
    USER_LOGIN = 'user-login'
    INDEX = 'index'


class SessionContent:
    PAGES_DATA = 'pages_data'
    TOKEN = 'token'
    CURRENT_USER = 'current_user'


class ApiEndpoints:
    TOKEN = '/core/token/'
    CURRENT_USER = '/core/current-user/'
    PAGE_PUBLIC = '/core/page-public/'
    PAGE_PRIVATE = '/core/page-private/'
