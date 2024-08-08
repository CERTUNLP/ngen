import React from 'react';
import { Form } from 'react-bootstrap';
import Select from 'react-select';

const SelectLabel = ({set, setSelect, options, value, placeholder, required, disabled, legend}) => {
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
                placeholder={`Select ${placeholder}`}
                onChange={handleChange}
                {...(disabled ? {isDisabled: true} : {})}
            />
            {legend ? <Form.Text className="text-muted">{legend}</Form.Text> : ""}
        </Form.Group>
    );
};

export default SelectLabel;
