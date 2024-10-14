import React from "react";
import { Form } from "react-bootstrap";
import Select from "react-select";
import { useTranslation } from "react-i18next";

const SelectLabel = ({ set, setSelect, options, value, placeholder, required, disabled, legend }) => {
  const { t } = useTranslation();
  const handleChange = (e) => {
    if (e) {
      set(e.value);
    } else {
      set("");
    }
    setSelect(e);
  };

  return (
    <Form.Group controlId={`Form.${placeholder}`}>
      <Form.Label>
        {placeholder} {required ? <b style={{ color: "red" }}>*</b> : ""}
      </Form.Label>
      <Select
        options={options}
        value={value}
        isClearable
        placeholder={`${t("w.select")} ${placeholder}`}
        onChange={handleChange}
        {...(disabled ? { isDisabled: true } : {})}
      />
      {legend ? <Form.Text className="text-muted">{legend}</Form.Text> : ""}
    </Form.Group>
  );
};

export default SelectLabel;
