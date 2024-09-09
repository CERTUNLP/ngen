import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import store from "../../store";

const Alert = ({ component }) => {
  const [textMessage, setTextMessage] = useState("");
  const [typeAlert, setTypeAlert] = useState("");
  const [typeComponent, setTypeComponent] = useState("");

  useEffect(() => {
    // Función para manejar actualizaciones del store
    const handleStoreChange = () => {
      const state = store.getState();
      const message = state.message.text;
      const alertType = state.message.typeMessage;
      const componentType = state.message.typeComponent;

      setTextMessage(message);
      setTypeAlert(alertType);
      setTypeComponent(componentType);

      // Verifica si el mensaje es para este componente y muestra el toast
      if (message !== "" && componentType === component) {
        showToast(alertType, message);
      }
    };

    // Función para mostrar el toast según el tipo de alerta
    const showToast = (alertType, message) => {
      if (alertType === "success") {
        toast.success(message);
      } else {
        toast.error(message);
      }
      // Limpiar el mensaje en el store
      store.dispatch({ type: "CLEAR_MESSAGE" });
    };

    // Mostrar el mensaje inicial si ya existe uno al montar el componente
    handleStoreChange();

    // Suscribirse al store para escuchar cambios
    const unsubscribe = store.subscribe(handleStoreChange);

    // Cleanup de la suscripción al desmontar el componente
    return () => unsubscribe();
  }, [component]);

  return null; // No necesitas renderizar nada en este componente
};

export default Alert;
