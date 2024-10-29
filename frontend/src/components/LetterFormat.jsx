import React from "react";
import { Badge } from "react-bootstrap";

const LetterFormat = ({ useBadge, stringToDisplay, color }) => {
  // let styleColor = "";
  // if (stringToDisplay.lower() === "amber") {
  //   styleColor = "tlp-amber";
  // } else if (stringToDisplay.lower() === "red") {
  //   styleColor = "tlp-red";
  // } else if (stringToDisplay.lower() === "green") {
  //   styleColor = "tlp-green";
  // } else if (stringToDisplay.lower() === "clear") {

  
  return useBadge ? (
    <Badge
      className={"custom-badge mr-1"}
      ref={(element) => {
        if (element) {
          // Verificar si algún elemento padre tiene la clase 'row-false-positive'
          const hasFalsePositiveParent = element.closest(".row-false-positive");
          if (!hasFalsePositiveParent) {
            console.log("element", element);
            // Aplicar los estilos personalizados al Badge
            element.style.setProperty("color", color, "important");
            element.style.setProperty("background-color", "#000", "important");
          } else {
            // Eliminar color y background de todos los hijos
            element.querySelectorAll("*").forEach((child) => {
              child.style.removeProperty("color");
              child.style.removeProperty("background-color");
            });
            element.classList.add("custom-badge-gray");
          }
        }
      }}
    >
      {stringToDisplay}
    </Badge>
  ) : (
    <div>{stringToDisplay}</div>
  );
};

export default LetterFormat;
