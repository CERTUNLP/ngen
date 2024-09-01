import { logout } from "./api/services/auth";

const menuItems = {
  items: [
    {
      id: "principal",
      title: "menu.main",
      type: "group",
      children: [
        {
          id: "dashboard",
          title: "menu.metrics",
          type: "item",
          url: "/metrics",
          icon: "feather icon-home",
          breadcrumbs: false
        },
        {
          id: "Eventos",
          title: "menu.events",
          type: "item",
          url: "/events",
          classes: "",
          icon: "feather icon-alert-circle",
          breadcrumbs: false
        },
        {
          id: "case",
          title: "menu.cases",
          type: "item",
          url: "/cases",
          icon: "feather icon-search",
          breadcrumbs: false
        }
      ]
    },
    {
      id: "constituency",
      title: "menu.constituency",
      type: "group",
      icon: "fas fa-network-wired",
      children: [
        {
          id: "entity",
          title: "menu.entities",
          type: "item",
          url: "/entities",
          icon: "fas fa-cubes",
          breadcrumbs: false
        },
        {
          id: "networks",
          title: "menu.networks",
          type: "item",
          url: "/networks",
          icon: "feather icon-share-2",
          breadcrumbs: false
        },
        {
          id: "contacts",
          title: "menu.contacts",
          type: "item",
          url: "/contacts",
          icon: "far fa-address-book",
          breadcrumbs: false
        }
      ]
    },
    {
      id: "config",
      title: "menu.config",
      type: "group",
      icon: "icon-pages",
      children: [
        {
          id: "platform",
          title: "menu.platform",
          type: "collapse",
          icon: "feather icon-settings",
          link: false,
          children: [
            {
              id: "tlp",
              title: "menu.tlp",
              type: "item",
              url: "/tlp",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "reporte",
              title: "menu.report",
              type: "item",
              url: "/reports",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "feeds",
              title: "menu.feeds",
              type: "item",
              url: "/feeds",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "priority",
              title: "menu.priorities",
              type: "item",
              url: "/priorities",
              classes: "",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "playbook",
              title: "menu.playbooks",
              type: "item",
              url: "/playbooks",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "taxonomy",
              title: "menu.taxonomies",
              type: "item",
              url: "/taxonomies",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "Estados",
              title: "menu.states",
              type: "item",
              url: "/states",
              classes: "",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "Plantilla",
              title: "menu.templates",
              type: "item",
              url: "/templates",
              classes: "",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "users",
              title: "menu.users",
              type: "item",
              url: "/users",
              classes: "",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "Configuración",
              title: "menu.config",
              type: "item",
              url: "/setting",
              classes: "",
              icon: "",
              breadcrumbs: false
            }
          ]
        }
      ]
    }
  ],
  itemsBottom: [
    {
      id: "principal",
      title: "",
      type: "group",
      children: [
        {
          id: "profile",
          title: "menu.profile",
          type: "item",
          url: "/profile",
          classes: "",
          icon: "feather icon-user",
          breadcrumbs: false
        },
        {
          id: "logout",
          title: "menu.logout",
          type: "item",
          url: "#",
          basic_link: true,
          classes: "logout-btn",
          icon: "fa fa-sign-out-alt",
          breadcrumbs: false,
          onClick: logout
        }
      ]
    }
  ]
};

export default menuItems;
