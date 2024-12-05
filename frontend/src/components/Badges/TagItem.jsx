import React from "react";
import { Badge } from "react-bootstrap";

const TagItem = ({ tag, itemkey }) => {
  const x = tag || tag.value || tag;
  const tagKey = x.replace(/[^a-zA-Z0-9]/g, "-");
  console.log("tag", tag);
  return (
    <React.Fragment>
      <style type="text/css">
        {`
        .custom-${tagKey} {
          color: #333 !important;
          background-color: ${tag.color} !important;
        }
        `}
      </style>
      <Badge
        className={"custom-badge mr-1" + " custom-" + tagKey}
        ref={(element) => {
          if (element) {
            // Verificar si algún elemento padre tiene la clase 'row-false-positive'
            const hasFalsePositiveParent = element.closest(".row-false-positive");
            if (!hasFalsePositiveParent) {
              console.log("element", element);
              // Eliminar color y background de todos los hijos
              element.querySelectorAll("*").forEach((child) => {
                child.style.removeProperty("color");
                child.style.removeProperty("background-color");
              });
              // Aplicar los estilos personalizados al Badge
              element.style.setProperty("color", "#333", "important");
              element.style.setProperty("background-color", x, "important");
            } else {
              element.classList.add("custom-badge-gray");
            }
          }
        }}
      >
        {x}
      </Badge>
    </React.Fragment>
  );
};

export default TagItem;
