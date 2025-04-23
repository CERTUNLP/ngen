import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";


const getAnalyzerMappings = () => {
    return apiInstance
      .get(COMPONENT_URL.analyzerMapping)
      .then((response) => {
        return response.data;
      })
      .catch((error) => {
        return Promise.reject(error);
      });
  };

  
export { getAnalyzerMappings };