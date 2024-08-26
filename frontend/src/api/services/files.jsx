import apiInstance from '../api'

const getFiles = (url) => {
  return apiInstance.get(url)
}

export { getFiles }
