import React from "react";
import TagItem from "./TagItem";
import LetterFormat from "components/LetterFormat";
import { getMinifiedTag } from "api/services/tags";

const TagContainer = ({ tags, maxWidth = "150px", justifyContent = "center" }) => {
  const [fetchedTags, setFetchedTags] = React.useState([]);
  const [tagsToDisplay, setTagsToDisplay] = React.useState([]);

  React.useEffect(() => {
    getMinifiedTag()
      .then((response) => {
        setFetchedTags(response);
      })
      .catch((error) => {
        console.error("Error fetching tags:", error);
      });
  }, []);

  React.useEffect(() => {
    if (fetchedTags?.length > 0) {
      setTagsToDisplay(tags?.map((tag) => fetchedTags?.find((ft) => ft?.name === tag)));
    }
  } , [fetchedTags, tags]);

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
        {tagsToDisplay?.length > 0
          ? tagsToDisplay?.map((tag, index) => (
              <LetterFormat
                key={index}
                stringToDisplay={tag.name}
                useBadge={true}
                bgcolor={tag.color}
              />
            ))
          : "-"}
      </div>
    </div>
  );
};

export default TagContainer;
