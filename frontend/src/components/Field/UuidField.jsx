import React, { useEffect, useState, useRef } from "react";
import { Button, OverlayTrigger, Tooltip, Overlay } from "react-bootstrap";
import { useTranslation } from "react-i18next";

const UuidField = ({ value, fulltext = false }) => {
  const { t } = useTranslation();

  const [v, setV] = useState(null);
  const [showTooltip, setShowTooltip] = useState(false);
  const target = useRef(null);

  useEffect(() => {
    setV(value);
  }, [value]);

  const handleCopy = () => {
    navigator.clipboard.writeText(v).then(() => {
      setShowTooltip(true);
      setTimeout(() => setShowTooltip(false), 2000); // Hide tooltip after 2 seconds
    });
  };

  let component = "";

  if (fulltext) {
    component = <span>{v}</span>;
  } else {
    component = (
      <OverlayTrigger placement="top" overlay={<Tooltip id="uuid-tooltip">{v}</Tooltip>}>
        <span
          style={{
            position: "relative",
            display: "inline-block",
            maxWidth: "75px", // Limit the width of the text
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            verticalAlign: "middle",
            cursor: "pointer" // Show pointer on hover
          }}
        >
          {v}
        </span>
      </OverlayTrigger>
    );
  }

  return (
    <div>
      {component}
      <Button
        ref={target}
        variant="outline-link"
        onClick={handleCopy}
        style={{
          fontSize: "1rem",
          padding: "0.5rem 0.5rem",
          lineHeight: "1",
          minWidth: "auto"
        }}
      >
        <i className="fa fa-copy" />
      </Button>
      <Overlay target={target.current} show={showTooltip} placement="top">
        {(props) => (
          <Tooltip id="copied-tooltip" {...props}>
            Copied!
          </Tooltip>
        )}
      </Overlay>
    </div>
  );
};

export default UuidField;
