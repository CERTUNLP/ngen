import React from "react";
import Select from "react-select";
import makeAnimated from "react-select/animated";
import { useTranslation } from "react-i18next";
import { getTextColorBasedOnBackground } from "utils/colors";

const animatedComponents = makeAnimated();

const SelectTag = ({ value, onChange, options }) => {
  const { t } = useTranslation();

  return (
    <Select
      placeholder={t("ngen.artifact_other_select")}
      closeMenuOnSelect={false}
      components={animatedComponents}
      isMulti
      value={value}
      onChange={onChange}
      options={options}
    />
  );
};

export default SelectTag;
