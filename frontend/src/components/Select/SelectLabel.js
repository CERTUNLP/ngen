import React from 'react';
import { Form } from 'react-bootstrap';
import Select from 'react-select';

const SelectLabel = ({set, setSelect, options, value, placeholder, required}) => {
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
            <Form.Label>{placeholder} {required ? <b style={{color:"red"}}>*</b> : ""}</Form.Label>
            <Select
                options={options}
                value={value}
                isClearable
                placeholder={`Seleccione ${placeholder}`}
                onChange={handleChange}
            />
        </Form.Group>
    );
};

export default SelectLabel;
