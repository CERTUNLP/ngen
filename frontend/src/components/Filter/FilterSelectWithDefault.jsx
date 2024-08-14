import React from 'react'
import { Form } from 'react-bootstrap'
import Select from 'react-select'

const FilterSelectWithDefault = ({
  options,
  partOfTheUrl,
  setFilter,
  currentFilter,
  value,
  setValue,
  setLoading,
  placeholder,
}) => {
  const applyFilter = (e) => {
    const filterValue = e?.value
    const newFilter = `${partOfTheUrl}=${filterValue || ''}&` //Aquí, se utiliza el operador de fusión nula (||) para proporcionar un valor predeterminado de cadena vacía ('') en caso de que filterValue sea nulo o indefinido. Esto es útil para evitar que la cadena resultante sea "undefined" si filterValue no tiene un valor.

    if (newFilter !== currentFilter) {
      setFilter(newFilter)
      setLoading(true)
    }

    setValue(e)
  }

  return (
    <Form.Group>
      <Select options={options} isClearable placeholder={placeholder}
              onChange={applyFilter} value={value}/>
    </Form.Group>
  )
}

export default FilterSelectWithDefault
