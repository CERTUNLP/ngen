import React from 'react'
import { Button } from 'react-bootstrap'

const ButtonFilter = ({ open, setOpen }) => {

  return (
    <Button variant="primary" className="text-capitalize" size="md"
            onClick={() => setOpen(!open)} aria-expanded={open}>
      <span className="feather icon-filter">
      </span>
    </Button>

  )
}

export default ButtonFilter
