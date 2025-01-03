import api from "./api";
import { API_ENDPOINTS } from "../utils/constants";
import { Task, TaskResponse } from "../types/task.types";

export const taskService = {
  async uploadFile(file: File): Promise<TaskResponse> {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await api.post(API_ENDPOINTS.UPLOAD, formData);
    return data;
  },

  async getTasks(): Promise<Task[]> {
    const { data } = await api.get(API_ENDPOINTS.TASKS);
    return data;
  },

  async getTask(taskId: string): Promise<Task> {
    const { data } = await api.get(`${API_ENDPOINTS.TASKS}/${taskId}`);
    return data;
  },
};
