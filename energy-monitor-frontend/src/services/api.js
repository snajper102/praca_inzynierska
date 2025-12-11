import axios from 'axios';

// Ustaw bazowy URL swojego API Django
const API_URL = 'http://127.0.0.1:8000/api'; 

const apiClient = axios.create({
  baseURL: API_URL,
});

// Interceptor, który dodaje token do KAŻDEGO zapytania
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      // Używamy formatu Token, którego oczekuje DRF
      config.headers['Authorization'] = `Token ${token}`; 
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;
