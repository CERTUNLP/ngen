import React, { useState, useEffect } from 'react';
import { Dropdown } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';


function DropdownState({ state, setActive }) {
  const { t } = useTranslation();

  const options = {
    true: "w.active",
    false: "w.inactive"
  };
  const options2 = {
    "w.active": true,
    "w.inactive": false
  };

  const [selected, setSelected] = useState();

  useEffect(() => {
    setSelected(t(options[state]))
  }, [state]);

  const setValue = (value) => {
    setSelected(value)
    setActive(options2[value])
  }


  return (
    <Dropdown>
      <Dropdown.Toggle variant="secondary">
        {selected}
      </Dropdown.Toggle>
      <Dropdown.Menu>
        {Object.entries(options).map(([key, value]) => (
          <Dropdown.Item eventKey={key} key={key} onSelect={() => setValue(value)} active={selected === value} >
            {t(value)}
          </Dropdown.Item>)
        )
        }
      </Dropdown.Menu>
    </Dropdown>
  )
}

export default DropdownState;

