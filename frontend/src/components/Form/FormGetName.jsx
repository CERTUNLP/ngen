import React, { useEffect, useState } from "react";
import { Form } from "react-bootstrap";

const FormGetName = (props) => {
  // url, get, key, Form: true o false, getFromList: if endpoint returns a list
  const [item, setItem] = useState("");
  const field = props.field || "name";

  useEffect(() => {
    if (props.getFromList) {
      showFromList(props.get ,props.url)
    } else {
      showName(props.url);
    }
  }, []);

  const showName = (url) => {
    props
      .get(url)
      .then((response) => {
        setItem(response.data);
      });
  };

  const showFromList = (method, url) => {
    method()
      .then((response) => {
        setItem(response.find((item) => item.url === url));
      });
  }

  return (
    item && (
      <React.Fragment>
        {props.form ? <Form.Control plaintext readOnly defaultValue={item[field] || ""} key={props.url} /> : <>{item.name}</>}
      </React.Fragment>
    )
  );
};

export default FormGetName;
