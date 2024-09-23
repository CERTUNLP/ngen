import React, { Fragment, lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import Loader from "./components/Loader/Loader";
import AdminLayout from "./layouts/AdminLayout";

import { BASE_URL } from "./config/constant";

import GuestGuard from "./components/Auth/GuestGuard";
// import AuthGuard from "./components/Auth/AuthGuard";
import PermissionGuard from "./components/Auth/PermissionGuard";

export const renderRoutes = (routes = []) => (
  <Suspense fallback={<Loader />}>
    <Routes>
      {routes.map((route, i) => {
        const Guard = route.guard || Fragment;
        const Layout = route.layout || Fragment;
        const Element = route.element;
        const permissions = route.permissions || [];

        return (
          <Route
            key={i}
            path={route.path}
            element={
              Guard === Fragment ? (
                <Layout>{route.routes ? renderRoutes(route.routes) : <Element />}</Layout>
              ) : (
                <Guard permissions={permissions}>
                  <Layout>{route.routes ? renderRoutes(route.routes) : <Element />}</Layout>
                </Guard>
              )
            }
          />
        );
      })}
    </Routes>
  </Suspense>
);

const routes = [
  {
    exact: "true",
    guard: GuestGuard,
    path: "/login",
    element: lazy(() => import("./views/auth/signin/SignIn1"))
  },
  {
    exact: "true",
    path: "/auth/signin-1",
    element: lazy(() => import("./views/auth/signin/SignIn1"))
  },
  {
    exact: "true",
    path: "/auth/signup-1",
    element: lazy(() => import("./views/auth/signup/SignUp1"))
  },
  {
    exact: "true",
    path: "/unauthorized",
    element: lazy(() => import("./views/auth/unauthorized/Unauthorized"))
  },
  {
    exact: "true",
    path: "/metrics",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_dashboard"],
    element: lazy(() => import("./views/dashboard/DashDefault"))
  },
  {
    exact: "true",
    path: "/feeds",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_feed"],
    element: lazy(() => import("./views/feeds/ListFeed"))
  },
  {
    exact: "true",
    path: "/feeds/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_feed"],
    element: lazy(() => import("./views/feeds/CreateFeed"))
  },
  {
    exact: "true",
    path: "/feeds/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_feed"],
    element: lazy(() => import("./views/feeds/EditFeed"))
  },
  {
    exact: "true",
    path: "/taxonomies",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_taxonomy"],
    element: lazy(() => import("./views/taxonomy/ListTaxonomies"))
  },
  {
    exact: "true",
    path: "/taxonomies/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_taxonomy"],
    element: lazy(() => import("./views/taxonomy/CreateTaxonomy"))
  },
  {
    exact: "true",
    path: "/taxonomies/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_taxonomy"],
    element: lazy(() => import("./views/taxonomy/EditTaxonomy"))
  },
  {
    exact: "true",
    path: "/taxonomyGroups",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_taxonomygroup"],
    element: lazy(() => import("./views/taxonomyGroup/ListTaxonomyGroups"))
  },
  {
    exact: "true",
    path: "/taxonomyGroups/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_taxonomygroup"],
    element: lazy(() => import("./views/taxonomyGroup/CreateTaxonomyGroup"))
  },
  {
    exact: "true",
    path: "/taxonomyGroups/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_taxonomygroup"],
    element: lazy(() => import("./views/taxonomyGroup/EditTaxonomyGroup"))
  },
  {
    exact: "true",
    path: "/tlp",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_tlp"],
    element: lazy(() => import("./views/tlp/ListTLP"))
  },
  {
    exact: "true",
    path: "/contacts",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_contact"],
    element: lazy(() => import("./views/contact/ListContact"))
  },
  {
    exact: "true",
    path: "/contacts/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_contact"],
    element: lazy(() => import("./views/contact/CreateContact"))
  },
  {
    exact: "true",
    path: "/contacts/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_contact"],
    element: lazy(() => import("./views/contact/EditContact"))
  },
  {
    exact: "true",
    path: "/entities",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_networkentity"],
    element: lazy(() => import("./views/entity/ListEntity"))
  },
  {
    exact: "true",
    path: "/entities/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_networkentity"],
    element: lazy(() => import("./views/entity/CreateEntity"))
  },
  {
    exact: "true",
    path: "/entities/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_networkentity"],
    element: lazy(() => import("./views/entity/EditEntity"))
  },
  {
    exact: "true",
    path: "/networks",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_network"],
    element: lazy(() => import("./views/network/ListNetwork"))
  },
  {
    exact: "true",
    path: "/networks/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_network"],
    element: lazy(() => import("./views/network/CreateNetwork"))
  },
  {
    exact: "true",
    path: "/networks/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_network"],
    element: lazy(() => import("./views/network/EditNetwork"))
  },
  {
    exact: "true",
    path: "/priorities",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_priority"],
    element: lazy(() => import("./views/priority/ListPriority"))
  },
  {
    exact: "true",
    path: "/priorities/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_priority"],
    element: lazy(() => import("./views/priority/CreatePriority"))
  },
  {
    exact: "true",
    path: "/priorities/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_priority"],
    element: lazy(() => import("./views/priority/EditPriority"))
  },
  {
    exact: "true",
    path: "/users",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_user"],
    element: lazy(() => import("./views/user/ListUser"))
  },
  {
    exact: "true",
    path: "/users/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_user"],
    element: lazy(() => import("./views/user/CreateUser"))
  },
  {
    exact: "true",
    path: "/users/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_user"],
    element: lazy(() => import("./views/user/EditUser"))
  },
  {
    exact: "true",
    path: "/states",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_state"],
    element: lazy(() => import("./views/state/ListState"))
  },
  {
    exact: "true",
    path: "/states/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_state"],
    element: lazy(() => import("./views/state/CreateState"))
  },
  {
    exact: "true",
    path: "/states/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_state"],
    element: lazy(() => import("./views/state/EditState"))
  },
  {
    exact: "true",
    path: "/events",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_event"],
    element: lazy(() => import("./views/event/ListEvent"))
  },
  {
    exact: "true",
    path: "/events/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_event"],
    element: lazy(() => import("./views/event/CreateEvent"))
  },
  {
    exact: "true",
    path: "/events/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_event"],
    element: lazy(() => import("./views/event/EditEvent"))
  },
  {
    exact: "true",
    path: "/events/view",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_event"],
    element: lazy(() => import("./views/event/ReadEvent"))
  },
  {
    exact: "true",
    path: "/playbooks",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_playbook"],
    element: lazy(() => import("./views/playbook/ListPlaybook"))
  },
  {
    exact: "true",
    path: "/playbooks/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_playbook"],
    element: lazy(() => import("./views/playbook/CreatePlaybook"))
  },
  {
    exact: "true",
    path: "/playbooks/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_playbook"],
    element: lazy(() => import("./views/playbook/EditPlaybook"))
  },
  {
    exact: "true",
    path: "/cases",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_case"],
    element: lazy(() => import("./views/case/ListCase"))
  },
  {
    exact: "true",
    path: "/cases/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_case"],
    element: lazy(() => import("./views/case/CreateCase"))
  },
  {
    exact: "true",
    path: "/cases/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_case"],
    element: lazy(() => import("./views/case/EditCase"))
  },
  {
    exact: "true",
    path: "/cases/view",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_case"],
    element: lazy(() => import("./views/case/ReadCase"))
  },
  {
    exact: "true",
    path: "/templates",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_template"],
    element: lazy(() => import("./views/template/ListTemplate"))
  },
  {
    exact: "true",
    path: "/templates/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_template"],
    element: lazy(() => import("./views/template/CreateTemplate"))
  },
  {
    exact: "true",
    path: "/templates/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_template"],
    element: lazy(() => import("./views/template/EditTemplate"))
  },
  {
    exact: "true",
    path: "/reports",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_report"],
    element: lazy(() => import("./views/report/ListReport"))
  },
  {
    exact: "true",
    path: "/reports/edit",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["change_report"],
    element: lazy(() => import("./views/report/EditReport"))
  },
  {
    exact: "true",
    path: "/reports/create",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["add_report"],
    element: lazy(() => import("./views/report/CreateReport"))
  },
  {
    exact: "true",
    path: "/setting",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_constance"],
    element: lazy(() => import("./views/setting/EditSetting"))
  },
  {
    exact: "true",
    path: "/profile",
    layout: AdminLayout,
    guard: PermissionGuard,
    permissions: ["view_profile"],
    element: lazy(() => import("./views/profile/Profile"))
  },
  {
    path: "*",
    exact: "true",
    element: () => <Navigate to={BASE_URL} />
  }
];

export default routes;
