import React, { useEffect, useState } from "react";
import { Form } from "react-bootstrap";

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat/DateTimeFormat#date-time_component_options

const DateShowField = ({ value, year = true, time = true, seconds = false, asFormControl }) => {
  const [date, setDate] = useState(null);
  const [title, setTitle] = useState(null);
  const date_options = localStorage.getItem("date_options");
  const browserTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  let options = date_options
    ? JSON.parse(date_options)
    : {
        year: year ? "numeric" : undefined,
        month: "numeric",
        day: "numeric",
        hour: time ? "numeric" : undefined,
        minute: time ? "numeric" : undefined,
        second: time ? (seconds ? "numeric" : undefined) : undefined,
        locale: "en-CA",
        separator: " "
        // hourCycle: "h24",
        // timeZone: "",
        // timeZoneName: "short"
      };

  if (!options["timeZone"]) {
    options.timeZone = browserTimeZone;
  }

  const optionsFull = {
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    second: "numeric",
    locale: "en-CA",
    separator: " ",
    hourCycle: "h24",
    timeZone: "UTC",
    timeZoneName: "short"
  };

  const optionsFullLocal = {
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    second: "numeric",
    locale: "en-CA",
    separator: " ",
    hourCycle: "h24",
    timeZone: browserTimeZone,
    timeZoneName: "short"
  };

  useEffect(() => {
    let d = new Date(value);
    setDate(d.toLocaleDateString(options["locale"], options));
    setTitle(`${d.toLocaleDateString(optionsFullLocal["locale"], optionsFullLocal)}\n${d.toLocaleDateString(optionsFull["locale"], optionsFull)}`);
  }, [value, options]);

  if (asFormControl) {
    return (
      <Form.Control
        plaintext
        readOnly
        defaultValue={date}
        title={title}
      />
    );
  } else {
    return (
      <React.Fragment>
        <div title={title}>{date}</div>
      </React.Fragment>
    );
  }
};

export default DateShowField;
