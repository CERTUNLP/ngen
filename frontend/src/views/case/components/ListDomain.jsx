import React, { useEffect, useState } from "react";
import { getEvent } from "../../../api/services/events";

const ListDomain = ({ events }) => {
  const [eventDomains, setEventDomains] = useState([]);

  useEffect(() => {
    async function fetchAndSetEvents(events) {
      try {
        if (!Array.isArray(events) || events.length === 0) {
          console.error("events is either undefined or not an array");
          return; // Salir si events no es un array válido
        }

        const responses = await Promise.all(
          events.map((event) =>
            getEvent(event).then((response) => {
              return response.data;
            })
          )
        );

        const ListDomain = responses.map((response) =>
          response.address_value ? response.address_value : ""
        );
        setEventDomains(ListDomain);
      } catch (error) {
        console.error("Error fetching events:", error);
      }
    }

    // Llamada a la función
    fetchAndSetEvents(events);
  }, [events]);

  return (
    <div>
      <ul>
        {eventDomains.map((domain, index) => (
          <li key={index}>{domain}</li>
        ))}
      </ul>
    </div>
  );
};

export default ListDomain;
