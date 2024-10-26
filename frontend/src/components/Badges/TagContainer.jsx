import React from "react";
import TagItem from "./TagItem";

const TagContainer = ({ tags, maxWidth="150px", justifyContent="center" }) => {
    return (
      <div style={{ width: "100%", textAlign: "center" }}>
    <div style={{ display: "inline-flex", flexWrap: "wrap", gap: "1px", maxWidth: maxWidth, justifyContent: justifyContent, alignItems: "center" }}>
      {tags.length > 0 ? tags.map((tag, index) => <TagItem tag={tag} itemkey={index} />) : "-"}
            </div>
        </div>
  );
};

export default TagContainer;
