class PageNames:
    ENTRY_POINT = 'entry-point'
    USER_LOGIN = 'user-login'
    INDEX = 'index'


class SessionContent:
    PAGES_DICT = 'pages_dict'
    TOKEN = 'token'
    CURRENT_USER = 'current_user'
    CONTEXT_BY_PAGE = 'context_by_page'


class ApiEndpoints:
    TOKEN = '/token/'
    CURRENT_USER = '/current-user/'
    PAGE_PUBLIC = '/page-public/'
    PAGE_PRIVATE = '/page-private/'
    CONTENT_BY_PAGE = '/content-public-by-page/'
