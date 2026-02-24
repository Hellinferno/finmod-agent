import axios from 'axios';

// The URL to the local FastAPI server
export const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    timeout: 30000, // 30 seconds for LLM generations
});

apiClient.interceptors.response.use(
    (response) => response.data,
    (error) => {
        const apiMessage =
            error.response?.data?.message ||
            error.response?.data?.detail ||
            error.message;
        console.error("API Error: ", apiMessage);
        return Promise.reject(error);
    }
);
