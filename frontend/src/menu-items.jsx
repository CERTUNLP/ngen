import { logout } from "./api/services/auth";
import { userIsNetworkAdmin } from "utils/permissions";

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
          id: "event",
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
          id: "network",
          title: "menu.networks",
          type: "item",
          url: "/networks",
          icon: "feather icon-share-2",
          breadcrumbs: false
        },
        {
          id: "contact",
          title: "menu.contacts",
          type: "item",
          url: "/contacts",
          icon: "far fa-address-book",
          breadcrumbs: false
        }
      ]
    },
    {
      id: "networkadminprincipal",
      title: "menu.networkadmin.main",
      type: "group",
      children: [
        {
          id: "networkadminevent",
          title: "menu.networkadmin.events",
          type: "item",
          url: "/networkadmin/events",
          classes: "",
          icon: "feather icon-alert-circle",
          breadcrumbs: false
        },
        {
          id: "networkadmincase",
          title: "menu.networkadmin.cases",
          type: "item",
          url: "/networkadmin/cases",
          icon: "feather icon-search",
          breadcrumbs: false
        }
      ]
    },
    {
      id: "networkadminconstituency",
      title: "menu.networkadmin.constituency",
      type: "group",
      icon: "fas fa-network-wired",
      children: [
        {
          id: "networkadminentity",
          title: "menu.networkadmin.entities",
          type: "item",
          url: "/networkadmin/entities",
          icon: "fas fa-cubes",
          breadcrumbs: false
        },
        {
          id: "networkadminnetwork",
          title: "menu.networkadmin.networks",
          type: "item",
          url: "/networkadmin/networks",
          icon: "feather icon-share-2",
          breadcrumbs: false
        },
        {
          id: "networkadmincontact",
          title: "menu.networkadmin.contacts",
          type: "item",
          url: "/networkadmin/contacts",
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
              id: "report",
              title: "menu.report",
              type: "item",
              url: "/reports",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "feed",
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
              id: "taxonomyGroup",
              title: "menu.taxonomygroups",
              type: "item",
              url: "/taxonomyGroups",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "state",
              title: "menu.states",
              type: "item",
              url: "/states",
              classes: "",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "template",
              title: "menu.templates",
              type: "item",
              url: "/templates",
              classes: "",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "user",
              title: "menu.users",
              type: "item",
              url: "/users",
              classes: "",
              icon: "",
              breadcrumbs: false
            },
            {
              id: "configuration",
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
