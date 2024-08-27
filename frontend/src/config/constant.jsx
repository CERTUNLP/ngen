export const API_SERVER = import.meta.env.VITE_APP_API_SERVER;
export const BASE_URL = import.meta.env.VITE_APP_BASE_URL || "/metrics";
export const BASENAME = import.meta.env.VITE_APP_BASENAME || "";
export const BASE_TITLE = " | ngen ";
export const PAGE = "?page=";
export const PAGE_SIZE = "PAGE_SIZE/";

export const CONFIG = {
  layout: "vertical", // disable on free version
  subLayout: "", // disable on free version
  collapseMenu: false, // mini-menu
  layoutType: "menu-dark", // disable on free version
  navIconColor: false, // disable on free version
  headerBackColor: "header-default", // disable on free version
  navBackColor: "navbar-default", // disable on free version
  navBrandColor: "brand-default", // disable on free version
  navBackImage: false, // disable on free version
  rtlLayout: false, // disable on free version
  navFixedLayout: true, // disable on free version
  headerFixedLayout: false, // disable on free version
  boxLayout: false, // disable on free version
  navDropdownIcon: "style1", // disable on free version
  navListIcon: "style1", // disable on free version
  navActiveListColor: "active-default", // disable on free version
  navListTitleColor: "title-default", // disable on free version
  navListTitleHide: false, // disable on free version
  configBlock: true, // disable on free version
  layout6Background: "linear-gradient(to right, #A445B2 0%, #D41872 52%, #FF0066 100%)", // disable on free version
  layout6BackSize: "" // disable on free version
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
  loginFrontend: "login/",
  searchCase: "search/case/",
  logout: "ctoken/logout/",
  logoutFrontend: "logout/",
  refreshCookieToken: "ctoken/refresh/",
  stringidentifier: "stringidentifier/",
  dashboardFeed: "dashboard/feeds",
  dashboardEvent: "dashboard/events",
  dashboardCases: "dashboard/cases",
  dashboardNetworkEntities: "dashboard/network_entities",
  constance: "constance/",
  profile: "profile/",
  taxonomyMinifiedList: "minified/taxonomy/",
  taxonomyGroupMinifiedList: "minified/taxonomygroup/",
  priorityMinifiedList: "minified/priority/",
  tlpMinifiedList: "minified/tlp/",
  feedMinifiedList: "minified/feed/",
  stateMinifiedList: "minified/state/",
  entityMinifiedList: "minified/entity",
  contactMinifiedList: "minified/contact/",
  userMinifiedList: "minified/user/",
  caseMinifiedList: "/minified/case/",
  artifactMinifiedList: "minified/artifact/",
  group: "groups/"
};
