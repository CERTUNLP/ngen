import apiInstance from '../api';

const getGroup = (url) => {
  return apiInstance.get(url);
};

export { getGroup };
