import React, { useEffect, useState } from "react";
import { Dropdown } from "react-bootstrap";
import { useTranslation } from "react-i18next";

function DropdownState({ state, setActive, str_true = "w.active", str_false = "w.inactive" }) {
  const { t } = useTranslation();

  const options = {
    true: str_true,
    false: str_false
  };

  const [selected, setSelected] = useState(state);

  useEffect(() => {
    setSelected(selected);
  }, [state]);

  const setValue = (key) => {
    setSelected(key);
    setActive(key);
  };

  return (
    <Dropdown onSelect={(key) => setValue(key)} >
      <Dropdown.Toggle
        variant="secondary"
        className="btn-block"
        style={{
          textOverflow: "ellipsis",
          overflow: "hidden" // force to avoid overflow and colision with other elements
        }}
      >
        {t(options[selected])}
      </Dropdown.Toggle>
      <Dropdown.Menu>
        {Object.entries(options).map(([key, value]) => (
          <Dropdown.Item eventKey={key} key={key} active={key === selected}>
            {t(value)}
          </Dropdown.Item>
        ))}
      </Dropdown.Menu>
    </Dropdown>
  );
}

export default DropdownState;
