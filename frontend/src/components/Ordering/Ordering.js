import React from 'react'

const Ordering = ({ field, label, order, setOrder, setLoading, letterSize = "" }) => {

  const getIconColor = (field) => (order === field || order === `-${field}`) ? 'red' : 'black';

  const orderBy = (ordering) => {
    setOrder(ordering);
    if (order !== ordering) {
      setLoading(true);
    }
  };

  return (
    <th style={letterSize}>
      {label}
      <span
        className="material-icons"
        style={{
          marginLeft: '8px',
          color: getIconColor(field),
          cursor: 'pointer',
          fontSize: 'inherit',
          verticalAlign: 'middle',
        }}
        onClick={() => orderBy(order === field ? `-${field}` : field)}
      >
                unfold_more
            </span>
    </th>
  )
}

export default Ordering
