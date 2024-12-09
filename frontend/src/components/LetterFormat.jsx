import React from "react";
import { Badge } from "react-bootstrap";
import { getTextColorBasedOnBackground } from "utils/colors";

const LetterFormat = ({ useBadge, stringToDisplay, color, bgcolor }) => {
  // let styleColor = "";
  // if (stringToDisplay.lower() === "amber") {
  //   styleColor = "tlp-amber";
  // } else if (stringToDisplay.lower() === "red") {
  //   styleColor = "tlp-red";
  // } else if (stringToDisplay.lower() === "green") {
  //   styleColor = "tlp-green";
  // } else if (stringToDisplay.lower() === "clear") {

  let bgColorToDisplay = bgcolor ? bgcolor : "#CCC";
  let colorToDisplay = color ? color : getTextColorBasedOnBackground(bgColorToDisplay);

  
  return useBadge ? (
    <Badge
      className={"custom-badge mr-1"}
      ref={(element) => {
        if (element) {
          // Verificar si algún elemento padre tiene la clase 'row-false-positive'
          const hasFalsePositiveParent = element.closest(".row-false-positive");
          if (!hasFalsePositiveParent) {
            // Aplicar los estilos personalizados al Badge
            element.style.setProperty("color", colorToDisplay, "important");
            element.style.setProperty("background-color", bgColorToDisplay, "important");
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
