export interface Task {
  id: string;
  filename: string;
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  createdAt: string;
  userId: string;
  results?: string;
}

export interface TaskResponse {
  task_id: string;
  filename: string;
}
