import React, { useState } from "react";
import { Form } from "react-bootstrap";

const FilterInput = ({ partOfTheUrl, setFilter, currentFilter, setLoading, placeholder, validate, invalid_msg, label }) => {
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState("");
  const functionToValidate = validate || (() => true);

  const applyFilter = () => {
    console.log("applyFilter: ", inputValue);
    if (!functionToValidate(inputValue)) {
      setError(invalid_msg || "Invalid input");
      return;
    }
    setError(""); // Clear error if validation is successful

    const newFilter = `${partOfTheUrl}=${inputValue || ""}&`;

    if (newFilter !== currentFilter) {
      setFilter(newFilter);
      setLoading(true);
    }
  };

  return (
    <Form.Group>
      <Form.Label>{label}</Form.Label>
      <Form.Control
        type="text"
        value={inputValue}
        placeholder={placeholder}
        onChange={(e) => setInputValue(e.target.value)}
        onBlur={applyFilter}
        onKeyUp={applyFilter}
      />
      {error && <div style={{ color: "red" }}>{error}</div>}
    </Form.Group>
  );
};

export default FilterInput;
