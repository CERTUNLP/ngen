export const API_SERVER = process.env.REACT_APP_API_SERVER;
export const BASE_URL = process.env.REACT_APP_BASE_URL || '/metrics';
export const BASENAME = process.env.REACT_APP_BASENAME || '';
export const BASE_TITLE = ' | ngen ';
export const PAGE = '?page=';

export const CONFIG = {
    layout: 'vertical', // disable on free version
    subLayout: '', // disable on free version
    collapseMenu: false, // mini-menu
    layoutType: 'menu-dark', // disable on free version
    navIconColor: false, // disable on free version
    headerBackColor: 'header-default', // disable on free version
    navBackColor: 'navbar-default', // disable on free version
    navBrandColor: 'brand-default', // disable on free version
    navBackImage: false, // disable on free version
    rtlLayout: false, // disable on free version
    navFixedLayout: true, // disable on free version
    headerFixedLayout: false, // disable on free version
    boxLayout: false, // disable on free version
    navDropdownIcon: 'style1', // disable on free version
    navListIcon: 'style1', // disable on free version
    navActiveListColor: 'active-default', // disable on free version
    navListTitleColor: 'title-default', // disable on free version
    navListTitleHide: false, // disable on free version
    configBlock: true, // disable on free version
    layout6Background: 'linear-gradient(to right, #A445B2 0%, #D41872 52%, #FF0066 100%)', // disable on free version
    layout6BackSize: '' // disable on free version
};

export const COMPONENT_URL = {
    tlp: "administration/tlp/",
    feed: "administration/feed/",
    priority: "administration/priority/",
    state: "state/",
    edge: "edge/",
    template: "template/",
    case: "case/",
    evidence: "evidence/",
    event: "event/",
    taxonomy: "taxonomy/",
    report: "report/",
    network: "network/",
    contact: "contact/",
    entity: "entity/",
    user: "user/",
    playbook: "playbook/",
    task: "task/",
    todo: "todo/",
    artifact: "artifact/",
    announcement: "announcement/",
    register: "register/",
    checkSession: "checkSession/",
    login: "ctoken/",
    searchCase: "search/case/",
    logout: "ctoken/logout/",
    refreshCookieToken: "ctoken/refresh/",
    stringidentifier: "stringidentifier/",
    dashboardFeed: "dashboard/feeds",
    dashboardEvent: "dashboard/events",
    dashboardCases: "dashboard/cases",
    dashboardNetworkEntities: "dashboard/network_entities",
    constance: "constance/",
    profile: "profile/",
    taxonomyMinifiedList:"minified/taxonomy/",
    priorityMinifiedList: "minified/priority/",
    tlpMinifiedList: "minified/tlp/",
    feedMinifiedList:"minified/feed/",
    stateMinifiedList: "minified/state/",
    entityMinifiedList: "minified/Entity",
    contactMinifiedList: "minified/Contact/",
    userMinifiedList: "minified/User/",
    caseMinifiedList:"/minified/Case/",
    artifactMinifiedList:"minified/Artifact/",
    group: "groups/"

};