import React, { Fragment, lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import Loader from "./components/Loader/Loader";
import AdminLayout from "./layouts/AdminLayout";

import { BASE_URL } from "./config/constant";
import DashDefault from "./views/dashboard/DashDefault";

import GuestGuard from "./components/Auth/GuestGuard";
import AuthGuard from "./components/Auth/AuthGuard";

export const renderRoutes = (routes = []) => (
  <Suspense fallback={<Loader />}>
    <Routes>
      {routes.map((route, i) => {
        const Guard = route.guard || Fragment;
        const Layout = route.layout || Fragment;
        const Element = route.element;

        return (
          <Route
            key={i}
            path={route.path}
            element={
              <Guard>
                <Layout>{route.routes ? renderRoutes(route.routes) : <Element props={true} />}</Layout>
              </Guard>
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
    path: "*",
    layout: AdminLayout,
    guard: AuthGuard,
    routes: [
      {
        exact: "true",
        path: "/metrics",
        // element: lazy(() => import('./views/dashboard/DashDefault'))
        element: DashDefault
      },
      {
        exact: "true",
        path: "/feeds",
        element: lazy(() => import("./views/feeds/ListFeed"))
      },
      {
        exact: "true",
        path: "/feeds/create",
        element: lazy(() => import("./views/feeds/CreateFeed"))
      },
      {
        exact: "true",
        path: "/feeds/edit",
        element: lazy(() => import("./views/feeds/EditFeed"))
      },
      {
        exact: "true",
        path: "/taxonomies",
        element: lazy(() => import("./views/taxonomy/ListTaxonomies"))
      },
      {
        exact: "true",
        path: "/taxonomies/create",
        element: lazy(() => import("./views/taxonomy/CreateTaxonomy"))
      },
      {
        exact: "true",
        path: "/taxonomies/edit",
        element: lazy(() => import("./views/taxonomy/EditTaxonomy"))
      },
      {
        exact: "true",
        path: "/taxonomyGroups",
        element: lazy(() => import("./views/taxonomyGroup/ListTaxonomyGroups"))
      },
      {
        exact: "true",
        path: "/taxonomyGroups/create",
        element: lazy(() => import("./views/taxonomyGroup/CreateTaxonomyGroup"))
      },
      {
        exact: "true",
        path: "/taxonomyGroups/edit",
        element: lazy(() => import("./views/taxonomyGroup/EditTaxonomyGroup"))
      },
      {
        exact: "true",
        path: "/tlp",
        element: lazy(() => import("./views/tlp/ListTLP"))
      },
      {
        exact: "true",
        path: "/contacts",
        element: lazy(() => import("./views/contact/ListContact"))
      },
      {
        exact: "true",
        path: "/contacts/create",
        element: lazy(() => import("./views/contact/CreateContact"))
      },
      {
        exact: "true",
        path: "/contacts/edit",
        element: lazy(() => import("./views/contact/EditContact"))
      },
      {
        exact: "true",
        path: "/entities",
        element: lazy(() => import("./views/entity/ListEntity"))
      },
      {
        exact: "true",
        path: "/entities/create",
        element: lazy(() => import("./views/entity/CreateEntity"))
      },
      {
        exact: "true",
        path: "/entities/edit",
        element: lazy(() => import("./views/entity/EditEntity"))
      },
      {
        exact: "true",
        path: "/networks",
        element: lazy(() => import("./views/network/ListNetwork"))
      },
      {
        exact: "true",
        path: "/networks/create",
        element: lazy(() => import("./views/network/CreateNetwork"))
      },
      {
        exact: "true",
        path: "/networks/edit",
        element: lazy(() => import("./views/network/EditNetwork"))
      },
      {
        exact: "true",
        path: "/priorities",
        element: lazy(() => import("./views/priority/ListPriority"))
      },
      {
        exact: "true",
        path: "/priorities/create",
        element: lazy(() => import("./views/priority/CreatePriority"))
      },
      {
        exact: "true",
        path: "/priorities/edit",
        element: lazy(() => import("./views/priority/EditPriority"))
      },
      {
        exact: "true",
        path: "/users",
        element: lazy(() => import("./views/user/ListUser"))
      },
      {
        exact: "true",
        path: "/users/create",
        element: lazy(() => import("./views/user/CreateUser"))
      },
      {
        exact: "true",
        path: "/users/edit",
        element: lazy(() => import("./views/user/EditUser"))
      },
      {
        exact: "true",
        path: "/states",
        element: lazy(() => import("./views/state/ListState"))
      },
      {
        exact: "true",
        path: "/states/create",
        element: lazy(() => import("./views/state/CreateState"))
      },
      {
        exact: "true",
        path: "/states/edit",
        element: lazy(() => import("./views/state/EditState"))
      },
      {
        exact: "true",
        path: "/events",
        element: lazy(() => import("./views/event/ListEvent"))
      },
      {
        exact: "true",
        path: "/events/create",
        element: lazy(() => import("./views/event/CreateEvent"))
      },
      {
        exact: "true",
        path: "/events/edit",
        element: lazy(() => import("./views/event/EditEvent"))
      },
      {
        exact: "true",
        path: "/events/view",
        element: lazy(() => import("./views/event/ReadEvent"))
      },
      {
        exact: "true",
        path: "/playbooks",
        element: lazy(() => import("./views/playbook/ListPlaybook"))
      },
      {
        exact: "true",
        path: "/playbooks/create",
        element: lazy(() => import("./views/playbook/CreatePlaybook"))
      },
      {
        exact: "true",
        path: "/playbooks/edit",
        element: lazy(() => import("./views/playbook/EditPlaybook"))
      },
      {
        exact: "true",
        path: "/cases",
        element: lazy(() => import("./views/case/ListCase"))
      },
      {
        exact: "true",
        path: "/cases/create",
        element: lazy(() => import("./views/case/CreateCase"))
      },
      {
        exact: "true",
        path: "/cases/edit",
        element: lazy(() => import("./views/case/EditCase"))
      },
      {
        exact: "true",
        path: "/cases/view",
        element: lazy(() => import("./views/case/ReadCase"))
      },
      {
        exact: "true",
        path: "/templates",
        element: lazy(() => import("./views/template/ListTemplate"))
      },
      {
        exact: "true",
        path: "/templates/create",
        element: lazy(() => import("./views/template/CreateTemplate"))
      },
      {
        exact: "true",
        path: "/templates/edit",
        element: lazy(() => import("./views/template/EditTemplate"))
      },
      {
        exact: "true",
        path: "/reports",
        element: lazy(() => import("./views/report/ListReport"))
      },
      {
        exact: "true",
        path: "/reports/edit",
        element: lazy(() => import("./views/report/EditReport"))
      },
      {
        exact: "true",
        path: "/reports/create",
        element: lazy(() => import("./views/report/CreateReport"))
      },
      {
        exact: "true",
        path: "/setting",
        element: lazy(() => import("./views/setting/EditSetting"))
      },
      {
        exact: "true",
        path: "/profile",
        element: lazy(() => import("./views/profile/Profile"))
      },
      {
        path: "*",
        exact: "true",
        element: () => <Navigate to={BASE_URL} />
      }
    ]
  }
];

export default routes;
