import React from "react";
import { toast } from "react-toastify";
import store from "../../store";

const Alert = ({ showAlert, resetShowAlert, component }) => {
  const textMessage = store.getState().message.text;
  const typeAlert = store.getState().message.typeMessage;
  const typeComponent = store.getState().message.typeComponent;

  React.useEffect(() => {
    if (showAlert === true && textMessage !== "" && typeComponent === component) {
      if (typeAlert === "success") {
        toast.success(textMessage);
      } else {
        toast.error(textMessage);
      }
      resetShowAlert();
      store.dispatch({ type: "CLEAR_MESSAGE" });
    }
  }, [showAlert, textMessage, typeAlert, typeComponent, component, resetShowAlert]);

  return null; // No necesitas renderizar nada en este componente
};

export default Alert;
