import React, { useEffect, useState } from 'react';
import { Dropdown } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

function DropdownState({ state, setActive, str_true = 'w.active', str_false = 'w.inactive' }) {
  const { t } = useTranslation();

  const options = {
    true: str_true,
    false: str_false
  };

  const options2 = {};
  for (const key in options) {
    options2[options[key]] = key;
  }

  const [selected, setSelected] = useState();

  useEffect(() => {
    setSelected(t(options[state]));
  }, [state]);

  const setValue = (value) => {
    setSelected(t(value));
    setActive(options2[value]);
  };

  return (
    <Dropdown>
      <Dropdown.Toggle
        variant="secondary"
        className="btn-block"
        style={{
          textOverflow: 'ellipsis',
          overflow: 'hidden' // force to avoid overflow and colision with other elements
        }}
      >
        {selected}
      </Dropdown.Toggle>
      <Dropdown.Menu>
        {Object.entries(options).map(([key, value]) => (
          <Dropdown.Item eventKey={key} key={key} onSelect={() => setValue(value)} active={selected === value}>
            {t(value)}
          </Dropdown.Item>
        ))}
      </Dropdown.Menu>
    </Dropdown>
  );
}

export default DropdownState;
