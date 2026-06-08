import React from "react";

const Ordering = ({ field, label, order, setOrder, setLoading, letterSize = "" }) => {
  const isActive = order === field || order === `-${field}`;

  const getIcon = (field) =>
    isActive
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
        className={`${getIcon(field)} sort-icon${isActive ? " sort-icon-active" : ""}`}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); orderBy(field_order); } }}
        onClick={() => orderBy(field_order)}
      ></span>
    </th>
  );
};

export default Ordering;
