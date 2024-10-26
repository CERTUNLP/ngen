import React, { useEffect, useState } from "react";
import { getEvent } from "../../../api/services/events";

const ListDomain = ({ events }) => {
  const [eventDomains, setEventDomains] = useState([]);

  useEffect(() => {
    async function fetchAndSetEvents(events) {
      try {
        if (Array.isArray(events) && events.length > 0) {
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
        }
      } catch (error) {
        console.error("Error fetching events:", error);
      }
    }

    // Llamada a la función
    fetchAndSetEvents(events);
  }, [events]);

  if (eventDomains.length === 0) {
    return <div>-</div>;
  }

  return (
    <div>
      <ul style={{ padding: 0 }}>
        {eventDomains.map((domain, index) => (
          <li key={index} style={{ listStyleType: "none" }}>{domain}</li>
        ))}
      </ul>
    </div >
  );
};

export default ListDomain;
