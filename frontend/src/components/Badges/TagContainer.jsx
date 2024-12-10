import React from "react";
import TagItem from "./TagItem";
import LetterFormat from "components/LetterFormat";
import { getMinifiedTag } from "api/services/tags";

// Bandera global para evitar múltiples solicitudes
let isFetchingTags = false;

const TagContainer = ({ tags, maxWidth = "150px", justifyContent = "center" }) => {
  const [fetchedTags, setFetchedTags] = React.useState([]);

  React.useEffect(() => {
    if (!isFetchingTags) {
      isFetchingTags = true; // Activar la bandera global
      getMinifiedTag()
        .then((response) => {
          setFetchedTags(tags.map((tag) => response.find((t) => t.name === tag)));
        })
        .catch((error) => {
          console.error("Error fetching tags:", error);
        })
        .finally(() => {
          isFetchingTags = false; // Desactivar la bandera global
        });
    }
  }, []);

  return (
    <div style={{ width: "100%", textAlign: "center" }}>
      <div
        style={{
          display: "inline-flex",
          flexWrap: "wrap",
          gap: "1px",
          maxWidth: maxWidth,
          justifyContent: justifyContent,
          alignItems: "center"
        }}
      >
        {tags?.length > 0
          ? fetchedTags?.map((tag, index) => <LetterFormat key={index} stringToDisplay={tag.name} useBadge={true} bgcolor={tag.color} />)
          : "-"}
      </div>
    </div>
  );
};

export default TagContainer;
