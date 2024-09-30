import PropTypes from "prop-types";
import React, { useEffect } from "react";
import { useSelector } from "react-redux";
import { ListGroup } from "react-bootstrap";
import PerfectScrollbar from "react-perfect-scrollbar";

import NavGroup from "./NavGroup";
import NavCard from "./NavCard";
import routes from "../../../../routes";
import { userIsNetworkAdmin } from "utils/permissions";

const NavContent = ({ navigation }) => {
  const account = useSelector((state) => state.account);
  const { isLoggedIn, user } = account;
  const [userPermissions] = React.useState(user.permissions || []);
  const [items, setItems] = React.useState([]);
  const [itemsBottom, setItemsBottom] = React.useState([]);
  
  const filterMenuItems = (items) => {
    const isNetworkAdmin = userIsNetworkAdmin();

    return items.reduce((acc, item) => {
      // Si el item tiene una URL, lo añadimos a la nueva estructura
      if (item.url) {
        let add = true;
        if (!user.is_superuser) {
          let r = routes.filter((route) => route.path === item.url);
          if (r.length > 0) {
            if (r[0].permissions?.length > 0) {
              if (!r[0].permissions.every((perm) => userPermissions.includes(perm))) {
                add = false;
              }
            }
          }
        }
        if (!isNetworkAdmin && item.id?.includes("networkadmin")) {
          add = false;
        }
        if (add) {
          acc.push({ ...item });
        }
      } else if (item.children) {
        // Si el item tiene hijos, los filtramos también
        const filteredChildren = filterMenuItems(item.children);
        if (filteredChildren.length > 0) {
          acc.push({
            ...item,
            children: filteredChildren // Solo añadimos hijos filtrados
          });
        }
      }
      return acc;
    }, []);
  };

  useEffect(() => {
    setItems(filterMenuItems(navigation.items));
    setItemsBottom(filterMenuItems(navigation.itemsBottom));
  }, [userPermissions]);

  let navItems = items.map((item) => {
    switch (item.type) {
      case "group":
        return <NavGroup key={"nav-group-" + item.id} group={item} />;
      default:
        return false;
    }
  });

  const navItemsBottom = itemsBottom.map((item) => {
    switch (item.type) {
      case "group":
        return <NavGroup layout="vertical" key={"nav-group-" + item.id} group={item} />;
      default:
        return false;
    }
  });

  let mainContent = "";

  mainContent = (
    <div className="navbar-content datta-scroll">
      <PerfectScrollbar>
        <ListGroup variant="flush" as="ul" bsPrefix=" " className="nav pcoded-inner-navbar" id="nav-ps-next">
          {navItems}
        </ListGroup>
        <ListGroup variant="flush" as="ul" bsPrefix=" " className="nav pcoded-inner-navbar" id="nav-ps-bottom">
          {navItemsBottom}
        </ListGroup>
        <NavCard />
      </PerfectScrollbar>
    </div>
  );

  return <React.Fragment>{mainContent}</React.Fragment>;
};

// NavContent.propTypes = {
//   navigation: PropTypes.array
// };

NavContent.propTypes = {
  navigation: PropTypes.shape({
    items: PropTypes.array.isRequired,
    itemsBottom: PropTypes.array.isRequired
  }).isRequired
};

export default NavContent;
