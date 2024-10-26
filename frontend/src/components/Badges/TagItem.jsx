import React from "react";
import { Badge } from "react-bootstrap";

const TagItem = ({ tag, itemkey }) => {
  const x = tag.name || tag.value || tag;
  return (
    <Badge
      key={itemkey}
      className="badge mr-1"
      ref={(element) => {
        if (element) {
          element.style.setProperty("color", "#333", "important");
          element.style.setProperty("background", tag.color || "#ccc", "important");
        }
      }}
    >
      {x}
    </Badge>
  );
};

export default TagItem;
