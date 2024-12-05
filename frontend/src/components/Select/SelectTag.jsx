import React from "react";
import Select from "react-select";
import makeAnimated from "react-select/animated";
import { useTranslation } from "react-i18next";
import { getTextColorBasedOnBackground } from "utils/colors";

const animatedComponents = makeAnimated();

const SelectTag = ({ value, onChange, options }) => {
    const { t } = useTranslation();
    
  const customStyles = {
    option: (style, state) => ({
      ...style,
      // backgroundColor: state.data.color,
      // color: getTextColorBasedOnBackground(state.data.color),
      // padding: 10,
      color: state.data.color,
      cursor: "pointer"
    }),
    singleValue: (style, state) => ({
      ...style,
      backgroundColor: state.data.color,
      color: getTextColorBasedOnBackground(state.data.color),
    }),
    multiValue: (style, state) => ({
      ...style,
      backgroundColor: state.data.color,
      color: getTextColorBasedOnBackground(state.data.color),
      borderRadius: 5,
    }),
    multiValueLabel: (style, state) => ({
      ...style,
      color: getTextColorBasedOnBackground(state.data.color),
    }),
    multiValueRemove: (style, state) => ({
      ...style,
      color: getTextColorBasedOnBackground(state.data.color),
      ':hover': {
        backgroundColor: '#f0f0f0',
        color: 'black',
      },
    }),

  };


  return (
    <Select 
      placeholder={t("ngen.tag_other")}
      closeMenuOnSelect={false}
      components={animatedComponents}
      styles={customStyles}
      isMulti
      value={value}
      onChange={onChange}
      options={options}
    />
  );
};

export default SelectTag;
