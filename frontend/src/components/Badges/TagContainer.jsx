import React from "react";
import { useQuery } from "@tanstack/react-query";
import { getMinifiedTag } from "api/services/tags";
import LetterFormat from "components/LetterFormat";

const TagContainer = ({
  tags, // e.g. ['urgent', 'important']
  maxWidth = "150px",
  justifyContent = "center",
  component: TagComponent = LetterFormat,
}) => {
  const { data: allTags = [], isLoading, error } = useQuery({
    queryKey: ["minified-tags"],
    queryFn: getMinifiedTag,
    staleTime: 5 * 60 * 1000, // optional: 5 minutes
  });

  const tagsToDisplay = React.useMemo(() => {
    if (!tags?.length || !allTags?.length) return [];
    return tags
      .map((tagName) => allTags.find((t) => t?.name === tagName))
      .filter(Boolean);
  }, [tags, allTags]);

  if (isLoading) {
    return <div style={{ textAlign: "center" }}>Loading tags...</div>;
  }

  if (error) {
    console.error("Error loading tags:", error);
    return <div style={{ textAlign: "center" }}>Failed to load tags.</div>;
  }

  return (
    <div style={{ width: "100%", textAlign: "center" }}>
      <div
        style={{
          display: "inline-flex",
          flexWrap: "wrap",
          gap: "1px",
          maxWidth: maxWidth,
          justifyContent: justifyContent,
          alignItems: "center",
        }}
      >
        {tagsToDisplay.length > 0 ? (
          tagsToDisplay.map((tag, index) => (
            <TagComponent
              key={index}
              stringToDisplay={tag.name}
              bgcolor={tag.color}
              useBadge={true}
              tag={tag} // optional if component needs full tag
            />
          ))
        ) : (
          "-"
        )}
      </div>
    </div>
  );
};

export default TagContainer;
