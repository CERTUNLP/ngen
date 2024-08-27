import React from "react";

const Ordering = ({ field, label, order, setOrder, setLoading, letterSize = "" }) => {
  const getIconColor = (field) => (order === field || order === `-${field}` ? "red" : "black");

  const getIcon = (field) =>
    order === field || order === `-${field}`
      ? order.startsWith("-")
        ? "fa fa-sort-alpha-up"
        : "fa fa-sort-alpha-down"
      : "fa fa-sort-alpha-down";

  const orderBy = (ordering) => {
    setOrder(ordering);
    if (order !== ordering) {
      setLoading(true);
    }
  };

  let field_order = order === field ? `-${field}` : field;

  return (
    <th style={letterSize}>
      {label}
      <span
        className={getIcon(field)}
        style={{
          marginLeft: "8px",
          color: getIconColor(field),
          cursor: "pointer",
          fontSize: "inherit",
          verticalAlign: "middle"
        }}
        onClick={() => orderBy(field_order)}
      ></span>
    </th>
  );
};

export default Ordering;
