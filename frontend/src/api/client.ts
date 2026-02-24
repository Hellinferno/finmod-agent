import axios from 'axios';

// The URL to the local FastAPI server
export const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    timeout: 30000, // 30 seconds for LLM generations
});

apiClient.interceptors.response.use(
    (response) => response.data,
    (error) => {
        console.error("API Error: ", error.response?.data?.message || error.message);
        return Promise.reject(error);
    }
);
